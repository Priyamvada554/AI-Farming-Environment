"""
Enhanced rule-based agent with scoring system for FarmingEnv.

Policy uses action scoring instead of simple rules:
  - Score each action based on current state
  - Pick the action with the highest score
  - More sophisticated decision-making
"""

from __future__ import annotations

from typing import Optional, Dict, Tuple

from farming_env import FarmingEnv


def score_action(env: FarmingEnv, action: str) -> float:
    """
    Score an action based on the current environment state.
    Higher score = better action for this situation.
    """
    score = 0.0
    
    if action == "plant":
        # Only plant if field is empty
        if env.crop_stage == 0:
            score = 50.0  # Base score for planting
            # Bonus if soil moisture is in ideal range
            if 0.45 <= env.soil_moisture <= 0.65:
                score += 15.0
            else:
                score += 5.0  # Still okay to plant, but not ideal
        else:
            score = -100.0  # Can't plant if already planted
    
    elif action == "water":
        # Score water based on how much it's needed
        if env.crop_stage == 0:
            score = -50.0  # Waste to water empty field
        else:
            # Need indicates how dry the soil is
            if env.soil_moisture < 0.20:
                score = 60.0  # Critical: very dry
            elif env.soil_moisture < 0.30:
                score = 50.0  # Important: dry
            elif env.soil_moisture < 0.40:
                score = 30.0  # Helpful: somewhat dry
            elif env.soil_moisture < 0.50:
                score = 20.0  # Mild: getting dry
            else:
                score = -30.0  # Bad: already wet
            
            # Adjust based on health and weather
            if env.health < 50:
                score += 10.0  # Watering helps sick plants
            if env.weather == "hot":
                score += 5.0  # More critical in hot weather
    
    elif action == "harvest":
        # Score based on crop readiness
        if env.crop_stage >= 3:
            score = 80.0  # Ready to harvest
            # Bonus if health is good
            health_multiplier = max(0.5, env.health / 100.0)
            score += 20.0 * health_multiplier
        elif env.crop_stage == 2:
            score = 10.0  # Almost ready, risky
        else:
            score = -80.0  # Way too early
    
    elif action == "wait":
        # Waiting is good when things are stable
        if env.crop_stage == 0:
            score = 10.0  # Waiting for the right time to plant
        elif 0.40 <= env.soil_moisture <= 0.70 and env.health > 70:
            score = 40.0  # Good conditions, wait for growth
        elif env.crop_stage >= 3:
            score = -50.0  # Don't wait, harvest!
        else:
            score = 15.0  # Waiting is neutral
    
    return score


def choose_action(env: FarmingEnv) -> str:
    """Pick the next action using the scoring-based policy."""
    actions = env.action_space
    scores = {action: score_action(env, action) for action in actions}
    best_action = max(scores, key=scores.get)
    return best_action


def explain_action(env: FarmingEnv, action: str) -> str:
    """Detailed human-readable explanation for the action."""
    explanations = {
        "plant": f"Field empty (stage=0) & soil ready (moisture={env.soil_moisture:.2f}) → Plant now",
        "water": f"Soil dry (moisture={env.soil_moisture:.2f}<0.30) → Watering required",
        "harvest": f"Crop mature (stage={env.crop_stage}≥3) & ready → Harvest for reward",
        "wait": f"Conditions stable → Wait for growth (soil={env.soil_moisture:.2f}, health={env.health:.0f})"
    }
    return explanations.get(action, "Unknown action")


def get_action_scores(env: FarmingEnv) -> Dict[str, float]:
    """Get scores for all possible actions."""
    actions = env.action_space
    return {action: score_action(env, action) for action in actions}


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

