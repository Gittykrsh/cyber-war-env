from fastapi import FastAPI, HTTPException
from models import CyberAction
from server.cyber_env import CyberWarEnv

app = FastAPI(title="Cyber War OpenEnv")

# Global environment
env = CyberWarEnv()


# ROOT (HF health check friendly)
@app.get("/")
def home():
    return {
        "status": "healthy",
        "message": "Cyber War Env Running",
        "docs": "/docs"
    }


# EXTRA HEALTH CHECK (VERY IMPORTANT)
@app.get("/health")
def health():
    return {"status": "ok"}


# RESET API
@app.post("/reset")
def reset():
    try:
        return env.reset()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# STEP API
@app.post("/step")
def step(action: CyberAction):
    try:
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