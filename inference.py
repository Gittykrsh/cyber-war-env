import os
try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "requests"])
    import requests
from typing import List

# ENV VARIABLES (MANDATORY)
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://shakyas1mha-cyber-war-env.hf.space"
)
MODEL_NAME = os.getenv("MODEL_NAME", "dummy-model")
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
    """
    Simple rule-based agent
    (later LLM se replace kar sakte hain)
    """
    text = str(obs).lower()

    if "alert" in text:
        return "block_ip"
    elif "suspicious" in text:
        return "scan"
    else:
        return "monitor"


# ---------------- MAIN ---------------- #

def run():
    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
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
            steps_taken = step

            log_step(step, action, reward, done, error)

            state = result if not error else {}

            if done:
                break

        # -------- SCORE -------- #
        total_reward = sum(rewards)

        # normalize to [0,1]
        score = max(0.0, min(1.0, total_reward / 10.0))

        success = score > 0.3

    finally:
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    run()