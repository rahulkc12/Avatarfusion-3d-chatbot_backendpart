import { exec } from "child_process";
import cors from "cors";
import dotenv from "dotenv";
import voice from "elevenlabs-node";
import express from "express";
import { promises as fs } from "fs";
import OpenAI from "openai";
import * as tf from "@tensorflow/tfjs";
import { loadModel } from "@tensorflow/tfjs-node";
dotenv.config();

{/*}
console.log('OPENAI_API_KEY:', process.env.OPENAI_API_KEY);
const openai = new OpenAI({
  apiKey: "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",//"-","-" Your OpenAI API key here, I used "-" to avoid errors when the key is not set but you should not do that
});

*/}

console.log('ELEVENLABS_API_KEY:', process.env.ELEVEN_LABS_API_KEY);
const elevenLabsApiKey = process.env.ELEVEN_LABS_API_KEY;
//const voiceID = "kgG7dCoKCfLehAPWkJOE";
const voiceID = "jsCqWAovK2LkecY7zXl4";

const app = express();
app.use(express.json());
app.use(cors());
const port = 3000;
//loading emotion recognition model
let emotionModel;

async function loadEmotionModel() {
  emotionModel = await loadModel("./models/e_model/emotion_recognition.h5");
}
loadEmotionModel();

const generateReply = (userMessage, userEmotion) => {
  tranformerModel= loadModel("./models/t_model/mymodel1.h5")
  return replyMessage;
};


app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.get("/voices", async (req, res) => {
  res.send(await voice.getVoices(elevenLabsApiKey));
});

const execCommand = (command) => {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) reject(error);
      resolve(stdout);
    });
  });
};

const lipSyncMessage = async (message) => {
  const time = new Date().getTime();
  console.log(`Starting conversion for message ${message}`);
  await execCommand(
    `ffmpeg -y -i audios/message_${message}.mp3 audios/message_${message}.wav`
    // -y to overwrite the file
  );
  console.log(`Conversion done in ${new Date().getTime() - time}ms`);
  await execCommand(
    `./bin/rhubarb -f json -o audios/message_${message}.json audios/message_${message}.wav -r phonetic`
  );
  // -r phonetic is faster but less accurate
  console.log(`Lip sync done in ${new Date().getTime() - time}ms`);
};

app.post("/chat", async (req, res) => {
  const userMessage = req.body.message;
  console.log("Received message from voice input:", userMessage);

  if (!userMessage) {
    res.send({
      messages: [
       
        {
          text: "Hey dear... how was your day",
          audio: await audioFileToBase64("audios/intro_0.wav"),
          lipsync: await readJsonTranscript("audios/intro_0.json"),
          facialExpression: "smile",
          animation: "Talking_1",
        },
      {/*  // 
      //   {
      //    text: "Hello, I am freya,what is your name?",
      //   audio: await audioFileToBase64("audios/freyaintro.mp3"),
      // lipsync: await readJsonTranscript("audios/freyaintro.json"),
       //   facialExpression: "smile",
        //  animation: "Talking_1",
        //},
       // 
        {
          text: "I missed you so much... Please don't go for so long!",
          audio: await audioFileToBase64("audios/intro_1.wav"),
          lipsync: await readJsonTranscript("audios/intro_1.json"),
          facialExpression: "sad",
          animation: "Crying",
        },
      */}
      
      ],
    });
    return;
  }
  if (!elevenLabsApiKey) {//==="-"
    res.send({
      messages: [
        {
          text: "Please my dear, don't forget to add your API keys!",
          audio: await audioFileToBase64("audios/api_0.wav"),
          lipsync: await readJsonTranscript("audios/api_0.json"),
          facialExpression: "angry",
          animation: "Angry",
        },
       
      ],
    });
    return;
  }
  {/*}
  let messages = JSON.parse(completion.choices[0].message.content);
  if (messages.messages) {
    messages = messages.messages; // ChatGPT is not 100% reliable, sometimes it directly returns an array and sometimes a JSON object with a messages property
  }*/}


  for (let i = 0; i < messages.length; i++) {
    const message = messages[i];
    // generate audio file
    const fileName = `audios/message_${i}.mp3`; // The name of your audio file
    const textInput = message.text; // The text you wish to convert to speech
    await voice.textToSpeech(elevenLabsApiKey, voiceID, fileName, textInput);
    // generate lipsync
    await lipSyncMessage(i);
    message.audio = await audioFileToBase64(fileName);
    message.lipsync = await readJsonTranscript(`audios/message_${i}.json`);
  }


    // Predict emotion for user message
    const userEmotion = await predictEmotion(userMessage);

    // Generate reply message using some logic
    const replyMessage = generateReply(userMessage, userEmotion);
  
    // Predict emotion for generated reply message
    const replyEmotion = await predictEmotion(replyMessage);
    console.log("Reply emotion:", replyEmotion);
  
  
  
  
  
  
    res.send({ messages });


});

const readJsonTranscript = async (file) => {
  const data = await fs.readFile(file, "utf8");
  return JSON.parse(data);
};

const audioFileToBase64 = async (file) => {
  const data = await fs.readFile(file);
  return data.toString("base64");
};

app.listen(port, () => {
  console.log(`AvatarFusion listening on port ${port}`);
});
