"""
Simple beginner-friendly farming simulation.

Actions are applied, then the environment advances by 1 day.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass
class FarmingEnv:
    """
    Tiny turn-based environment.

    State returned by `state()` includes:
      - day
      - soil_moisture
      - weather
      - crop_stage
      - health
    """

    # Episode ends after this many days.
    max_days: int = 30
    seed: int | None = None

    # --- Required state fields ---
    day: int = 0
    soil_moisture: float = 0.5  # 0.0 (dry) .. 1.0 (wet)
    weather: str = "sunny"  # "sunny" | "rainy" | "hot"
    crop_stage: int = 0  # 0=empty, 1=sprout, 2=grown, 3=ready
    health: float = 100.0  # 0..100

    # --- Simple constants used by the beginner simulation ---
    _soil_cap: float = 1.0
    _health_cap: float = 100.0

    # "Good" moisture range (rewards/penalties are relative to this).
    _ideal_moisture_low: float = 0.45
    _ideal_moisture_high: float = 0.65

    def __post_init__(self) -> None:
        if self.seed is not None:
            random.seed(self.seed)

    @property
    def action_space(self) -> Tuple[str, ...]:
        return ("water", "plant", "harvest", "wait")

    def state(self) -> Dict[str, Any]:
        """Return the current environment state."""
        return {
            "day": self.day,
            "soil_moisture": round(self.soil_moisture, 3),
            "weather": self.weather,
            "crop_stage": self.crop_stage,
            "health": round(self.health, 2),
        }

    def reset(
        self,
        seed: int | None = None,
        episode_id: str | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Reset environment back to its starting state.

        OpenEnv/Gym-style runners may pass `seed`, `episode_id`, and extra kwargs.
        We accept them to avoid signature errors.
        """
        # If caller provides a seed at runtime, use it for reproducibility.
        if seed is not None:
            random.seed(seed)
        self.day = 0
        self.soil_moisture = 0.5
        self.weather = "sunny"
        self.crop_stage = 0
        self.health = 100.0
        return self.state()

    def step(
        self, action: Any
    ) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Apply an action and advance the simulation by 1 day.

        Returns:
          (state, reward, done, info)
        """
        # Allow simple action encodings used by some runners.
        # Examples: "water" or {"action": "water"}.
        if isinstance(action, dict) and "action" in action:
            action = action["action"]
        elif isinstance(action, (list, tuple)) and len(action) == 1:
            action = action[0]

        if not isinstance(action, str):
            raise ValueError(f"Action must be a string. Got: {type(action)}")

        if action not in self.action_space:
            raise ValueError(f"Unknown action: {action}. Choose from {self.action_space}")

        info: Dict[str, Any] = {"action": action}

        # Keep previous values so we can measure "what changed".
        prev_state = {
            "day": self.day,
            "soil_moisture": self.soil_moisture,
            "weather": self.weather,
            "crop_stage": self.crop_stage,
            "health": self.health,
        }

        reward = 0.0

        # ----------------------------
        # 1) Immediate action effect
        # ----------------------------
        if action == "water":
            # Water increases moisture, but too much watering becomes a penalty.
            moisture_before = self.soil_moisture
            self.soil_moisture = min(self._soil_cap, self.soil_moisture + 0.20)

            # Positive reward when watering is clearly needed.
            if self.crop_stage > 0:
                if moisture_before < self._ideal_moisture_low:
                    reward += 1.0  # "good" watering
                elif moisture_before > self._ideal_moisture_high:
                    reward -= 1.5  # likely overwatering
                else:
                    reward += 0.2  # watering while "ok"
            else:
                # Watering empty soil is usually wasted effort.
                reward -= 0.5

            # Extra penalty if the action pushes moisture too high immediately.
            if moisture_before >= 0.70 or self.soil_moisture >= 0.85:
                reward -= 3.0  # overwatering

            info["action_detail"] = "applied watering"

        elif action == "plant":
            # Planting is only allowed on an empty field.
            if self.crop_stage == 0:
                self.crop_stage = 1

                # Reward planting when moisture is in the ideal range.
                if self._ideal_moisture_low <= self.soil_moisture <= self._ideal_moisture_high:
                    reward += 1.5
                else:
                    reward += 0.5
                info["action_detail"] = "planted crop"
            else:
                reward -= 1.0
                info["action_detail"] = "plant failed (already planted)"

        elif action == "harvest":
            # Harvest is only successful when the crop is ready (stage 3).
            if self.crop_stage >= 3:
                # High reward for successful harvest.
                # - health matters (healthy crops produce more)
                # - moisture matters (very dry or very wet can reduce yield)
                health_factor = max(0.0, self.health) / self._health_cap  # 0..1

                # Convert distance from ideal moisture into a 0..1 "moisture quality".
                mid = (self._ideal_moisture_low + self._ideal_moisture_high) / 2.0
                half_range = (self._ideal_moisture_high - self._ideal_moisture_low) / 2.0
                if half_range <= 0:
                    moisture_quality = 0.5
                else:
                    moisture_quality = 1.0 - min(1.0, abs(self.soil_moisture - mid) / half_range)

                # Big base reward + bonuses.
                reward = 60.0 * health_factor + 20.0 * moisture_quality

                # Successful harvest resets the field.
                self.crop_stage = 0
                info["action_detail"] = "harvest successful"
            else:
                # Harvesting too early is a bad decision.
                reward -= 6.0
                info["action_detail"] = "harvest too early"

        elif action == "wait":
            # Waiting can be good if your moisture is already in the ideal range.
            if self.crop_stage > 0:
                if self._ideal_moisture_low <= self.soil_moisture <= self._ideal_moisture_high:
                    reward += 0.3
                elif self.soil_moisture < 0.25:
                    # Waiting while very dry is a form of underwatering.
                    reward -= 1.5
                else:
                    reward -= 0.2
            else:
                # Waiting with no crop doesn't change much.
                reward += 0.0
            info["action_detail"] = "no direct action"

        # --------------------------------
        # 2) Natural environment changes
        # --------------------------------
        # Weather randomly changes each day.
        # We keep it simple with fixed probabilities.
        self.weather = random.choices(
            population=["sunny", "rainy", "hot"],
            weights=[0.50, 0.30, 0.20],
            k=1,
        )[0]

        # Weather affects soil moisture each day.
        if self.weather == "sunny":
            self.soil_moisture -= 0.05
        elif self.weather == "rainy":
            self.soil_moisture += 0.10
        else:  # "hot"
            self.soil_moisture -= 0.10

        # Clamp to valid range.
        self.soil_moisture = max(0.0, min(self._soil_cap, self.soil_moisture))

        # ----------------------------
        # 3) Crop growth + health
        # ----------------------------
        prev_crop_stage = prev_state["crop_stage"]
        prev_health = prev_state["health"]

        # Crop growth chance increases when moisture is reasonable.
        if 0 < self.crop_stage < 3:
            stage_growth_chance = 0.12

            # Moisture helps growth only when in a reasonable band.
            if self.soil_moisture >= 0.6:
                stage_growth_chance += 0.20
            elif self.soil_moisture >= 0.3:
                stage_growth_chance += 0.10

            # Rain is slightly better; hot is a bit worse.
            if self.weather == "rainy":
                stage_growth_chance += 0.15
            elif self.weather == "hot":
                stage_growth_chance -= 0.05

            # Advance stage with some probability.
            if random.random() < max(0.0, stage_growth_chance):
                self.crop_stage += 1
                reward += 2.0  # positive reward for progress
                info["stage_up"] = True
            else:
                info["stage_up"] = False
        else:
            info["stage_up"] = False

        # Health changes:
        # - dry soil harms health
        # - hot weather harms health
        # - rainy weather gives a small boost
        if self.crop_stage > 0:
            if self.soil_moisture < 0.30:
                self.health -= 5.0
            if self.weather == "hot":
                self.health -= 3.0
            if self.weather == "rainy":
                self.health += 1.0

        # Clamp health.
        self.health = max(0.0, min(self._health_cap, self.health))

        # ---------------------------------------
        # 4) Underwatering / overwatering rewards
        # ---------------------------------------
        # These checks happen after weather changes (so they reflect the full day outcome).
        if self.crop_stage > 0:
            # Underwatering penalty if it's too dry.
            if self.soil_moisture < 0.20:
                reward -= 3.0
                info["underwater_penalty"] = True
            else:
                info["underwater_penalty"] = False

            # Overwatering penalty if it's very wet.
            if self.soil_moisture > 0.85:
                reward -= 3.0
                info["overwater_penalty"] = True
            else:
                info["overwater_penalty"] = False

        # --------------------------------
        # 5) Small "good decision" shaping
        # --------------------------------
        # If crop exists, staying near ideal moisture is rewarded a little.
        if self.crop_stage > 0 and self._ideal_moisture_low <= self.soil_moisture <= self._ideal_moisture_high:
            reward += 0.2

        # Track changes for debugging/learning.
        info["prev_state"] = prev_state
        info["new_state"] = self.state()
        info["stage_changed"] = self.crop_stage != prev_crop_stage
        info["health_changed"] = self.health - prev_health

        # ----------------
        # 6) Advance time
        # ----------------
        self.day += 1

        # Episode ends strictly after 30 days (regardless of health).
        # This matches the requirement.
        done = self.day >= self.max_days
        info["done_reason"] = "day_limit_reached"

        return self.state(), reward, done, info


if __name__ == "__main__":
    # Tiny demo loop.
    env = FarmingEnv(max_days=10, seed=42)
    s = env.reset()
    print("reset ->", s)

    actions = ["plant", "wait", "water", "wait", "wait", "harvest"]
    for a in actions:
        s, r, done, info = env.step(a)
        print(f"step({a}) -> reward={r:.2f}, done={done}, state={s}, weather={s['weather']}")
        if done:
            break

