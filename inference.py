try:
    from openai import OpenAI
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI
import os
try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "requests"])
    import requests
from typing import List

# ENV VARIABLES (MANDATORY)
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("HF_TOKEN") or os.getenv("API_KEY")
)
TASK_NAME = "cyber-war"
BENCHMARK = "cyber-war-env"

MAX_STEPS = 10


# ---------------- LOG FUNCTIONS ---------------- #

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error):
    err = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ---------------- ENV CALLS ---------------- #

def reset_env():
    res = requests.post(f"{API_BASE_URL}/reset")
    return res.json()


def step_env(action: str):
    res = requests.post(
        f"{API_BASE_URL}/step",
        json={"action_type": action}
    )
    return res.json()


# ---------------- SIMPLE AGENT ---------------- #

def choose_action(obs):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity agent. Choose one action: block_ip, rate_limit, investigate, ignore."
                },
                {
                    "role": "user",
                    "content": str(obs)
                }
            ],
            temperature=0
        )

        action = response.choices[0].message.content.strip()

        if action not in ["block_ip", "rate_limit", "investigate", "ignore"]:
            return "investigate"

        return action

    except Exception:
        return "investigate"


# ---------------- MAIN ---------------- #

def run():
    all_rewards = []
    steps_taken = 0
    success = False
    final_score = 0.0

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        episode_scores = []

        # Run at least 3 tasks (episodes)
        for episode in range(3):

            rewards = []
            state = reset_env()

            for step in range(1, MAX_STEPS + 1):

                action = choose_action(state)

                try:
                    result = step_env(action)

                    reward = float(result.get("reward", 0.0))
                    done = bool(result.get("done", False))
                    error = None

                except Exception as e:
                    reward = 0.0
                    done = True
                    error = str(e)

                rewards.append(reward)
                all_rewards.append(reward)
                steps_taken += 1

                log_step(step, action, reward, done, error)

                state = result if not error else {}

                if done:
                    break

            # Per-task (episode) scoring → REQUIRED by Meta
            ep_score = sum(rewards) / 10.0

            # force score strictly in (0,1)
            if ep_score >= 1.0:
                ep_score = 0.99
            elif ep_score <= 0.0:
                ep_score = 0.01

            episode_scores.append(ep_score)

        # Final score = average of all tasks
        if episode_scores:
            final_score = sum(episode_scores) / len(episode_scores)

        success = final_score > 0.3

    except Exception as e:
        print("Fatal Error:", str(e))

    finally:
        log_end(success, steps_taken, final_score, all_rewards)


if __name__ == "__main__":
    run()