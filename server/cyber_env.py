import random
from typing import List

from models import CyberAction, CyberObservation, CyberState, Alert


class CyberWarEnv:

    def __init__(self):
        self.step_count = 0
        self.max_steps = 20
        self.last_reward = 0
        self.current_alerts = []

    # RESET
    def reset(self):
        self.step_count = 0
        self.last_reward = 0
        self.current_alerts = self._generate_alerts()

        return {
            "observation": self._get_observation(),
            "reward": 0,
            "done": False,
            "info": {}
        }

    # STEP FUNCTION
    def step(self, action: CyberAction):
        self.step_count += 1

        reward = self._calculate_reward(action)
        self.last_reward = reward

        # next alerts generate karo
        self.current_alerts = self._generate_alerts()

        done = self.step_count >= self.max_steps

        return {
            "observation": self._get_observation(),
            "reward": reward,
            "done": done,
            "info": {}
        }

    # OBSERVATION
    def _get_observation(self) -> CyberObservation:
        return CyberObservation(
            alerts=[Alert(type=a["type"], severity=a["severity"]) for a in self.current_alerts],
            system_load=random.randint(30, 90),
            threat_level=random.randint(1, 10)
        )

    # ALERT GENERATOR (ATTACK ENGINE)
    def _generate_alerts(self) -> List[dict]:
        alerts = []

        for _ in range(3):  # 3 alerts per step
            attack_type = random.choice(["ddos", "brute_force", "normal"])

            if attack_type == "ddos":
                alerts.append({
                    "type": "ddos",
                    "severity": random.randint(7, 10),
                    "is_attack": True
                })

            elif attack_type == "brute_force":
                alerts.append({
                    "type": "brute_force",
                    "severity": random.randint(5, 8),
                    "is_attack": True
                })

            else:
                alerts.append({
                    "type": "normal",
                    "severity": random.randint(1, 4),
                    "is_attack": False
                })

        return alerts

    # REWARD FUNCTION
    def _calculate_reward(self, action: CyberAction):
        reward = 0

        for alert in self.current_alerts:

            if alert["is_attack"]:
                if action.action_type in ["block_ip", "rate_limit"]:
                    reward += 2
                else:
                    reward -= 2

            else:  # normal traffic
                if action.action_type in ["block_ip", "rate_limit"]:
                    reward -= 3
                else:
                    reward += 1

        return reward

    # STATE (OPTIONAL)
    def state(self):
        return CyberState(
            step_count=self.step_count,
            last_reward=self.last_reward
        )