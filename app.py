from fastapi import FastAPI, File, Form, HTTPException, Query, Response, Request
from fastapi.responses import JSONResponse
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
    
    # Fetch all users from Firestore
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
    
    # Fetch all users from Firestore
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
    # await asyncio.sleep(25)
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

@app.get("/taskboard/{board_id}")
async def view_task_board(board_id: str, request: Request):
    token = request.cookies.get("token")
    
    if not token:
        return JSONResponse(content={"message": "Login required"})
    
    try:
        decoded_token = id_token.verify_firebase_token(token, requests.Request())
        user_id = decoded_token["user_id"]
    except Exception as e:
        return JSONResponse(content={"message": f"Error decoding token: {str(e)}"})

    # Fetch the task board details by ID
    task_board_ref = taskBoardDB.document(board_id)
    task_board = task_board_ref.get()
    
    if not task_board.exists:
        return JSONResponse(content={"message": "Task board not found"})
    
    board_data = task_board.to_dict()

    tasks_ref = tasksDB.where("taskboard_id", "==", board_id)
    tasks = tasks_ref.stream()

    task_list = []
    isCreator=board_data['creator']==user_id


    taskDetails={}   
    completedTasks=0
    activeTasks=0
    for task in tasks:
        task_data = task.to_dict()
        if task_data["completion"]=="Completed":
          completedTasks+=1
        else: 
           activeTasks+=1 

        task_list.append({
            "name": task_data["name"],
            "completion": task_data["completion"],
            "dueDate": task_data["dueDate"],
            "id": task.id,
            "completedAt": task_data["completedAt"],
        })
    
    taskDetails={
        'totalTasks':len(task_list),
        'completedTasks':completedTasks,
        'activeTasks':activeTasks
    }    

    print(board_data,'board data')
    return templates.TemplateResponse('taskBoardDetails.html', {
        'request': request, 
        'board': board_data, 
        'tasks': task_list,
        'board_id':board_id,
        'creator':isCreator,
        'taskDetails':taskDetails
    })


@app.post("/createtask")
async def create_task(request: Request):
    token = request.cookies.get("token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Login required")
    
    req = await request.json()
    task_name = req.get('name')
    completion = req.get('completion')
    taskboard_id = req.get('taskboard_id')  
    due_date = req.get('due_date', None)  
    
    print('assinged',task_name,taskboard_id)

    if not task_name or not completion or not taskboard_id:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    task_data = {
        "name": task_name,
        "completion": completion,
        "taskboard_id": taskboard_id,
        "dueDate": due_date,
        "completedAt": "",
    }
    task_ref = tasksDB.add(task_data)
    
    return {"message": "Task created successfully!"}

@app.post("/remove/{board_id}")
async def RemoveUserFromBoard(board_id: str, request: Request):
    token = request.cookies.get("token")
    if not token:
        return JSONResponse(content={"message": "Login required"})

    try:
        decoded_token = id_token.verify_firebase_token(token, requests.Request())
        current_user_id = decoded_token["user_id"]
    except Exception as e:
        return JSONResponse(content={"message": f"Error decoding token: {str(e)}"})

    task_board_ref = taskBoardDB.document(board_id)
    task_board = task_board_ref.get()

   
    if not task_board.exists:
        return JSONResponse(content={"message": "Task board not found"})

    task_board_data = task_board.to_dict()

    if task_board_data["creator"] != current_user_id:
        return JSONResponse(content={"message": "You are not allowed to remove users from this board"})

    req = await request.json()
    user_id = req.get("user_id")
    
    if not user_id:
        return JSONResponse(content={"message": "User ID is required"})

    if user_id not in task_board_data.get("users", []):
        return JSONResponse(content={"message": "User is not part of this board"})


    updated_users = [u for u in task_board_data["users"] if u != user_id]
    task_board_ref.update({"users": updated_users})

    return JSONResponse(content={"message": "User removed successfully from task board"})


@app.post("/adduser/{board_id}")
async def add_user_to_board(board_id: str, request: Request):
    token = request.cookies.get("token")
    if not token:
        return JSONResponse(content={"message": "Login required"})

    try:
        decoded_token = id_token.verify_firebase_token(token, requests.Request())
        current_user_id = decoded_token["user_id"]
    except Exception as e:
        return JSONResponse(content={"message": f"Error decoding token: {str(e)}"})

    task_board_ref = taskBoardDB.document(board_id)
    task_board = task_board_ref.get()

    if not task_board.exists:
        return JSONResponse(content={"message": "Task board not found"})

    task_board_data = task_board.to_dict()

    if task_board_data["creator"] != current_user_id:
        return JSONResponse(content={"message": "You are not allowed to add users to this board"})

    req = await request.json()
    new_user_id = req.get("user_id")

    if not new_user_id:
        return JSONResponse(content={"message": "User ID is required"})

    if new_user_id in task_board_data.get("users", []):
        return JSONResponse(content={"message": "User already added"})

    task_board_ref.update({
        "users": firestore.ArrayUnion([new_user_id])
    })

    return JSONResponse(content={"message": "User added successfully"})

@app.post("/update-task/{task_id}")
async def UpdateTask(task_id: str, task_data: dict):
    try:
        task_ref = tasksDB.document(task_id)
        
        task = task_ref.get()
        
        if not task.exists:
            return JSONResponse(content= {"success":False,"message":f"Task with ID {task_id} not found"})
        
        task_ref.update({
            "completion": task_data.get("completion", "Pending"),
            "completedAt":firestore.SERVER_TIMESTAMP
        })

        return JSONResponse(content= {"success":True,"message":"Task updated successfully"})

    except Exception as e:
        return JSONResponse(content= {"success":False,"message":str(e)})
    
@app.delete("/delete-task/{task_id}")
async def delete_task(task_id: str):
    try:
        task_ref = tasksDB.document(task_id)
        task = task_ref.get()

        if not task.exists:
            return JSONResponse(content={"success": False, "message": f"Task with ID {task_id} not found"}, status_code=404)

        task_ref.delete()
        return JSONResponse(content={"success": True, "message": "Task deleted successfully"})

    except Exception as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)

@app.post("/update-task/{task_id}")
async def EditTask(task_id: str, request: Request):
    try:
        task_data = await request.json() 

        task_ref = tasksDB.document(task_id)
        task = task_ref.get()

        if not task.exists:
            return JSONResponse({"success": False, "message": "Task not found"})

        update_data = {key: value for key, value in task_data.items() if value is not None}

        if "completion" in update_data and update_data["completion"] == "Completed":
            update_data["completedAt"] = datetime.now().isoformat()

        task_ref.update(update_data)

        return JSONResponse({"success": True, "message": "Task updated successfully"})

    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)})

@app.post("/rename-board/{board_id}")
async def RenameBoard(board_id: str, request: Request):
    token = request.cookies.get("token")
    if not token:
        return JSONResponse(content={"message": "Login required"})

    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token["user_id"]
    except Exception as e:
        return JSONResponse(content={"message": f"Error decoding token: {str(e)}"})

    task_board_ref = taskBoardDB.document(board_id)
    task_board = task_board_ref.get()
    
    if not task_board.exists:
        return JSONResponse(content={"message": "Task board not found"})
    
    board_data = task_board.to_dict()

    if board_data["creator"] != user_id:
        return JSONResponse(content={"message": "You are not the owner of this board"})
    
    requestName = await request.json()
    new_name=requestName.get("name")
    if not new_name:
        return JSONResponse(content={"message": "New name is required"})

    task_board_ref.update({"name": new_name})

    return JSONResponse(content={"message": "Board renamed successfully"})

@app.post("/delete-board/{board_id}")
async def DeleteBoard(board_id: str, request: Request):
    token = request.cookies.get("token")
    if not token:
        return JSONResponse(content={"message": "Login required"})

    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token["user_id"]

    except Exception as e:
        return JSONResponse(content={"success":False,"message": f"Error decoding token: {str(e)}"})

    task_board_ref = taskBoardDB.document(board_id)
    task_board = task_board_ref.get()
    

    
    if not task_board.exists:
        return JSONResponse(content={"success":False,"message": "Task board not found"})

    board_data = task_board.to_dict()
    print(board_data,'task')
    if board_data["creator"] != user_id:
        return JSONResponse(content={"success":False,"message": "You are not the owner of this board"})
        
    tasks_ref = tasksDB.where("taskboard_id", "==", board_id)
    tasks = tasks_ref.stream()
    tasks_list = list(tasks)
    
    length=len(tasks_list)
    if(length>0):
          return JSONResponse(content={"success": False, "message": "Unable to delete as tasks are present in board!"})
    
    task_board_ref.delete()

    return JSONResponse(content={"success": True, "message": "Board deleted successfully"})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7000, reload=True)