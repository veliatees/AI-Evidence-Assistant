from fastapi import FastAPI

app= FastAPI(
    title= "AI Evidence Assistant",
    version= "0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/login")
def login_check():
    return {"status": "logged in"}