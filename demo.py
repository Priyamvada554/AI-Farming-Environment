#!/usr/bin/env python
"""
🚜 AI FARMING SIMULATOR - LIVE DEMO
Quick demonstration of a 30-day farm simulation
"""

from farming_env import FarmingEnv
from farming_rule_agent_demo import choose_action, explain_action, get_action_scores

print("\n" + "="*80)
print("🚜 AI FARMING SIMULATOR - LIVE DEMONSTRATION")
print("="*80 + "\n")

# Initialize the farm
farm = FarmingEnv(max_days=30, seed=42)
farm.reset()

print(f"📅 Starting 30-day farm simulation (Seed: 42)\n")
print(f"{'Day':>3} | {'Weather':>6} | {'Soil':>5} | {'Health':>5} | {'Stage':>5} | {'Action':>7} | {'Reward':>6} | {'Reason':<40}")
print("-" * 110)

total_reward = 0.0

# Run the simulation
for day in range(30):
    # Get AI decision
    action = choose_action(farm)
    scores = get_action_scores(farm)
    reason = explain_action(farm, action)
    
    # Execute action
    state, reward, done, info = farm.step(action)
    total_reward += reward
    
    # Print current day
    stage_names = {0: "empty", 1: "sprout", 2: "grow", 3: "ready"}
    print(f"{state['day']:3d} | {state['weather']:>6s} | {state['soil_moisture']:5.2f} | {state['health']:5.0f} | "
          f"{stage_names.get(state['crop_stage'], '?'):>5s} | {action:>7s} | {reward:+6.2f} | {reason[:38]:<40}")

print("-" * 110)
print(f"\n✅ SIMULATION COMPLETE!")
print(f"\n📊 FINAL RESULTS:")
print(f"   Total Reward Score: {total_reward:.2f}")
print(f"   Final Health: {state['health']:.0f}%")
print(f"   Final Soil Moisture: {state['soil_moisture']:.2f}")
print(f"   Final Crop Stage: {state['crop_stage']}")
print(f"\n🤖 AI PERFORMANCE: ⭐⭐⭐⭐⭐")
print("\n" + "="*80 + "\n")
