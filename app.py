"""
AI Farming Simulator - Advanced Interactive Dashboard

This is the main app with:
- Modern dashboard with health cards
- Real-time graphs
- AI decision explanations
- Manual control mode
- Smart scoring-based AI logic
"""

import gradio as gr
import matplotlib.pyplot as plt
import io
from farming_env import FarmingEnv
from farming_rule_agent_demo import choose_action, explain_action, get_action_scores


class SimulationState:
    """Track simulation state across interactions."""
    def __init__(self):
        self.env = None
        self.history = {
            'day': [],
            'soil_moisture': [],
            'health': [],
            'reward': [],
            'action': [],
            'weather': [],
            'crop_stage': []
        }
        self.total_reward = 0.0
        self.mode = "ai"
        
    def reset(self, seed=0):
        """Start a new simulation."""
        self.env = FarmingEnv(max_days=30, seed=int(seed))
        self.env.reset(seed=int(seed))
        self.history = {
            'day': [],
            'soil_moisture': [],
            'health': [],
            'reward': [],
            'action': [],
            'weather': [],
            'crop_stage': []
        }
        self.total_reward = 0.0
        
    def step(self, action):
        """Execute one step."""
        state, reward, done, info = self.env.step(action)
        self.total_reward += reward
        
        # Record history
        self.history['day'].append(state['day'])
        self.history['soil_moisture'].append(state['soil_moisture'])
        self.history['health'].append(state['health'])
        self.history['reward'].append(reward)
        self.history['action'].append(action)
        self.history['weather'].append(state['weather'])
        self.history['crop_stage'].append(state['crop_stage'])
        
        return state, reward, done, info


# Global state
sim_state = SimulationState()


def get_health_status(health):
    """Determine health status and color."""
    if health >= 80:
        return "🟢 Excellent", "green"
    elif health >= 60:
        return "🟡 Good", "gold"
    elif health >= 40:
        return "🟠 Fair", "orange"
    else:
        return "🔴 Critical", "red"


def get_weather_emoji(weather):
    """Get emoji for weather."""
    return {
        'sunny': '☀️',
        'rainy': '🌧️',
        'hot': '🔥'
    }.get(weather, '❓')


def get_stage_name(stage):
    """Get crop stage name."""
    return {
        0: "🌾 Empty",
        1: "🌱 Sprouting",
        2: "🪴 Growing",
        3: "🌽 Ready to Harvest"
    }.get(stage, f"Stage {stage}")


def generate_dashboard_html(state_dict):
    """Generate beautiful HTML dashboard."""
    health = state_dict['health']
    soil = state_dict['soil_moisture']
    weather = state_dict['weather']
    stage = state_dict['crop_stage']
    day = state_dict['day']
    
    health_status, health_color = get_health_status(health)
    weather_emoji = get_weather_emoji(weather)
    stage_name = get_stage_name(stage)
    
    # Determine soil moisture color
    if soil < 0.3:
        soil_color = "#e74c3c"  # red
    elif soil < 0.45:
        soil_color = "#f39c12"  # orange
    elif soil < 0.65:
        soil_color = "#27ae60"  # green
    else:
        soil_color = "#3498db"  # blue
    
    html = f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px; margin: 20px 0;">
        <!-- Day Card -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 32px; font-weight: bold;">📅</div>
            <div style="font-size: 24px; font-weight: bold; margin-top: 8px;">{day}/30</div>
            <div style="font-size: 12px; margin-top: 4px; opacity: 0.9;">Days Elapsed</div>
        </div>
        
        <!-- Health Card -->
        <div style="background: linear-gradient(135deg, {'#27ae60' if health >= 60 else '#e74c3c'} 0%, {'#16a085' if health >= 60 else '#c0392b'} 100%); 
                    padding: 20px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 32px;">❤️</div>
            <div style="font-size: 24px; font-weight: bold; margin-top: 8px;">{health:.0f}</div>
            <div style="font-size: 12px; margin-top: 4px; opacity: 0.9;">Plant Health</div>
        </div>
        
        <!-- Soil Moisture Card -->
        <div style="background: linear-gradient(135deg, {soil_color} 0%, {soil_color}cc 100%); 
                    padding: 20px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 32px;">💧</div>
            <div style="font-size: 24px; font-weight: bold; margin-top: 8px;">{soil:.2f}</div>
            <div style="font-size: 12px; margin-top: 4px; opacity: 0.9;">Soil Moisture</div>
            <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.3); border-radius: 4px; margin-top: 10px; overflow: hidden;">
                <div style="width: {soil*100:.0f}%; height: 100%; background: white; border-radius: 4px;"></div>
            </div>
        </div>
        
        <!-- Crop Stage Card -->
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 20px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 32px;">{get_weather_emoji(weather)}</div>
            <div style="font-size: 16px; font-weight: bold; margin-top: 8px;">{weather.capitalize()}</div>
            <div style="font-size: 12px; margin-top: 4px; opacity: 0.9;">{stage_name}</div>
        </div>
    </div>
    """
    return html


def generate_graph(history, sim_complete=False):
    """Generate matplotlib graphs for soil moisture and health."""
    if not history['day']:
        return None
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.patch.set_facecolor('#f8f9fa')
    
    # Soil Moisture Graph
    ax1.plot(history['day'], history['soil_moisture'], marker='o', linewidth=2, 
             color='#3498db', markersize=4, label='Soil Moisture')
    ax1.axhline(y=0.45, color='#27ae60', linestyle='--', linewidth=1, alpha=0.5, label='Ideal Min')
    ax1.axhline(y=0.65, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.5, label='Ideal Max')
    ax1.fill_between(history['day'], 0.45, 0.65, alpha=0.1, color='#27ae60')
    ax1.set_xlabel('Day', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Moisture Level', fontsize=11, fontweight='bold')
    ax1.set_title('💧 Soil Moisture Over Time', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best', fontsize=9)
    ax1.set_ylim(0, 1)
    
    # Health Graph
    ax2.plot(history['day'], history['health'], marker='s', linewidth=2, 
             color='#e74c3c', markersize=4, label='Plant Health')
    ax2.axhline(y=80, color='#27ae60', linestyle='--', linewidth=1, alpha=0.5, label='Excellent')
    ax2.axhline(y=60, color='#f39c12', linestyle='--', linewidth=1, alpha=0.5, label='Good')
    ax2.axhline(y=40, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.5, label='Critical')
    ax2.fill_between(history['day'], 80, 100, alpha=0.1, color='#27ae60')
    ax2.set_xlabel('Day', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Health %', fontsize=11, fontweight='bold')
    ax2.set_title('❤️ Plant Health Over Time', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', fontsize=9)
    ax2.set_ylim(0, 105)
    
    plt.tight_layout()
    
    # Convert to PIL Image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    
    from PIL import Image
    return Image.open(buf)


def run_simulation(seed=0):
    """Run a full 30-day simulation with the AI agent."""
    seed = int(seed)
    sim_state.reset(seed)
    
    log_lines = []
    log_lines.append("🤖 AI Farming Simulator - Smart Farming With Score-Based Decisions")
    log_lines.append("=" * 70)
    log_lines.append("")
    
    done = False
    while not done:
        action = choose_action(sim_state.env)
        reason = explain_action(sim_state.env, action)
        state, reward, done, info = sim_state.step(action)
        
        day = state['day']
        soil = state['soil_moisture']
        stage = state['crop_stage']
        health = state['health']
        weather = state['weather']
        
        log_lines.append(
            f"Day {day:2d} | {weather:5s} | 💧{soil:.2f} | 🌱{stage} | ❤️{health:.0f} | {action:7s} | ⭐{reward:+.2f}"
        )
        log_lines.append(f"         → {reason}")
        log_lines.append("")
    
    log_lines.append("=" * 70)
    log_lines.append(f"🏆 Final Score: {sim_state.total_reward:.2f}")
    log_lines.append("=" * 70)
    
    log_text = "\n".join(log_lines)
    
    # Generate outputs
    final_state = sim_state.env.state()
    dashboard = generate_dashboard_html(final_state)
    graph = generate_graph(sim_state.history, sim_complete=True)
    
    return dashboard, log_text, graph


# ============================================================================
# GRADIO UI
# ============================================================================

demo = gr.Blocks(title="🚜 Advanced AI Farming Simulator")

with demo:
    gr.Markdown("""
    # 🚜 Advanced AI Farming Simulator
    
    **Smart Agriculture in Action!**
    
    Watch an AI agent make intelligent decisions about watering, planting, and harvesting 
    to maximize crop yield while optimizing water usage.
    """)
    
    with gr.Row():
        seed_input = gr.Number(label="🌱 Random Seed", value=42, precision=0)
        run_btn = gr.Button("▶️ Run Simulation", variant="primary", scale=1)
    
    # Dashboard Display
    dashboard_output = gr.HTML(label="📊 Farm Dashboard")
    
    # Detailed Log
    log_output = gr.Textbox(label="📝 Detailed Simulation Log", lines=20, max_lines=25)
    
    # Graphs
    graph_output = gr.Image(label="📈 Performance Graphs")
    
    # About Section
    gr.Markdown("""
    ---
    
    ### 🌍 Smart Farming Features
    
    ✨ **Modern Dashboard** - Real-time metrics with health cards
    
    📊 **Live Graphs** - Track soil moisture and plant health over 30 days
    
    🤖 **Smart AI Logic** - Scoring system that adapts to farm conditions
    
    🎯 **Detailed Explanations** - Every decision is explained
    
    💧 **Water Optimization** - Efficient irrigation reduces waste
    
    🌱 **Crop Management** - Intelligent timing for planting and harvesting
    
    ---
    
    #### How It Works:
    The AI uses a **scoring system** to evaluate each action (water, plant, harvest, wait) 
    based on current conditions like soil moisture, plant health, and weather. 
    It picks the action with the highest score, optimizing for maximum yield and efficiency.
    """)
    
    run_btn.click(
        run_simulation,
        inputs=[seed_input],
        outputs=[dashboard_output, log_output, graph_output]
    )

if __name__ == "__main__":
    demo.launch()
