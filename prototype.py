# Load variables from a .env file into the environment
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sounddevice as sd
import numpy as np
import webrtcvad
from openai import OpenAI
import wave
import json
import pyaudio
from openai import OpenAI
from cartesia import Cartesia
import jinja2
import os

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")

# Configuration
INPUT_SAMPLE_RATE = 16000  # Sample rate must be 16kHz for webrtcvad
CHUNK_DURATION_MS = 30  # Supported frame durations: 10, 20, 30ms
CHUNK_SIZE = int(INPUT_SAMPLE_RATE * CHUNK_DURATION_MS / 1000)
# SILENCE_THRESHOLD = 15  # Number of silent chunks to mark end of speech
SILENCE_THRESHOLD = 30  # Number of silent chunks to mark end of speech
VAD_AGGRESSIVENESS = 3  # VAD aggressiveness (0-3)

def record_audio():
    """Record audio from microphone until speech ends"""
    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    audio_buffer = []
    silent_count = 0
    started_speaking = False
    recording = True

    with sd.InputStream(samplerate=INPUT_SAMPLE_RATE, channels=1, dtype='int16', blocksize=CHUNK_SIZE) as stream:
        while recording:
            # Read audio chunk
            chunk, overflowed = stream.read(CHUNK_SIZE)
            if overflowed:
                print("Warning: Audio buffer overflow")

            # Convert to bytes and check for speech
            chunk_bytes = chunk.tobytes()
            if vad.is_speech(chunk_bytes, INPUT_SAMPLE_RATE):
                silent_count = 0
                audio_buffer.append(chunk_bytes)
                started_speaking = True
            else:
                if started_speaking:
                    silent_count += 1
                    if silent_count >= SILENCE_THRESHOLD:
                        recording = False
                    else:
                        audio_buffer.append(chunk_bytes)

    # Save recorded audio to WAV file
    with wave.open("recording.wav", 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(INPUT_SAMPLE_RATE)
        wf.writeframes(b''.join(audio_buffer))
    return "recording.wav"

def transcribe_audio(file_path):
    """Transcribe audio using OpenAI's Whisper model"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcription

def run_S2T():
    audio_file = record_audio()
    result = transcribe_audio(audio_file)
    print(result, end="", flush=True)
    return result

# Configuration
VOICE_ID = "a0e99841-438c-4a64-b679-ae501e7d6091"
OUTPUT_SAMPLE_RATE = 22050

# Initialize APIs
openai = OpenAI(api_key=OPENAI_API_KEY)
cartesia = Cartesia(api_key=CARTESIA_API_KEY)

config = {
    "model": "gpt-4.1-mini",
}

current_llm_message = []
current_tool_call = {
    "name": None,
    "arguments": [],
}

def openai_stream_generator(message):
    global messages
    global current_llm_message
    global current_tool_call

    current_llm_message = []
    current_tool_call = {
        "name": None,
        "arguments": [],
    }

    """Stream text chunks from OpenAI's API response"""
    for chunk in openai.chat.completions.create(
        model=config["model"],
        messages=messages,
        tools=config["tools"],
        stream=True,
    ):
        content = chunk.choices[0].delta.content
        if content and content != "":
            # Append content to current message
            current_llm_message.append(content)
            print(content, end="", flush=True)
            yield content
        
        try:
            tool_call = chunk.choices[0].delta.tool_calls[0]
            if tool_call.function.name:
                current_tool_call["name"] = tool_call.function.name
            if tool_call.function.arguments:
                current_tool_call["arguments"].append(tool_call.function.arguments)
        except:
            tool_call = None
        

def run_LLM_and_T2S(message):
    audio_interface = pyaudio.PyAudio()

    global current_llm_message

    try:        
        # Setup audio stream
        audio_stream = None
        ws = cartesia.tts.websocket()
        # Establish WebSocket connection to Cartesia
        context = ws.context("live-stream")
        # Stream processing pipeline
        for audio_data in context.send(
            model_id="sonic-2",
            transcript=openai_stream_generator(message),
            voice={"id": VOICE_ID},
            stream=True,
            output_format={
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": OUTPUT_SAMPLE_RATE
            },
            max_buffer_delay_ms=200  # Lower latency for real-time streaming
        ):
            # Initialize audio stream on first chunk
            if not audio_stream:
                audio_stream = audio_interface.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    rate=OUTPUT_SAMPLE_RATE,
                    output=True
                )
            # Play audio chunk
            audio_stream.write(audio_data.audio)
    finally:
        # Cleanup resources
        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
        audio_interface.terminate()
        print("\n", end="", flush=True)
        return "".join(current_llm_message)

# Load developer prompt from prompts/reception.j2
def render_template(assistant_name, institution_name):
    template_loader = jinja2.FileSystemLoader(searchpath="prompts")
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "reception.j2"
    template = template_env.get_template(template_file)
    rendered_template = template.render(
        assistant_name=assistant_name,
        institution_name=institution_name,
    )
    return rendered_template


def end_conversation(arguments):
        reason = arguments["reason"]
        if reason == 1:
            print("Ending conversation: I have gathered all the necessary information.")
        elif reason == 2:
            print("Ending conversation: The user has no further information to share.")
        elif reason == 3:
            print("Ending conversation: Other reason.")
        else:
            print("Ending conversation: Unknown reason.")

tools = [
    {
        "type": "function",
        "function": {
            "name": "end_conversation",
            "description": "Ends the conversation with the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "integer",
                        "description": "The reason for ending the conversation."
                    }
                },
                "required": ["reason"]
            }
        }
    }
]

config = {
    "model": "gpt-4.1-mini",
    "tools": tools,
}

system_prompt = "You are a helpful assistant helping to gather information about a flood."

developer_prompt = render_template(
    assistant_name = "5-2-5, the Disaster Information Gathering System for the city of Heidelberg",
    institution_name = "University Hospital Heidelberg"
)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "developer", "content": developer_prompt}
]

running = True

while running:
    print("User: ", end="", flush=True)
    user_message = run_S2T()
    messages.append({"role": "user", "content": user_message})

    print("Assistant: ", end="", flush=True)
    llm_message = run_LLM_and_T2S(user_message)
    messages.append({"role": "assistant", "content": llm_message})
    
    if current_tool_call["name"]:
        arguments = "".join(current_tool_call["arguments"])
        arguments = json.loads(arguments)
        if current_tool_call["name"] == "end_conversation":
            end_conversation(arguments)
        running = False