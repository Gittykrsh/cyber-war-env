from fastapi import FastAPI, HTTPException, Request
from models import CyberAction
from server.cyber_env import CyberWarEnv

app = FastAPI(title="Cyber War OpenEnv")

# Global environment
env = CyberWarEnv()


# ROOT (HF health check friendly)
@app.get("/")
def home():
    return {"status": "ok"}


# EXTRA HEALTH CHECK (VERY IMPORTANT)
@app.get("/health")
def health():
    return {"status": "ok"}


# RESET API
@app.post("/reset")
async def reset(request: Request):
    try:
        try:
            data = await request.json()
        except:
            data = {}

        task = data.get("task", "easy")

        if task not in ["easy", "medium", "hard"]:
            task = "easy"
        
        print(f"[RESET] task={task}")

        return env.reset(task)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# STEP API
@app.post("/step")
def step(action: CyberAction):
    try:
        if action.action_type not in ["block_ip", "rate_limit", "investigate"]:
            raise HTTPException(status_code=400, detail="Invalid action")

        print(f"[STEP] action={action.action_type}")

        return env.step(action)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# STATE API
@app.get("/state")
def state():
    try:
        return env.state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
def startup_event():
    print(" App started successfully")

# ENTRYPOINT (FIXED PORT)
def main():
    import uvicorn
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,   # FIXED
        reload=False
    )


# RUN
if __name__ == "__main__":
    print(" Starting Cyber War Env Server...")
    main()