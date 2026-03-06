from fastapi import FastAPI

app = FastAPI(title="DisputeGuard AI")

@app.get("/")
def root():
    return {"status": "DisputeGuard AI backend running"}
