from fastapi import FastAPI

app = FastAPI()

@app.post("/analyze")
def analyze_text():
    return {"status": "okay"}