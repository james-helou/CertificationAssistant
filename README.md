<div align="center">

# Certification Assistant

**Tell it about your job and your goals, and it recommends Microsoft certifications and builds you a study plan.**

<img alt="Four AI agents" src="https://img.shields.io/badge/Four-AI_agents-24292f?style=for-the-badge"> <img alt="Written in Python" src="https://img.shields.io/badge/Written_in-Python-24292f?style=for-the-badge">

</div>

<br>

Picking a certification is harder than it should be. There are dozens, they build on each other, and it's hard to tell which one fits your job. This command-line tool asks a few questions about you, then passes your answers through four AI agents in a row. Each agent does one job and hands its result to the next. The certification data lives in a local JSON file, so the agents recommend from a real catalogue instead of guessing.

## What you can do with it

- Get certification recommendations based on your role, goals, background and experience.
- See whether you meet the prerequisites, and what to learn first if you don't.
- Get a study plan broken into modules.
- Get a weekly schedule that fits the number of hours you have.

## How the agents work together

| Agent | Job |
|---|---|
| **Goal** | Reads your profile and picks the certifications that fit |
| **Prerequisite** | Checks what you already know and finds the gaps |
| **Curriculum** | Turns the chosen certification into study modules |
| **Schedule** | Spreads the modules over your available hours |

## Use it

The agents live in `simple_agents.py` and the certification catalogue is `data/certifications.json`. The agents talk to Azure OpenAI, so you pass in your own client:

```python
from openai import AzureOpenAI
from simple_agents import CertificationData, GoalAgent, AgentType

client = AzureOpenAI(api_key="...", azure_endpoint="...", api_version="...")
data = CertificationData()          # reads data/certifications.json
goal = GoalAgent(client, data)
```

Then give each agent the shared context and run them in order: Goal, Prerequisite, Curriculum, Schedule. Install the one dependency with `pip install -r requirements.txt`.
