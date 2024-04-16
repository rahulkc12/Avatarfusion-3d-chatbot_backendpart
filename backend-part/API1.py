from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tensorflow as tf
from emotion_p import *
from transfomer_p import *
#import elevenlabs 
import gtts
import os
import subprocess
import uuid
from typing import List
from base64 import b64encode
import asyncio
import random
from fastapi import BackgroundTasks as background_tasks


app = FastAPI()


# Allowing CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''
def speech(text, lang='en'):
    tts = gtts(text=text, lang=lang)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)  # Reset the position to the start of the BytesIO object
    return audio_bytes.read()
'''
async def generate_lipsync(message):
    # Convert text to speech using ElevenLabs
    filename = str(uuid.uuid4())

    # Convert text to speech using ElevenLabs
    audio_file_path = f"audios/{filename}.mp3"
    audio= gtts.gTTS(message,lang="en")
    audio.save(audio_file_path)

    # Convert audio to WAV format
    subprocess.run(["ffmpeg", "-i", audio_file_path, f"audios/{filename}.wav"])

    # Generate lipsync
    subprocess.run(["./Rhubarb-Lip-Sync-1.13.0-Windows/rhubarb", "-f", "json", "-o", f"audios/{filename}.json", f"audios/{filename}.wav", "-r", "phonetic"])
    return filename

# Define request body model
class MessageIn(BaseModel):
    message: str

# Define response body model for messages
class MessageOut(BaseModel):
    text: str
    audio: str
    lipsync: str
    facialExpression: str
    animation: str
    


# Route for handling chat messages
@app.post("/chat", response_model=List[MessageOut])
async def chat(message_in: MessageIn):
    try:
        user_message = message_in.message
        print(user_message)
        if not user_message:
            raise HTTPException(status_code=400, detail="User message cannot be empty")

        # Predict emotion for user message
        preprocessed_message = preprocess_sentence(user_message)
        user_emotion = predict_emotion(preprocessed_message)

        # Generate reply message using transformer model
        reply_message = str(predict(user_message, user_emotion))

        # Predict emotion for generated reply message
        reply_emotion = predict_emotion(reply_message)
        print("****reply:", reply_message)
        print("****mytext:", user_message)
        print("reply_motion:", reply_emotion)

        # generate lipsync and audio
        filename = await generate_lipsync(reply_message)
        print('filename',filename)
        # Load lipsync data
        #filename = "freyaintro"
        lipsync_file_path = f"audios/{filename}.json"
        with open(lipsync_file_path, "r") as lipsync_file:
            lipsync_data = str(lipsync_file.read())
        print("lipsync:", lipsync_data)

        audio_file_path = f"audios/{filename}.wav"
        
        with open(audio_file_path, "rb") as audio_file:
            audio_base64 = str(b64encode(audio_file.read()).decode())
        
        
        facial_emotion = await emotion(reply_emotion)
        face_animation = await animation(facial_emotion)

        response = MessageOut(
            text=reply_message,
            audio= audio_base64,
            lipsync=lipsync_data,
            facialExpression=facial_emotion,
            animation=face_animation
        )
        remove = await delete_audio_files(filename)
        print("Sending response:", response)
        return [response]

    except IndexError:
        error_message = "Index out of range error occurred. Please provide a valid input."
        return HTTPException(status_code=400, detail=error_message)



async def emotion(reply_emotion):
    #neutral,fear sad,suprised,angry,happy,disgust expression in ui
    #['neutral','angry', 'fear', 'joy', 'love', 'sadness', 'suprised'] in emotion model
    if(reply_emotion=="neutral"or reply_emotion==" neutral"):
        emotion ="neutral"
    elif(reply_emotion=="angry"):
        emotion ="angry"
    elif(reply_emotion=="fear"):
        emotion ="fear"
    elif(reply_emotion=="love" or reply_emotion=="joy"):
        emotion="happy"
    elif(reply_emotion=="sadness"):
        emotion="sad"
    elif(reply_emotion=="suprised"):
        emotion= "suprised"
    else:
        emotion= "neutral"
        
    return str(emotion)
        
   


def randomanimation(animation):
    rn = random.randint(1,4)
    print(rn)
    if(rn==1):
        animation =animation
    elif(rn==2):
        animation ="Talking0"
    elif(rn==3):
        animation ="Talking1"
    else:
        animation ="Talking2"
        
    return str(animation)

async def animation(emotion):
    #neutral,fear sad,suprised,angry,happy,disgust expression in ui
    
    
    if(emotion=="neutral"):
        animation = randomanimation(emotion)
    elif(emotion=="angry"):
        animation = randomanimation(emotion)
    elif(emotion=="fear"):
        animation = randomanimation(emotion)
    elif(emotion=="happy"):
        animation = randomanimation(emotion)
    elif(emotion=="sad"):
        animation = randomanimation(emotion)
    elif(emotion=="suprised"):
        animation = randomanimation(emotion)
    else:
        animation = "idle"
        
    return str(animation)


async def delete_audio_files(filename):
    # Delete audio files after a certain time period (e.g., 30 seconds)
    await asyncio.sleep(30)
    audio_file_path = f"audios/{filename}.mp3"
    os.remove(audio_file_path)
    os.remove(audio_file_path.replace(".mp3", ".wav"))
    os.remove(f"audios/{filename}.json")


# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
#uvicorn API1:app --host 0.0.0.0 --port 3000 
# --reload