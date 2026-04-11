---
title: Cyber War Env
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Cyber War Environment

## Overview
Cyber War Environment is a reinforcement learning-based cybersecurity simulation built using OpenEnv. It models real-world cyber defense scenarios where an AI agent acts as a security analyst and makes decisions to mitigate threats while maintaining system stability.

The environment is designed to evaluate decision-making under uncertainty, balancing attack mitigation, false positives, and system performance.

---

## Features

- OpenEnv compliant environment
- FastAPI-based backend
- Dockerized deployment on Hugging Face Spaces
- Multi-task evaluation system (easy, medium, hard)
- Dynamic reward shaping mechanism
- Real-time API interaction for agent evaluation
- Structured logging for benchmarking and validation

### 🧠 Advanced Capabilities

- Multi-stage cyber attack simulation (scan → brute force → DDoS)
- Stateful environment with attack progression
- Sequential decision-making required (not random RL)
- Intelligent hybrid agent (rule-based + LLM-ready)
- Partial reward grading (normalized between 0 and 1)
- Balanced defense vs false positive trade-offs

---

## Environment Design

### Observation Space
The agent receives the following information at each step:

- alerts: List of detected events (type and severity)
- system_load: Current system load (0–100)
- threat_level: Overall threat level (1–10)

---

### Action Space
The agent can perform the following actions:

- block_ip: Block suspicious IP addresses
- rate_limit: Limit incoming traffic
- investigate: Analyze suspicious activity
- ignore: Take no action

---

## Tasks and Evaluation

The environment includes three difficulty levels:


| Task   | Description |
|--------|------------|
| Easy   | Detect and mitigate brute-force attacks |
| Medium | Handle mixed traffic (normal + attack) |
| Hard   | Multi-stage cyber attack defense (sequential reasoning required) |

Each task includes a grading function that contributes to the final reward.

---

## Reward Function

The reward is computed using a combination of:

- Correct attack mitigation
- Penalties for false positives
- System load optimization
- Threat level reduction
- Task-specific scoring

Final reward formula:

reward = base_reward + (task_score * 10)

The final score is normalized in the range [0, 1].

---

## Evaluation Strategy

- Task-specific success criteria
- Hard task requires full attack mitigation sequence
- Medium task balances detection and stability
- Easy task focuses on basic threat handling

---

## API Endpoints

The environment exposes the following REST APIs:

- GET `/`  
  Health check endpoint

- GET `/health`  
  Service status verification

- POST `/reset`  
  Resets the environment and returns initial observation

- POST `/step`  
  Executes an action and returns next state, reward, and status

- GET `/state`  
  Returns internal environment state

---

## Inference

The project includes an `inference.py` script that:

- Connects to the deployed Hugging Face Space
- Interacts with the environment via API
- Executes a rule-based agent
- Logs results in OpenEnv-compliant format

### Agent Intelligence

- Rule-based decision making (primary)
- Sequential reasoning for attack stages
- Handles noisy + mixed alerts
- Avoids over-blocking (false positives)

Example output:

[START] task=easy env=cyber-war-env model=gpt-4o-mini
[STEP] step=1 action=rate_limit reward=0.60 done=false error=null
...
[END] success=true steps=10 score=0.45 rewards=...

---

## Deployment

The environment is deployed on Hugging Face Spaces using Docker.

Live endpoint:  
https://shakyas1mha-cyber-war-env.hf.space

---

## Validation

The project has been validated using:

- openenv validate
- Hugging Face deployment checks
- End-to-end inference execution
- Reward normalization

Status:

- Environment: Running
- Inference: Successful
- Score: 0–1
- OpenEnv Validation: Passed

---

## Project Structure

server/  
  app.py  
  cyber_env.py  

models.py  
inference.py  
openenv.yaml  
Dockerfile  
pyproject.toml  
README.md  

---

## How to Run Locally

pip install -r requirements.txt  
uvicorn server.app:app --host 0.0.0.0 --port 7860  

---

## Future Improvements

- Integration with LLM-based decision agents
- Advanced anomaly detection models
- Real-time monitoring dashboard
- Multi-agent simulation support

---

## License

This project is for research and educational purposes.