"""
Rule-based agent demo for FarmingEnv.

Policy:
  - If soil moisture < 0.30 -> "water"
  - If crop is ready -> "harvest"
  - Otherwise -> "wait"
"""

from __future__ import annotations

from typing import Optional

from farming_env import FarmingEnv


def choose_action(env: FarmingEnv) -> str:
    """Pick the next action using the simple rule-based policy."""
    if env.crop_stage == 0:
        return "plant"
    if env.soil_moisture < 0.30:
        return "water"
    if env.crop_stage >= 3:
        return "harvest"
    return "wait"


def explain_action(env: FarmingEnv, action: str) -> str:
    """Short human-readable explanation for the action."""
    if action == "plant":
        return "crop field is empty (crop_stage == 0) -> plant"
    if action == "water":
        return f"soil is too dry (soil_moisture < 0.30, now {env.soil_moisture:.2f}) -> water"
    if action == "harvest":
        return "crop is ready (crop_stage >= 3) -> harvest"
    return "no urgent needs -> wait"


def run_one_episode(seed: Optional[int] = 0) -> float:
    env = FarmingEnv(max_days=30, seed=seed)
    state = env.reset()

    total_reward = 0.0
    done = False

    while not done:
        action = choose_action(env)
        reason = explain_action(env, action)
        state, reward, done, info = env.step(action)
        total_reward += reward

        # Day-wise log for readability.
        day = state["day"]
        soil = state["soil_moisture"]
        stage = state["crop_stage"]
        health = state["health"]
        weather = state["weather"]
        action_detail = info.get("action_detail")

        if action_detail:
            print(
                f"Day {day:2d} | {weather:5s} | soil={soil:.2f} | stage={stage} | "
                f"health={health:.1f} | action={action} ({reason}) | reward={reward:.2f} | {action_detail}"
            )
        else:
            print(
                f"Day {day:2d} | {weather:5s} | soil={soil:.2f} | stage={stage} | "
                f"health={health:.1f} | action={action} ({reason}) | reward={reward:.2f}"
            )

    return total_reward


if __name__ == "__main__":
    total = run_one_episode(seed=0)
    print(f"Total reward: {total:.2f}")

