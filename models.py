from pydantic import BaseModel
from typing import List


# Single alert structure
class Alert(BaseModel):
    type: str        # "ddos", "normal", etc.
    severity: int    # 1 - 10


# Agent ka action
class CyberAction(BaseModel):
    action_type: str   # "block_ip", "ignore", "rate_limit", "investigate"


# Agent ko kya dikhega (VISIBLE STATE)
class CyberObservation(BaseModel):
    alerts: List[Alert]
    system_load: int
    threat_level: int


# Internal state (OPTIONAL but useful)
class CyberState(BaseModel):
    step_count: int
    last_reward: float