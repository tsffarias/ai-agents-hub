from fastapi import FastAPI
import socket

from routes.routes_recruter import router as recruter_router


app = FastAPI()

@app.get("/whoami")
async def whoami():
    return {"hostname": socket.gethostname()}

app.include_router(recruter_router)