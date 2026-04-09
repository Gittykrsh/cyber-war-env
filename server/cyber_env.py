import random
from typing import List

from models import CyberAction, CyberObservation, CyberState, Alert


class CyberWarEnv:

    def __init__(self):
        self.step_count = 0
        self.max_steps = 20
        self.last_reward = 0
        self.current_alerts = []

        # NEW
        self.current_task = "easy"

    # RESET
    def reset(self, task="easy"):
        self.step_count = 0
        self.last_reward = 0

        # RANDOM TASK
        self.current_task = task

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

        obs = self._get_observation()

        base_reward = self._calculate_reward(action, obs)

        # TASK GRADING
        if self.current_task == "easy":
            task_score = self._grade_easy(obs)
        elif self.current_task == "medium":
            task_score = self._grade_medium(obs)
        else:
            task_score = self._grade_hard(obs)

        # FINAL REWARD (base + task)
        reward = base_reward + (task_score * 10)

        self.last_reward = reward

        # next alerts
        self.current_alerts = self._generate_alerts()

        done = self.step_count >= self.max_steps

        return {
            "observation": self._get_observation(),
            "reward": reward,
            "done": done,
            "info": {
                "task": self.current_task,
                "task_score": task_score
            }
        }

    # OBSERVATION
    def _get_observation(self) -> CyberObservation:
        return CyberObservation(
            alerts=[Alert(type=a["type"], severity=a["severity"]) for a in self.current_alerts],
            system_load=random.randint(30, 90),
            threat_level=random.randint(1, 10)
        )

    # ALERT GENERATOR
    def _generate_alerts(self) -> List[dict]:
        alerts = []

        if self.current_task == "easy":
            # simple attacks
            for _ in range(2):
                alerts.append({
                    "type": "brute_force",
                    "severity": random.randint(6, 8),
                    "is_attack": True
                })

        elif self.current_task == "medium":
            # mixed traffic
            for _ in range(3):
                attack_type = random.choice(["ddos", "normal"])
                alerts.append({
                    "type": attack_type,
                    "severity": random.randint(4, 9),
                    "is_attack": attack_type != "normal"
                })

        elif self.current_task == "hard":
            # complex scenario
            for _ in range(5):
                attack_type = random.choice(["ddos", "brute_force", "normal"])
                alerts.append({
                    "type": attack_type,
                    "severity": random.randint(3, 10),
                    "is_attack": attack_type != "normal"
                })

        return alerts

    # BASE REWARD
    def _calculate_reward(self, action: CyberAction, obs: CyberObservation):
        reward = 0

        # 1. Attack handling reward
        for alert in self.current_alerts:

            if alert["is_attack"]:
                if action.action_type in ["block_ip", "rate_limit"]:
                    reward += 3   # correct mitigation
                elif action.action_type == "investigate":
                    reward += 1   # partial good
                else:
                    reward -= 3   # wrong

            else:  # normal traffic
                if action.action_type in ["block_ip", "rate_limit"]:
                    reward -= 4   # false positive (bad)
                else:
                    reward += 1   # correct ignore

        # 2. Threat level shaping
        reward += (10 - obs.threat_level) * 0.5

        # 3. System load shaping
        if obs.system_load < 50:
            reward += 3
        elif obs.system_load < 70:
            reward += 1
        else:
            reward -= 3

        # 4. Over-action penalty (spamming)
        if action.action_type in ["block_ip", "rate_limit"] and len(self.current_alerts) == 0:
            reward -= 5

        # 5. Encourage investigation
        if action.action_type == "investigate":
            reward += 0.5

        return reward

    # EASY TASK
    def _grade_easy(self, obs: CyberObservation):
        brute_force = [a for a in obs.alerts if a.type == "brute_force"]

        return 1.0 if len(brute_force) == 0 else 0.0

    # MEDIUM TASK
    def _grade_medium(self, obs: CyberObservation):
        ddos = [a for a in obs.alerts if a.type == "ddos"]

        score = 0.0

        if len(ddos) == 0:
            score += 0.5

        if obs.system_load < 50:
            score += 0.5

        return score

    # HARD TASK
    def _grade_hard(self, obs: CyberObservation):
        score = 1.0

        if obs.threat_level > 5:
            score -= 0.4

        if obs.system_load > 70:
            score -= 0.3

        return max(0.0, score)

    # STATE
    def state(self):
        return CyberState(
            step_count=self.step_count,
            last_reward=self.last_reward
        )