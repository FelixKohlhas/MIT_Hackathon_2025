# 525 – Automated Disaster Information Gathering System

<div align="center">
  <img width="40%" alt="Screenshot 2025-05-03 at 14 36 22" src="https://github.com/user-attachments/assets/7ca76ff1-aab8-4e74-b38b-971edf54c3d4" />
  <img width="40%" alt="Screenshot 2025-05-03 at 14 36 35" src="https://github.com/user-attachments/assets/1d8b1001-5420-4f2a-80bc-dee4ae11683e" />
</div>

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
