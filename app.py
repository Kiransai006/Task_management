from fastapi import FastAPI, File, Form, HTTPException, Query, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import firestore
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import service_account
from starlette.middleware.sessions import SessionMiddleware 
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime
import asyncio
import jwt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="12345")

app.mount("/static", StaticFiles(directory="static"), name="static")


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "task-management-1a4b0-firebase-adminsdk-fbsvc-a3617b3362.json"
projectID = 'task-management-1a4b0'

credentials = service_account.Credentials.from_service_account_file("task-management-1a4b0-firebase-adminsdk-fbsvc-a3617b3362.json")

db = firestore.Client(credentials=credentials, project=projectID)
templates = Jinja2Templates(directory="templates")

taskBoardDB=db.collection("TaskBoards")
userDB=db.collection("users")
tasksDB=db.collection("tasks")


@app.get("/getusers")
async def get_users(request: Request):
    token = request.cookies.get("token")
    
    if not token:
        return JSONResponse(content={"message": "Login required"})
    
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token["user_id"]
    except Exception as e:
        return JSONResponse(content={"message": f"Error decoding token: {str(e)}"})
    
    users_ref = userDB.stream()
    users = []
    
    for user in users_ref:
        user_data = user.to_dict()
        users.append({"id": user.id, "email": user_data.get("email", "")})

    return JSONResponse(content=users)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7000, reload=True)