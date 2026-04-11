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
    api_key=os.getenv("OPENAI_API_KEY")
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

def reset_env(task):
    res = requests.post(
        f"{API_BASE_URL}/reset",
        json={"task": task}
    )
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
        observation = obs.get("observation", {})
        alerts = observation.get("alerts", [])

        if not alerts:
            return "investigate"

        # Extract structured info
        has_scan = False
        has_brute = False
        has_ddos = False
        has_normal = False

        max_severity = 0

        for alert in alerts:
            t = alert.get("type", "")
            sev = alert.get("severity", 0)

            max_severity = max(max_severity, sev)

            if t == "scan_activity":
                has_scan = True
            elif t == "brute_force":
                has_brute = True
            elif t == "ddos":
                has_ddos = True
            elif t == "normal":
                has_normal = True

        # =========================
        # HARD TASK (STRICT SEQUENCE)
        # =========================
        if has_scan:
            return "investigate"

        if has_brute:
            return "rate_limit"

        if has_ddos:
            return "block_ip"

        # =========================
        # MEDIUM TASK (BALANCED LOGIC)
        # =========================
        # avoid over-blocking normal traffic

        if has_ddos:
            return "block_ip"

        if has_brute:
            return "rate_limit"

        if has_normal:
            return "investigate"   # KEY FIX

        # =========================
        # SEVERITY-BASED FALLBACK
        # =========================
        if max_severity >= 8:
            return "block_ip"
        elif max_severity >= 5:
            return "rate_limit"

        # =========================
        # SAFE DEFAULT
        # =========================
        return "investigate"

    except Exception:
        return "investigate"


# ---------------- MAIN ---------------- #

def run():

    TASKS = ["easy", "medium", "hard"]

    total_rewards = []
    total_steps = 0
    final_scores = []

    for task_name in TASKS:

        rewards = []
        steps_taken = 0
        success = False
        score = 0.0

        # IMPORTANT: separate START per task
        log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

        try:
            state = reset_env(task_name)

            for step in range(1, MAX_STEPS + 1):

                action = choose_action(state)

                try:
                    result = step_env(action)
                    raw_reward = float(result.get("reward", 0.0))

                    # normalize (assume max ~20)
                    reward = max(0.0, min(raw_reward / 20.0, 1.0))
                    done = bool(result.get("done", False))
                    error = None

                except Exception as e:
                    reward = 0.0
                    done = True
                    error = str(e)

                rewards.append(reward)
                total_rewards.append(reward)

                steps_taken += 1
                total_steps += 1

                log_step(step, action, reward, done, error)

                state = result if not error else {}

                if done:
                    break

            # score per task
            score = sum(rewards) / len(rewards)

            # DO NOT clamp aggressively
            score = max(0.0, min(score, 1.0))



            attack_stage = result.get("info", {}).get("attack_stage", 0)

            if task_name == "hard":
                success = attack_stage >= 3
            elif task_name == "medium":
                success = score > 0.25   # slightly relaxed
            else:
                success = score > 0.3

            final_scores.append(score)

        finally:
            # IMPORTANT: separate END per task
            log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    run()