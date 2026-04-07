import requests
import time

BASE_URL = "https://shakyas1mha-cyber-war-env.hf.space"


def reset_env():
    res = requests.post(f"{BASE_URL}/reset")
    print("RAW RESPONSE:", res.text)
    return res.json()


def step_env(action):
    res = requests.post(f"{BASE_URL}/step", json=action)
    return res.json()


# SIMPLE RULE-BASED AGENT
def choose_action(observation):
    alerts = observation["alerts"]

    for alert in alerts:
        if alert["type"] == "ddos":
            return {"action_type": "rate_limit"}

        elif alert["type"] == "brute_force":
            return {"action_type": "block_ip"}

    return {"action_type": "investigate"}


def run_episode():
    data = reset_env()

    total_reward = 0
    steps = 0

    while True:
        obs = data["observation"]

        action = choose_action(obs)

        data = step_env(action)

        total_reward += data["reward"]
        steps += 1

        if data["done"]:
            break

    return total_reward


# EVALUATE ALL TASKS
def evaluate():
    scores = []

    for i in range(5):  # multiple runs
        score = run_episode()
        scores.append(score)
        print(f"Run {i+1}: {score}")

    avg_score = sum(scores) / len(scores)

    print("\n FINAL SCORE:", avg_score)


if __name__ == "__main__":
    evaluate()