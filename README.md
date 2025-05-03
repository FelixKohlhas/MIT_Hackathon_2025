# 525 – Automated Disaster Information Gathering System

<div align="center">
  <img width="40%" alt="Screenshot 2025-05-03 at 14 36 22" src="https://github.com/user-attachments/assets/7ca76ff1-aab8-4e74-b38b-971edf54c3d4" />
  <img width="40%" alt="Screenshot 2025-05-03 at 14 36 35" src="https://github.com/user-attachments/assets/1d8b1001-5420-4f2a-80bc-dee4ae11683e" />
</div>

Due to the impact of global warming, the number and severity of extreme weather events, such as storms, floods and wildfires due to droughts, have been on the rise and will continue to rise for the foreseeable future.

To be better prepared for events such as this, we have built a prototype system named “525” (five-two-five). It is an AI-based, highly automated Disaster Assessment Platform that allows not just government officials and first responders but also members of the community to keep an overview of the situation and optimize rescue efforts.

It is designed to be a dashboard of all information available at the time, with a backend that can autonomously acquire and analyze new data in the background. In order be more resilient to events such as power outages and disruption of internet infrastructure, the system allows input and output of data as speech though phone calls. This also gives it a more human character and may provide additional emotional support to affected inhabitants.

## Vision of the project

When a disaster strikes, operators select an area that may be affected. The 525 system then automatically researches all important infrastructures in the area, collecting addresses and phone numbers. The system then automatically starts calling phone numbers and asks the recipients of the call questions about the event using a voice agent.

The response of these questions is then visualized on a map for the operators, for example the capacity and status of hospitals in the region.

In the “Tasks & Questions” the operator can define custom questions or instructions for the recipients of the call. With grouping into infrastructure categories, entities such as hospital can be asked specific questions or given specific instructions differing from those of the other entities.

525 primarily places outgoing calls but could also be adapted to accept calls under the catchy and easy to dial number “525”.


## Current state of the project
The project is currently in a prototype state. The following features are already implemented:
- **Voice agent**: A voice agent that can call people and ask them questions about the event.
- **Dashboard**: A dashboard that visualizes the responses of the recipients of the calls on a map.
- **Tasks & Questions**: A dashboard that allows operators to add specific instructions to be given or questions to be asked during the calls.
The last two are currently static demos, but the voice agent is already in a functional state.

## Voice Agent Demo

_This is the voice agent that will call residents, hospitals etc. and ask questions about the event. The transcript will then be analysed by a seperate LLM to extract the responses. This may also be achieved by letting the voice agent directly use tool calls for storing information._

### Install dependencies
```bash
pip install -r requirements.txt
```
### Run the demo
```bash
python prototype.py
```

## Dashboard Demo

_This is the map and dashboard on which the reveived data will be visualized. The map allows operators to get an overview of the situation by visualizing the responses of the recipients of the calls. The “Tasks & Questions” dashboard allows operators to add specific instructions to be given or questions to be asked during the calls._

### Install dependencies
```bash
pip install -r requirements.txt
```
### Run the demo
```bash
python -m http.server
```

## Technical

### Tools / ML models used

| Component        | Model               | Provider      |
|------------------|---------------------|---------------|
| Speech-to-text   | whisper-1           | OpenAI        |
| Text generation  | gpt-4.1-mini        | OpenAI        |
| Text-to-speech   | sonic-2             | cartesia.ai   |

To improve performance and create a fluent conversation, the LLM output gets streamed into the text to speech API while it is still being generated using websockets.

I mainly used `DeepSeek R1` for rapid prototyping. It is impressive at generating working prototypes, as long as the prompts are very clear and specific. I am using the free version and never hit any rate limits, even when generating a lot of code at once.
I barely used `GitHub Copilot` this time, because it was often faster to make the changes myself.
I mainly let the LLMs generate functions and manually integrated them with each other. This works the best, as the models still sometimes have problems completing two tasks at once.

### Data
The source of the data about the hospitals is the "TK-Klinikführer". It was converted from text to JSON using `gpt-4o-mini`.
More information can be found in map_data/README.md.

### Challenges

There are still many things to do to finish the project. The 24h time limit was a bit too short to finish everything I wanted to do, so the demos are mainly static.