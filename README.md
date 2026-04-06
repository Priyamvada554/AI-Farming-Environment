---
title: Ai Farming Simulator
emoji: 🚀
colorFrom: gray
colorTo: pink
sdk: gradio
sdk_version: 6.11.0
app_file: app.py
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

- **Web App**: `app.py`
  - Gradio interface for interactive simulation

---

## 🖼️ Demo

Try it live on Hugging Face Spaces: [Link will be provided after deployment]

---

## ⚙️ How It Works

1. `reset()` initializes the environment
2. Agent selects an action (`water`, `wait`, etc.)
3. `step(action)` updates the state and returns reward
4. Agent learns optimal behavior over time

---

## 🧠 Reward System

- ✅ Good crop health → Positive reward
- 🌾 Successful harvest → High reward
- ❌ Overwatering → Penalty
- ❌ Dry soil → Penalty

---

## 💻 Tech Stack

- UI: Gradio
- Backend: Python
- Simulation: Custom OpenEnv-style environment
- Deployment: Hugging Face Spaces

---

## 📁 Project Structure

```
app.py → Gradio web interface
farming_env.py → Core environment
farming_tasks.py → Task definitions
farming_grader.py → Evaluation logic
farming_rule_agent_demo.py → Demo agent
requirements.txt → Python dependencies
README.md → This file
```

---

## ▶️ How to Run Locally

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Web App

On Windows with the local virtual environment:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open the app in your browser at the URL shown in the terminal (usually `http://127.0.0.1:7861` or `http://localhost:7861`).

---

## 🚀 Deploy to Hugging Face Spaces

### Step-by-Step Instructions

1. **Create a Hugging Face Account**
   - Go to [huggingface.co](https://huggingface.co) and sign up

2. **Create a New Space**
   - Click "New Space" on your profile
   - Name: `ai-farming-simulator` (or your choice)
   - License: MIT
   - SDK: Gradio
   - Visibility: Public

3. **Upload Files**
   - Download this project as ZIP
   - Upload all files to your Space:
     - `app.py`
     - `farming_env.py`
     - `farming_tasks.py`
     - `farming_grader.py`
     - `farming_rule_agent_demo.py`
     - `requirements.txt`
     - `README.md`

4. **Deploy**
   - Click "Create Space"
   - Wait for build (usually 2-5 minutes)
   - Your app will be live at: `https://[your-username].huggingface.co/spaces/ai-farming-simulator`

### Troubleshooting

- If build fails, check the logs in the Space settings
- Ensure all Python files are uploaded
- Requirements.txt should contain the current project dependencies:
  - `gradio==4.44.1`
  - `huggingface_hub==0.23.0`
  - `jinja2<3.1`
  - `matplotlib>=3.5.0`

### Optional direct deployment

If you prefer deploying from your local repository, install the Hugging Face CLI and run:

```bash
gradio deploy
```

Then follow the prompts to connect the Space and push the app.

---

## 🌍 Why This Matters

This project demonstrates how AI agents can learn decision-making in dynamic real-world environments like agriculture.
It can be extended to real-world smart farming systems.

---

## 🏁 Conclusion

- Built a real-world simulation environment
- Implemented AI decision-making using rewards
- Demonstrated OpenEnv-compatible system

## 🙌 Author

Priyambada Kumari
