"""
Task evaluators for the FarmingEnv.

These functions are meant to be used after you run an episode.
They do not control the agent; they only check whether the goal was achieved.

Typical usage pattern:
  env = FarmingEnv(max_days=30, seed=0)
  s = env.reset()
  state_history = [s]
  reward_history = []
  info_history = []
  done = False
  while not done:
      action = ...  # your policy
      s, r, done, info = env.step(action)
      state_history.append(s)
      reward_history.append(r)
      info_history.append(info)
  ok = easy_keep_crop_alive(state_history)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def _find_crop_start_index(state_history: List[Dict[str, Any]]) -> Optional[int]:
    """
    Find the first time the crop exists (crop_stage > 0).

    Returns None if the crop never appears.
    """
    for i, s in enumerate(state_history):
        if s.get("crop_stage", 0) > 0:
            return i
    return None


def easy_keep_crop_alive(
    state_history: List[Dict[str, Any]],
    required_days: int = 10,
) -> bool:
    """
    Easy goal: Keep crop alive for `required_days`.

    "Alive" means:
    - crop_stage > 0
    - health > 0

    Logic:
    - Find the first day where a crop exists.
    - Check that for the next `required_days` days, it stays alive.
    """
    start_i = _find_crop_start_index(state_history)
    if start_i is None:
        return False

    # We need required_days consecutive days *including* the start day.
    end_i = start_i + required_days - 1
    if end_i >= len(state_history):
        return False

    for s in state_history[start_i : end_i + 1]:
        if s.get("crop_stage", 0) <= 0:
            return False
        if s.get("health", 0.0) <= 0.0:
            return False
    return True


def medium_maintain_health_above_70(
    state_history: List[Dict[str, Any]],
    required_days: int = 20,
    health_threshold: float = 70.0,
) -> bool:
    """
    Medium goal: Maintain crop health above `health_threshold` for `required_days`.

    Logic:
    - Find the first day where a crop exists.
    - Check that for the next `required_days` days:
      - crop_stage > 0
      - health > health_threshold
    """
    start_i = _find_crop_start_index(state_history)
    if start_i is None:
        return False

    end_i = start_i + required_days - 1
    if end_i >= len(state_history):
        return False

    for s in state_history[start_i : end_i + 1]:
        if s.get("crop_stage", 0) <= 0:
            return False
        if s.get("health", 0.0) <= health_threshold:
            return False
    return True


def hard_maximize_harvest_yield(
    reward_history: List[float],
    info_history: List[Dict[str, Any]],
    min_total_harvest_reward: float = 200.0,
) -> bool:
    """
    Hard goal: Maximize harvest yield within 30 days.

    Since we can't prove a run is the global maximum without checking many runs,
    this task checks a practical achievement threshold:
    - sum of rewards from successful harvest steps must be >= `min_total_harvest_reward`.

    Logic:
    - Count only steps where the env reports `action_detail == "harvest successful"`.
    - Sum the corresponding step rewards.
    - If the sum reaches the threshold, the goal is achieved.
    """
    if len(reward_history) != len(info_history):
        raise ValueError("reward_history and info_history must have the same length.")

    total = 0.0
    for r, info in zip(reward_history, info_history):
        if info.get("action_detail") == "harvest successful":
            total += float(r)

    return total >= float(min_total_harvest_reward)

