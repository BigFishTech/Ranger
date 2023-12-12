import { storage } from "firebase-admin";
import functions = require("firebase-functions");
import FormData from "form-data";
import axios from "axios";
import { PassThrough } from "stream";

// import { Storage } from "@google-cloud/storage";
// import fetch from "node-fetch";

export const testFunctionHandler = async (req: functions.https.Request, resp: functions.Response<string>) => {
    // const audioStorageLocation = req.body.audioStorageLocation as string;
    // if (!audioStorageLocation) {
    //     resp.status(400).send("No audio provided");
    //     return;
    // }
    // // Get the transcription
    // const transcription = await getTranscription(audioStorageLocation);
    // // Get the GPT chat completion
    // const gptChatCompletion = await getGptChatCompletion(transcription);
    // // Get the voice completion
    // const voiceCompletionUrl = await getVoiceCompletion(gptChatCompletion);
    // // Send the response
    // resp.send(voiceCompletionUrl);


    const openAiUrl = "https://api.openai.com/v1/audio/speech";

    // Prepare the request body for OpenAI TTS
    const requestBody = {
        model: "tts-1",
        input: "Hello this is a test, I am streaming this large body of text, I hope it works. Please let me know how we are doing here. Hello this is a test, I am streaming this large body of text, I hope it works. Please let me know how we are doing here. Hello this is a test, I am streaming this large body of text, I hope it works. Please let me know how we are doing here. ",
        voice: "onyx",
    };

    // Request to OpenAI TTS
    const ttsResponse = await axios.post(openAiUrl, requestBody, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        },
        responseType: "stream",
    });

    resp.setHeader("Content-Type", "audio/mpeg");
    ttsResponse.data.pipe(resp);
};

const getTranscription = async (storageAudioFileLocation: string): Promise<string> => {
    // Initialize Firebase Storage
    const storageFile = storage().bucket().file(storageAudioFileLocation);

    // Download the file from Firebase Storage
    const [fileBuffer] = await storageFile.download();

    functions.logger.info("File downloaded successfully");

    // Prepare the form data for OpenAI API request
    const formData = new FormData();
    formData.append("file", fileBuffer, {
        filename: "audio.wav",
        contentType: "audio/wav",
    });
    formData.append("model", "whisper-1");

    // OpenAI API endpoint and headers
    const openAiUrl = "https://api.openai.com/v1/audio/transcriptions";

    // Making the request using axios
    const openAiResponse = await axios.post(openAiUrl, formData, {
        headers: {
            ...formData.getHeaders(),
            "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        },
    });

    return openAiResponse.data.text;
};

const getGptChatCompletion = async (userMessage: string): Promise<string> => {
    const openAiUrl = "https://api.openai.com/v1/chat/completions";

    // Prepare the request body
    const requestBody = {
        model: "gpt-4-1106-preview",
        messages: [
            {
                role: "system",
                content: "You are the biggest bro of them all. Your bro level is over 9000.",
            },
            {
                role: "user",
                content: userMessage,
            },
        ],
    };

    try {
        const response = await axios.post(openAiUrl, requestBody, {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
            },
        });

        // Extracting the assistant"s response
        const assistantMessage = response.data.choices[0].message.content;
        return assistantMessage;
    } catch (error) {
        console.error("Error in GPT chat completion:", error);
        return "There was an error processing your request.";
    }
};

const getVoiceCompletion = async (message: string): Promise<string> => {
    const openAiUrl = "https://api.openai.com/v1/audio/speech";

    // Prepare the request body for OpenAI TTS
    const requestBody = {
        model: "tts-1",
        input: message,
        voice: "onyx",
    };

    try {
        // Request to OpenAI TTS
        const ttsResponse = await axios.post(openAiUrl, requestBody, {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
            },
            responseType: "arraybuffer",
        });

        // Initialize Firebase Storage
        const bucket = storage().bucket();
        const fileName = "speech_response.mp3";
        const file = bucket.file(fileName);

        // Upload the audio file to Firebase Storage
        await file.save(ttsResponse.data, {
            metadata: { contentType: "audio/mpeg" },
        });

        // Make the file publicly accessible (if required)
        await file.makePublic();

        // Get the file"s public URL
        const publicUrl = `https://storage.googleapis.com/ranger-8961d.appspot.com/${fileName}`;
        return publicUrl;
    } catch (error) {
        console.error("Error in text to speech and upload:", error);
        return "There was an error processing your request.";
    }
};
