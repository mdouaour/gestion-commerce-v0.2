from fastapi import FastAPI

app = FastAPI(title="Gestion Commerce API")

@app.get("/")
async def root():
    return {"message": "Welcome to Gestion Commerce POS and Parcel system"}
