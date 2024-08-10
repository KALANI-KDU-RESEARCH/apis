from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from pymongo.errors import ConnectionFailure
import logging
from typing import List
import bcrypt
from utils.index import generate_jwt_token, env
from models.index import predict, chat, getChats, deleteChats, updateInterests, createPostForEntrepreneur, getPostsForEntrepreneurById, editPostForEntrepreneur, deletePostForEntrepreneur

app = FastAPI()
app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False}) #Enable Swagger UI
# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up CORS (Cross-Origin Resource Sharing) to allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # allow these HTTP methods
    allow_headers=["*"],  # allow all headers
)

#=============================================== DB Configurations =========================================
# MongoDB Atlas connection string
MONGODB_URI = env('MONGODB_URI') + '=true&w=majority&appName=Cluster0'

# Connect to MongoDB Atlas
try:
    client = MongoClient(MONGODB_URI)
    # Test if the connection is successful
    client.admin.command('ismaster')
    logging.info("MongoDB connection successful")
except ConnectionFailure as e:
    logging.error("MongoDB connection failed: %s", e)
    raise e


# Select database and collection
db = client["research-kalani"]
users_collection = db["users"]

# Define a Pydantic model for the user data
class User(BaseModel):
    email: str
    password: str
    age: int
    experience: int
    interests: List[str]
    type: str

#============================================================================================================

@app.get("/")
async def read_root():
    return {"message": "Hello, Welcome to our server !!!"}

# Registration route
@app.post("/register/")
async def register(user: User):
        # Check if the username already exists
        existing_user = users_collection.find_one({"email": user.email})
        # Hash the password
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        if existing_user:
            logging.info(f"Username {user.email} already exists")
            raise HTTPException(status_code=400, detail="Email already exists")

        # Insert the new user into the database
        user_data = {"email": user.email, "password": hashed_password,  "age": user.age,
            "experience": user.experience,
            "interests": user.interests, "type": user.type}
        result = users_collection.insert_one(user_data)

        logging.info(f"User {user.email} registered successfully with ID: {result.inserted_id}")
        return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

# Define a Pydantic model for the login request
class LoginRequest(BaseModel):
    email: str
    password: str

# Login route
@app.post("/login/")
async def login(login_request: LoginRequest):
        # Find the user in the database
        user = users_collection.find_one({"email": login_request.email})
        print(user)
        if user:
            user['_id'] = str(user['_id'])
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify the password
        if not bcrypt.checkpw(login_request.password.encode('utf-8'), user['password']):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Generate JWT token
        jwt_token = generate_jwt_token(user)

        # If the username and password are correct, return a success message along with the JWT token
        return {"message": "Login successful", "token": jwt_token, "user": user}


class Query(BaseModel):
    name: str

# Prediction route
@app.post("/predict/")
async def prediction(query: Query):
    return predict(query.name)

class Chat(BaseModel):
     userId: str
     userName: str
     text: str

# Chat route
@app.post("/chat/")
async def chatBot(msg: Chat):
    return chat(msg, db)


# Chat route
@app.get("/chat/{userId}")
async def getChatsByUserId(userId):
    return getChats(userId, db)

# Chat route
@app.delete("/chat/{userId}")
async def deleteChatsByUserId(userId):
    return deleteChats(userId, db)

class InterestsPayload(BaseModel):
    interests: list[str]
@app.patch("/profile/{userId}")
async def updateUserInterests(interests:InterestsPayload, userId):
    return updateInterests(interests, userId, db)

class PostPayload(BaseModel):
    title: str
    desc: str
    cat: list[str]
    img: str
    userId: str
@app.post("/post")
async def createPost(payload:PostPayload):
    return createPostForEntrepreneur(payload, db)

@app.get("/getPosts/{userId}")
async def getPostsById(userId):
    return getPostsForEntrepreneurById(userId, db)

@app.put("/editPost/{postId}")
async def editPost(payload: PostPayload, postId):
    return editPostForEntrepreneur(payload, postId, db)

@app.delete("/deletePost/{postId}")
async def deletePost(postId):
    return deletePostForEntrepreneur(postId, db)