# 525 – Automated Disaster Information Gathering System

## Voice Agent Demo
### Install dependencies
```bash
pip install -r requirements.txt
```
### Run the demo
```bash
python prototype.py
```

## Dashboard Demo
### Install dependencies
```bash
pip install -r requirements.txt
```
### Run the demo
```bash
python -m http.server
```

### Technical

To improve performance and create a fluent conversation, the LLM output gets streamed into the text to speech API while it is still being generated.

LLM: gpt-4.1-mini (OpenAI)
TTS: sonic-2 (cartesia.ai)