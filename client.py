from openenv import EnvClient
from models import CyberAction


class CyberWarEnvClient(EnvClient):

    def reset(self):
        return self._post("/reset")

    def step(self, action: CyberAction):
        return self._post("/step", json=action.dict())

    def state(self):
        return self._get("/state")