import random
from typing import List

from models import CyberAction, CyberObservation, CyberState, Alert


class CyberWarEnv:

    def __init__(self):
        self.step_count = 0
        self.max_steps = 20
        self.last_reward = 0
        self.current_alerts = []

        self.current_task = "easy"

        # NEW: Attack progression (CORE UPGRADE)
        self.attack_stage = 0

        # NEW: Persistence
        self.blocked = False

    # RESET
    def reset(self, task="easy"):
        self.step_count = 0
        self.last_reward = 0
        self.current_task = task

        # reset progression
        self.attack_stage = 0
        self.blocked = False

        self.current_alerts = self._generate_alerts()

        return {
            "observation": self._get_observation(),
            "reward": 0,
            "done": False,
            "info": {
                "task": self.current_task
            }
        }

    # STEP FUNCTION
    def step(self, action: CyberAction):
        self.step_count += 1

        reward = 0
        obs = self._get_observation()

        # ATTACK PROGRESSION LOGIC (KEY DIFFERENTIATOR)

        if self.current_task == "hard":

            if action.action_type == "investigate" and self.attack_stage == 0:
                self.attack_stage = 1
                reward += 2

            elif action.action_type == "rate_limit" and self.attack_stage == 1:
                self.attack_stage = 2
                reward += 3

            elif action.action_type == "block_ip" and self.attack_stage == 2:
                self.attack_stage = 3
                self.blocked = True
                reward += 5

            else:
                reward -= 1  # wrong sequence penalty

        # BASE REWARD
        reward += self._calculate_reward(action, obs)

        # TASK GRADING
        if self.current_task == "easy":
            task_score = self._grade_easy(obs)
        elif self.current_task == "medium":
            task_score = self._grade_medium(obs)
        else:
            task_score = self._grade_hard(obs)

        # FINAL REWARD
        reward += task_score * 10

        self.last_reward = reward

        # SMART ALERT EVOLUTION (NO RANDOM RESET)
        self.current_alerts = self._generate_alerts()

        # DONE CONDITIONS
        done = False

        if self.current_task == "hard":
            if self.attack_stage >= 3:
                done = True

        if self.step_count >= self.max_steps:
            done = True

        return {
            "observation": self._get_observation(),
            "reward": reward,
            "done": done,
            "info": {
                "task": self.current_task,
                "task_score": task_score,
                "attack_stage": self.attack_stage
            }
        }

    # OBSERVATION
    def _get_observation(self) -> CyberObservation:
        return CyberObservation(
            alerts=[Alert(type=a["type"], severity=a["severity"]) for a in self.current_alerts],
            system_load=random.randint(30, 90),
            threat_level=random.randint(1, 10)
        )

    # ALERT GENERATOR (NOW STATE-DEPENDENT)
    def _generate_alerts(self) -> List[dict]:
        alerts = []

        if self.current_task == "easy":
            for _ in range(2):
                alerts.append({
                    "type": "brute_force",
                    "severity": random.randint(6, 8),
                    "is_attack": True
                })

        elif self.current_task == "medium":
            for _ in range(3):
                attack_type = random.choice(["ddos", "normal"])
                alerts.append({
                    "type": attack_type,
                    "severity": random.randint(4, 9),
                    "is_attack": attack_type != "normal"
                })

        elif self.current_task == "hard":
            # PROGRESSION BASED ALERTS
            if self.attack_stage == 0:
                alerts.append({"type": "scan_activity", "severity": 3, "is_attack": True})
            elif self.attack_stage == 1:
                alerts.append({"type": "brute_force", "severity": 6, "is_attack": True})
            elif self.attack_stage == 2:
                alerts.append({"type": "ddos", "severity": 9, "is_attack": True})
            else:
                alerts.append({"type": "normal", "severity": 2, "is_attack": False})

        return alerts

    # BASE REWARD
    def _calculate_reward(self, action: CyberAction, obs: CyberObservation):
        reward = 0

        for alert in self.current_alerts:

            if alert["is_attack"]:
                if action.action_type in ["block_ip", "rate_limit"]:
                    reward += 4
                elif action.action_type == "investigate":
                    reward += 1
                else:
                    reward -= 3

            else:
                if action.action_type in ["block_ip", "rate_limit"]:
                    reward -= 4
                else:
                    reward += 1

        # shaping
        reward += (10 - obs.threat_level) * 0.5

        if obs.system_load < 50:
            reward += 3
        elif obs.system_load < 70:
            reward += 1
        else:
            reward -= 3

        if action.action_type in ["block_ip", "rate_limit"] and len(self.current_alerts) == 0:
            reward -= 5

        if action.action_type == "investigate":
            reward += 0.5

        return reward

    # EASY TASK (IMPROVED)
    def _grade_easy(self, obs: CyberObservation):
        brute_force = [a for a in obs.alerts if a.type == "brute_force"]
        handled = 1 if len(brute_force) == 0 else 0
        return handled * 1.0

    # MEDIUM TASK
    def _grade_medium(self, obs: CyberObservation):
        ddos = [a for a in obs.alerts if a.type == "ddos"]

        score = 0.0

        if len(ddos) == 0:
            score += 0.5

        if obs.system_load < 50:
            score += 0.5

        return score

    # HARD TASK (COMPLETELY FIXED)
    def _grade_hard(self, obs: CyberObservation):
        score = 0

        if self.attack_stage >= 1:
            score += 0.3
        if self.attack_stage >= 2:
            score += 0.3
        if self.attack_stage >= 3:
            score += 0.4

        return score

    # STATE
    def state(self):
        return CyberState(
            step_count=self.step_count,
            last_reward=self.last_reward
        )