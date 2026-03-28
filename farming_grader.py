"""
Grading helpers for the FarmingEnv tasks.

This stays generic: it can grade either:
  - the boolean result from your task evaluators (True/False), or
  - a dict/numeric metric result (if you later extend tasks to return more info).
"""

from __future__ import annotations

from typing import Any, Dict


def grader(task_result: Any) -> float:
    """
    Convert a task result into a score in [0.0, 1.0].

    Higher performance => higher score.

    Expected inputs:
      - bool: True -> 1.0, False -> 0.0
      - float/int: if already in [0,1], use it; otherwise clamp to [0,1]
      - dict: uses common metric keys when present:
          * {"passed": bool} => pass/fail
          * {"score": float} => normalized score
          * {"days_alive": int, "required_days": int}
          * {"min_health": float, "health_threshold": float}
          * {"harvest_reward": float, "min_total_harvest_reward": float}
    """
    # 1) Pass/fail tasks (works with your current task functions).
    if isinstance(task_result, bool):
        return 1.0 if task_result else 0.0

    # 2) Numeric score or numeric metric.
    if isinstance(task_result, (int, float)):
        # If caller already normalized, keep it; otherwise clamp.
        x = float(task_result)
        if 0.0 <= x <= 1.0:
            return x
        return max(0.0, min(1.0, x))

    # 3) Dict-based grading (optional richer task results).
    if isinstance(task_result, dict):
        if "passed" in task_result:
            passed = bool(task_result["passed"])
            return 1.0 if passed else 0.0

        if "score" in task_result:
            x = float(task_result["score"])
            return max(0.0, min(1.0, x))

        # Easy-like metric: days_alive / required_days
        if "days_alive" in task_result and "required_days" in task_result:
            days_alive = float(task_result["days_alive"])
            required_days = float(task_result["required_days"])
            if required_days <= 0:
                return 0.0
            return max(0.0, min(1.0, days_alive / required_days))

        # Medium-like metric: min_health / health_threshold
        if "min_health" in task_result and "health_threshold" in task_result:
            min_health = float(task_result["min_health"])
            threshold = float(task_result["health_threshold"])
            if threshold <= 0:
                return 0.0
            return max(0.0, min(1.0, min_health / threshold))

        # Hard-like metric: harvest_reward / min_total_harvest_reward
        if "harvest_reward" in task_result and "min_total_harvest_reward" in task_result:
            harvest_reward = float(task_result["harvest_reward"])
            target = float(task_result["min_total_harvest_reward"])
            if target <= 0:
                return 0.0
            return max(0.0, min(1.0, harvest_reward / target))

    # Unknown format => worst score.
    return 0.0


__all__ = ["grader"]

