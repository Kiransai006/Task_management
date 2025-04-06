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


@app.get("/getassignedusers")
async def GetAssignedUsers(request: Request):
    token = request.cookies.get("token")
    
    if not token:
        return JSONResponse(content={"message": "Login required"})
    
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token["user_id"]
    except Exception as e:
        return JSONResponse(content={"message": f"Error decoding token: {str(e)}"})
    
    taskBoardDB_ref =taskBoardDB.where("creator", "==", user_id).stream()
    # users = []
    

    for board in taskBoardDB_ref:
        board_data = board.to_dict()
        print(board_data)

    return JSONResponse(content=board_data)


@app.get('/')
def Login(request: Request):
    return templates.TemplateResponse('login.html',{'request': request})

@app.get('/register')
def Register(request: Request):
    return templates.TemplateResponse('register.html',{'request': request})


@app.get("/index")
async def index(request: Request):
    token = request.cookies.get("token")  

    if not token:
        return JSONResponse(content="Login required")
    return templates.TemplateResponse('index.html', {'request': request})


@app.get("/createtaskboard")
async def index(request: Request):
    token = request.cookies.get("token")  

    if not token:
        return JSONResponse(content="Login required")

    return templates.TemplateResponse('createtaskboard.html', {'request': request})

@app.get("/displayboard")
async def displayboard(request: Request):
    token = request.cookies.get("token")  

    if not token:
        return JSONResponse(content="Login required")

    return templates.TemplateResponse('task_boards.html', {'request': request})

@app.post("/createboardtask")
async def create_task_board(request: Request):
    token = request.cookies.get("token")
    
    req=await request.json()
    name=req.get('name')
    description=req.get('description')

    if not token:
        return JSONResponse(content={"message": "Login required"})
    
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
       
        user_id = decoded_token["user_id"]
        print('name',decoded_token,user_id)
    except Exception as e:
        return JSONResponse(content={"message": f"Error decoding token: {str(e)}"})
    
    task_board_data = {
        "name": name,
        "description": description,
        "creator": user_id,
    }
    
    taskBoardDB.add(task_board_data)
    
    return JSONResponse(content={"message": "Task board created successfully!"})


@app.get("/gettaskboards")
async def get_task_boards(request: Request):
    try:
        token = request.cookies.get("token")
    
        if not token:
            return JSONResponse(content={"message": "Login required"})
    
        try:
            # decoded_token = id_token.verify_firebase_token(token, requests.Request())
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id =decoded["user_id"]
            print(f"Decoded user_id: {user_id}")  
        except Exception as e:
            return JSONResponse(content={"message": f"Error decoding token: {str(e)}"})

        creator_boards = taskBoardDB.where("creator", "==", user_id).stream()
        member_boards = taskBoardDB.where("users", "array_contains", user_id).stream()

        boards = {}

        for board in creator_boards:
            board_data = board.to_dict()
            print(f"Creator board found: {board.id}, data: {board_data}") 
            boards[board.id] = {"id": board.id, **board_data}

        for board in member_boards:
            board_data = board.to_dict()
            if board.id not in boards:
                boards[board.id] = {"id": board.id, **board_data}

        return JSONResponse(content={"boards": list(boards.values()), "user_id": user_id})

    except Exception as e:
        return JSONResponse(content={"message": f"Error: {str(e)}"})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7000, reload=True)