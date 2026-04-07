from server.app import app
from farming_env import FarmingEnv

def run_simulation():
    env = FarmingEnv(max_days=5, seed=42)
    state = env.reset()

    print("[START] task=AI-Farming", flush=True)

    total_reward = 0
    step_count = 0

    for i in range(5):
        action = list(env.action_space)[0]  # simple action
        state, reward, done, info = env.step(action)

        step_count += 1
        total_reward += reward

        print(f"[STEP] step={step_count} reward={reward}", flush=True)

        if done:
            break

    print(f"[END] task=AI-Farming score={total_reward} steps={step_count}", flush=True)


if __name__ == "__main__":
    run_simulation()
