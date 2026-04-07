from fastapi import FastAPI
from models import CyberAction
from server.cyber_env import CyberWarEnv

app = FastAPI()

# global env instance
env = CyberWarEnv()


# optional (root fix - no more 404)
@app.get("/")
def home():
    return {
        "message": "Cyber War Env Running",
        "docs": "/docs"
    }


# RESET API
@app.post("/reset")
def reset():
    return env.reset()


# STEP API
@app.post("/step")
def step(action: CyberAction):
    return env.step(action)


# STATE API
@app.get("/state")
def state():
    return env.state()


# REQUIRED FOR OPENENV
def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)


# IMPORTANT ENTRYPOINT
if __name__ == "__main__":
    main()