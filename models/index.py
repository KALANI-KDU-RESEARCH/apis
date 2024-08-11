import google.generativeai as genai
from IPython.display import Markdown
from utils.index import env
import requests
from fastapi import HTTPException
from bson import ObjectId
from utils.index import calculate_impression_rate
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import EmailStr
from jinja2 import Template

#THIS IS BASED ON GOOGLE LLM's
def predict(query):
    try:
        def to_markdown(text):
            return text

        genai.configure(api_key=env("API_KEY"))

        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)

        model = genai.GenerativeModel(env('AI_MODEL'))

        response = model.generate_content(query)

        print(response.text)

        return to_markdown(response.text)
    except:
         raise HTTPException(status_code=500, detail="Internal Server Error")

def chat(prompt, db):
    try:
        chat_collection = db["chats"]
   
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        payload = {
            "prompt": {
            "text": f"My name is {prompt.userName}. I'm a micro Entrepreneur. You are my assistant. Please answer this question '{prompt.text}'. It's best to respond to my message. Try to act assistant and casual rather than being very formal."
            }
        }

        response = requests.post(env('CHAT_MODEL') + '=AIzaSyD4z63UDBeKGjktRqd_N_SOEmFifQhJCm4',json=payload)
        response = response.json()

        chat_data = {"userId": prompt.userId, "user": prompt.text,  "assistant": response["candidates"][0]["output"]}
        chat_collection.insert_one(chat_data)
        
        return response["candidates"][0]["output"]
    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

def getChats(userId, db):
    try:
        chat_collection = db["chats"]
        chats = chat_collection.find({"userId": userId})
        chats = list(chats)
        for chat in chats:
            chat["_id"] = str(chat["_id"])
        return chats

    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

def deleteChats(userId, db):
    try:
        chat_collection = db["chats"]
        chat_collection.delete_many({"userId": userId})
        return {"mesage": "Chats Deleted Successfully"}

    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def updateInterests(payload, userId, db):
    try:
        users_collection = db["users"]
        users_collection.update_one(
            {"_id": ObjectId(userId)},  
            {"$set": {"interests": payload.interests, "age": payload.age, "experience": payload.experience}}
        )
        return {"mesage": "Interests Updated Successfully"}
    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

def createPostForEntrepreneur(payload, db):
    try:
        posts_collection = db["posts"]
        posts_data = {"userId": payload.userId, "title": payload.title,  "desc": payload.desc, "cat": payload.cat, "img": payload.img}
        posts_collection.insert_one(posts_data)
        return {"mesage": "Post Created Successfully"}
    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def getPostsForEntrepreneurById(userId, db):
    try:
        posts_collection = db["posts"]
        posts = posts_collection.find({"userId": userId}).sort({ "_id": -1 })
        posts = list(posts)
        for post in posts:
            post["_id"] = str(post["_id"])
        return posts
    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def editPostForEntrepreneur(payload, postId, db):
    try:
        posts_collection = db["posts"]
        posts_collection.update_one(
            {"_id": ObjectId(postId)},  
            {"$set": {"title": payload.title,  "desc": payload.desc, "cat": payload.cat, "img": payload.img }}
        )
        return {"message": "Post Updated Successfully"}
    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def deletePostForEntrepreneur(postId, db):
    try:
        posts_collection = db["posts"]
        posts_collection.delete_one(
            {"_id": ObjectId(postId)}
        )
        return {"message": "Post Deleted Successfully"}
    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def getAllPostsForInvester(db):
    try:
        posts_collection = db["posts"]
        posts = posts_collection.find().sort({ "_id": -1 })
        posts = list(posts)
        users_collection = db["users"]
        users = users_collection.find()
        users = list(users)
        users_dict = {str(user["_id"]): user for user in users}
        for post in posts:
            post["_id"] = str(post["_id"])
            user_id = str(post["userId"])
            if user_id in users_dict:
                post["impressionRate"] = users_dict[user_id].get("impression-rate", None)
            else:
                post["impressionRate"] = 0
        return posts
    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def calculate_impression_rate_for_user(payload, userId, db):
    try:
        global investors
        e_map_i_collection = db["e_map_i"]
        xx = e_map_i_collection.find({"_id": ObjectId(userId)})
        xx = list(xx)
        if(len(xx)):
            for x in xx:
                x["_id"] = str(x["_id"])
            investors = len(xx)
        else: investors = 0
        result = calculate_impression_rate(investors, payload.interests_count, payload.age, payload.experience)
        print(result)
        users_collection = db["users"]
        users_collection.update_one(
            {"_id": ObjectId(userId)},  
            {"$set": {"impression-rate": result}}
        )
        return {"impression-rate": result}
    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def markAsNotInterested(postId, userId, db):
    try:
        posts_collection = db["posts"]
        post = posts_collection.find_one({"_id": ObjectId(postId)})
        notInterested = list(post.get("not-interested", []))
        notInterested.append(userId)
        posts_collection.update_one(
            {"_id": ObjectId(postId)},
            {"$set": {"not-interested": notInterested}}
        )
        return {"message": "Marked As Not Interested"}
    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def send_email(email, investorId, eId, pId, db):
    try:
        sender_email = "codex.dev.m1@gmail.com"
        sender_password = "ijihiuyxreexlirh"
        subject= "Interest in Your Project"
        
        with open("email-templates/investor-send-email.html", "r") as file:
            template = Template(file.read())
            html_content = template.render(subject=subject, email=email.email, title=email.title)
            
        users_collection = db["users"]
        user = users_collection.find_one({"_id": ObjectId(eId)})
        
        e_map_i_collection = db["e_map_i"]
        e_map_i_collection.insert_one({"iId": investorId, "eId": eId})
        
        posts_collection = db["posts"]
        post = posts_collection.find_one({"_id": ObjectId(pId)})
        contactedList = list(post.get("contacted-list", []))
        contactedList.append(investorId)
        posts_collection.update_one(
            {"_id": ObjectId(pId)},
            {"$set": {"contacted-list": contactedList}}
        )

        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = user["email"]
        message["Subject"] = subject
        message.attach(MIMEText(html_content, "html"))

        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, message["To"], message.as_string())

        return {"status": "success", "message": "Email sent successfully"}

    except Exception as e:
        # Print exception details
        print(f"An error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")