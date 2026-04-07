import sys
sys.path.append('e:\\')  # Adjust the path if 'server' is in a different directory
from server.cyber_env import CyberWarEnv
from models import CyberAction
import random

# env create karo
env = CyberWarEnv()

# reset
response = env.reset()
print("Initial State:", response)

done = False

while not done:
    # random action
    action = CyberAction(
        action_type=random.choice(["block_ip", "ignore", "rate_limit", "investigate"])
    )

    response = env.step(action)

    print("\nAction:", action.action_type)
    print("Observation:", response["observation"])
    print("Reward:", response["reward"])

    done = response["done"]