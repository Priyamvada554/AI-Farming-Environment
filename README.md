---
title: AI Farming Simulator
emoji: 🌾
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🌱 AI Farming Environment Simulator

## 🚀 Overview

FarmingEnv is an AI-powered farming simulation environment where an agent learns to make optimal decisions such as watering, planting, and harvesting based on changing weather and soil conditions.

This project follows an OpenEnv-style API using `step()`, `reset()`, and `state()` to simulate real-world decision-making.

---

## ❗ Problem

Farmers often struggle to make correct decisions due to unpredictable weather and changing soil conditions.

This can lead to:

- Poor crop yield
- Resource wastage
- Financial loss

---

## 💡 Solution

This project implements a turn-based farming simulation environment where an AI agent learns optimal farming strategies using rewards and penalties.

The system includes:

- **Environment**: `farming_env.py`
  - Random weather (`sunny`, `rainy`, `hot`)
  - Soil moisture tracking
  - Crop growth stages
  - Health system
  - Actions: `water`, `plant`, `harvest`, `wait`

- **Tasks**: `farming_tasks.py`
  - Easy: Keep crop alive for 10 days
  - Medium: Maintain health above 70 for 20 days
  - Hard: Maximize harvest yield within 30 days

- **Grader**: `farming_grader.py`
  - Converts performance into a score between 0.0 and 1.0

- **Agent**: `farming_rule_agent_demo.py`
  - Rule-based agent that interacts with the environment

- **Inference API**: `inference.py`
  - FastAPI server with `/reset`, `/step`, `/state` endpoints

---

## 🖼️ Demo

Live on Hugging Face Spaces: [🚀 Click Here](https://huggingface.co/spaces/Priyambada544/Ai-Farming-Simulator)

---

## ⚙️ How It Works

1. `reset()` initializes the environment
2. Agent selects an action (`water`, `wait`, etc.)
3. `step(action)` updates the state and returns reward
4. Agent learns optimal behavior over time

---

## 🌍 Action Space

| Action | Description |
|--------|-------------|
| `water` | Water the crop |
| `plant` | Plant a new crop |
| `harvest` | Harvest the crop |
| `wait` | Do nothing |

---

## 👁️ Observation Space

| Field | Type | Description |
|-------|------|-------------|
| `day` | int | Current day (0-30) |
| `soil_moisture` | float | Moisture level (0.0-1.0) |
| `weather` | string | sunny / rainy / hot |
| `crop_stage` | int | 0=empty, 1=sprout, 2=growing, 3=ready |
| `health` | float | Plant health (0-100) |

---

## 🧠 Reward System

- ✅ Good crop health → Positive reward
- 🌾 Successful harvest → High reward (+60 to +80)
- ❌ Overwatering → Penalty (-3.0)
- ❌ Dry soil → Penalty (-3.0)
- ❌ Early harvest → Penalty (-6.0)

---

## 📊 Baseline Scores

| Task | Score |
|------|-------|
| easy_keep_crop_alive | 1.0 |
| medium_maintain_health_above_70 | 1.0 |
| hard_maximize_harvest_yield | 0.8 |

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/reset` | POST | Reset environment |
| `/step` | POST | Take an action |
| `/state` | GET | Get current state |
| `/action_space` | GET | Get available actions |
| `/docs` | GET | Swagger UI |

--- 

## 💻 Tech Stack

- API: FastAPI
- Backend: Python
- Simulation: Custom OpenEnv-style environment
- Deployment: Hugging Face Spaces (Docker)

---

## 📁 Project Structure  

inference.py               → FastAPI OpenEnv server
farming_env.py             → Core environment
farming_tasks.py           → Task definitions
farming_grader.py          → Evaluation logic
farming_rule_agent_demo.py → Demo agent
openenv.yaml               → OpenEnv specification
Dockerfile                 → Docker configuration
requirements.txt           → Python dependencies
README.md                  → This file

---

## ▶️ How to Run Locally

### Install Dependencies
```bash
pip install -r requirements.txt
pip install fastapi uvicorn
```

### Run the API Server
```bash
uvicorn inference:app --host 0.0.0.0 --port 7860
```

Open Swagger UI: `http://localhost:7860/docs`

---

## 🌍 Why This Matters

This project demonstrates how AI agents can learn decision-making in dynamic real-world environments like agriculture. It can be extended to real-world smart farming systems.

---

## 🏁 Conclusion

- Built a real-world OpenEnv-compatible simulation environment
- Implemented AI decision-making using rewards and penalties
- Deployed with FastAPI + Docker on Hugging Face Spaces

---

## 🙌 Author

**Priyambada Kumari**
