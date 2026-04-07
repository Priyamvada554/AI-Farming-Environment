from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from farming_env import FarmingEnv

app = FastAPI()
env = FarmingEnv(max_days=30, seed=42)
env.reset()

class ResetRequest(BaseModel):
    seed: Optional[int] = 42

class StepRequest(BaseModel):
    action: str

@app.get("/")
def root():
    return {"status": "ok", "name": "AI Farming Simulator"}

@app.post("/reset")
def reset(request: ResetRequest = None):
    global env
    seed = request.seed if request and request.seed is not None else 42
    env = FarmingEnv(max_days=30, seed=seed)
    state = env.reset(seed=seed)
    return {"state": state, "status": "ok"}

@app.post("/step")
def step(request: StepRequest):
    state, reward, done, info = env.step(request.action)
    return {"state": state, "reward": reward, "done": done, "info": info}

@app.get("/action_space")
def action_space():
    return {"actions": list(env.action_space)}

import uvicorn

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
