/**
 * Browser-side simulation to visualize the FarmingEnv.
 *
 * This mirrors the logic in `farming_env.py` closely enough for UI visualization.
 * It does NOT call the Python environment (no backend needed for this simple UI).
 */

export function createRng(seed) {
  // Simple deterministic RNG (mulberry32).
  // Source: common small PRNG pattern.
  let t = seed >>> 0;
  return function rng() {
    t += 0x6d2b79f5;
    let x = Math.imul(t ^ (t >>> 15), 1 | t);
    x ^= x + Math.imul(x ^ (x >>> 7), 61 | x);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

function clamp(x, lo, hi) {
  return Math.max(lo, Math.min(hi, x));
}

function weightedChoice(rng, population, weights) {
  const total = weights.reduce((a, b) => a + b, 0);
  let r = rng() * total;
  for (let i = 0; i < population.length; i++) {
    r -= weights[i];
    if (r <= 0) return population[i];
  }
  return population[population.length - 1];
}

export class FarmingEnvClient {
  constructor({ maxDays = 30, seed = 0 } = {}) {
    this.maxDays = maxDays;
    this.seed = seed;
    this.rng = createRng(seed);

    this.day = 0;
    this.soil_moisture = 0.5;
    this.weather = "sunny";
    this.crop_stage = 0;
    this.health = 100.0;

    // Keep constants consistent with Python defaults.
    this._soil_cap = 1.0;
    this._health_cap = 100.0;
    this._ideal_moisture_low = 0.45;
    this._ideal_moisture_high = 0.65;
  }

  actionSpace() {
    return ["water", "plant", "harvest", "wait"];
  }

  state() {
    return {
      day: this.day,
      soil_moisture: Math.round(this.soil_moisture * 1000) / 1000,
      weather: this.weather,
      crop_stage: this.crop_stage,
      health: Math.round(this.health * 100) / 100,
    };
  }

  reset({ seed = undefined } = {}) {
    if (seed !== undefined) {
      this.seed = seed;
      this.rng = createRng(seed);
    }

    this.day = 0;
    this.soil_moisture = 0.5;
    this.weather = "sunny";
    this.crop_stage = 0;
    this.health = 100.0;
    return this.state();
  }

  step(action) {
    if (typeof action !== "string") {
      // Allow {action:"..."} encoding for convenience.
      if (action && typeof action === "object" && action.action) action = action.action;
      else throw new Error("Action must be a string.");
    }
    if (!this.actionSpace().includes(action)) {
      throw new Error(`Unknown action: ${action}`);
    }

    const prev = {
      day: this.day,
      soil_moisture: this.soil_moisture,
      weather: this.weather,
      crop_stage: this.crop_stage,
      health: this.health,
    };

    let reward = 0.0;
    const info = { action };

    // 1) Immediate action effect
    if (action === "water") {
      const moisture_before = this.soil_moisture;
      this.soil_moisture = Math.min(this._soil_cap, this.soil_moisture + 0.20);

      if (this.crop_stage > 0) {
        if (moisture_before < this._ideal_moisture_low) reward += 1.0;
        else if (moisture_before > this._ideal_moisture_high) reward -= 1.5;
        else reward += 0.2;
      } else {
        reward -= 0.5;
      }

      if (moisture_before >= 0.70 || this.soil_moisture >= 0.85) reward -= 3.0;
      info.action_detail = "applied watering";
    } else if (action === "plant") {
      if (this.crop_stage === 0) {
        this.crop_stage = 1;
        if (
          this.soil_moisture >= this._ideal_moisture_low &&
          this.soil_moisture <= this._ideal_moisture_high
        ) {
          reward += 1.5;
        } else {
          reward += 0.5;
        }
        info.action_detail = "planted crop";
      } else {
        reward -= 1.0;
        info.action_detail = "plant failed (already planted)";
      }
    } else if (action === "harvest") {
      if (this.crop_stage >= 3) {
        const health_factor = clamp(this.health, 0, this._health_cap) / this._health_cap;

        const mid = (this._ideal_moisture_low + this._ideal_moisture_high) / 2.0;
        const half_range = (this._ideal_moisture_high - this._ideal_moisture_low) / 2.0;
        let moisture_quality;
        if (half_range <= 0) moisture_quality = 0.5;
        else {
          moisture_quality = 1.0 - Math.min(1.0, Math.abs(this.soil_moisture - mid) / half_range);
        }

        reward = 60.0 * health_factor + 20.0 * moisture_quality;
        this.crop_stage = 0;
        info.action_detail = "harvest successful";
      } else {
        reward -= 6.0;
        info.action_detail = "harvest too early";
      }
    } else if (action === "wait") {
      if (this.crop_stage > 0) {
        if (
          this.soil_moisture >= this._ideal_moisture_low &&
          this.soil_moisture <= this._ideal_moisture_high
        ) {
          reward += 0.3;
        } else if (this.soil_moisture < 0.25) {
          reward -= 1.5;
        } else {
          reward -= 0.2;
        }
      }
      info.action_detail = "no direct action";
    }

    // 2) Natural changes
    this.weather = weightedChoice(this.rng, ["sunny", "rainy", "hot"], [0.5, 0.3, 0.2]);
    if (this.weather === "sunny") this.soil_moisture -= 0.05;
    else if (this.weather === "rainy") this.soil_moisture += 0.10;
    else this.soil_moisture -= 0.10;
    this.soil_moisture = clamp(this.soil_moisture, 0, this._soil_cap);

    // 3) Crop growth + health
    let stageUp = false;
    if (this.crop_stage > 0 && this.crop_stage < 3) {
      let stage_growth_chance = 0.12;

      if (this.soil_moisture >= 0.6) stage_growth_chance += 0.20;
      else if (this.soil_moisture >= 0.3) stage_growth_chance += 0.10;

      if (this.weather === "rainy") stage_growth_chance += 0.15;
      else if (this.weather === "hot") stage_growth_chance -= 0.05;

      const prob = Math.max(0.0, stage_growth_chance);
      if (this.rng() < prob) {
        this.crop_stage += 1;
        reward += 2.0;
        stageUp = true;
      }
    }
    info.stage_up = stageUp;

    if (this.crop_stage > 0) {
      if (this.soil_moisture < 0.30) this.health -= 5.0;
      if (this.weather === "hot") this.health -= 3.0;
      if (this.weather === "rainy") this.health += 1.0;
    }
    this.health = clamp(this.health, 0, this._health_cap);

    // 4) Underwatering / overwatering penalties
    if (this.crop_stage > 0) {
      if (this.soil_moisture < 0.20) {
        reward -= 3.0;
        info.underwater_penalty = true;
      } else info.underwater_penalty = false;

      if (this.soil_moisture > 0.85) {
        reward -= 3.0;
        info.overwater_penalty = true;
      } else info.overwater_penalty = false;
    }

    // 5) Small shaping for good moisture
    if (
      this.crop_stage > 0 &&
      this.soil_moisture >= this._ideal_moisture_low &&
      this.soil_moisture <= this._ideal_moisture_high
    ) {
      reward += 0.2;
    }

    // 6) Advance time / done
    this.day += 1;
    const done = this.day >= this.maxDays;
    info.done_reason = "day_limit_reached";
    info.prev_state = prev;
    info.new_state = this.state();
    info.stage_changed = prev.crop_stage !== this.crop_stage;
    info.health_changed = this.health - prev.health;

    return [this.state(), reward, done, info];
  }
}

