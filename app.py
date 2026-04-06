import gradio as gr
from farming_env import FarmingEnv
from farming_rule_agent_demo import choose_action, explain_action

def run_simulation(seed=0):
    """Run a 30-day farming simulation with the rule-based agent."""
    seed = int(seed)
    env = FarmingEnv(max_days=30, seed=seed)
    state = env.reset()

    log_lines = []
    log_lines.append("AI Farming Simulator - Rule-Based Agent")
    log_lines.append("=" * 50)
    log_lines.append("")

    total_reward = 0.0
    done = False

    while not done:
        action = choose_action(env)
        reason = explain_action(env, action)
        state, reward, done, info = env.step(action)
        total_reward += reward

        day = state["day"]
        soil = state["soil_moisture"]
        stage = state["crop_stage"]
        health = state["health"]
        weather = state["weather"]
        action_detail = info.get("action_detail", "")

        log_lines.append(
            "Day " + str(day) + " | " + weather + " | soil=" + str(round(soil, 2)) + " | stage=" + str(stage) + " | health=" + str(round(health, 1)) + " | action=" + action + " (" + reason + ") | reward=" + str(round(reward, 2))
        )
        if action_detail:
            log_lines.append("      - " + action_detail)

    log_lines.append("")
    log_lines.append("Total Reward: " + str(round(total_reward, 2)))
    log_lines.append("")
    log_lines.append("Simulation complete!")

    return "\n".join(log_lines)

demo = gr.Interface(
    fn=run_simulation,
    inputs=[
        gr.Number(label="Random Seed (optional)", value=0, precision=0)
    ],
    outputs=gr.Textbox(label="Simulation Results", lines=30),
    title="AI Farming Environment Simulator",
    description="Run a 30-day farming simulation with an AI agent that makes decisions to plant, water, harvest, or wait."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)