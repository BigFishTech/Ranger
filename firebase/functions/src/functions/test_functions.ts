import { Storage } from "firebase-admin/storage";
import functions = require("firebase-functions");
import FormData from "form-data";
import axios from "axios";
// import { Storage } from '@google-cloud/storage';
// import fetch from 'node-fetch';

export const testFunctionHandler = async (req: functions.https.Request, resp: functions.Response<string>) => {
    // const audioUrl = req.body.audioUrl;

    // functions.logger.info(audioUrl);

    // resp.send("https://firebasestorage.googleapis.com/v0/b/ranger-8961d.appspot.com/o/bumbum.wav?alt=media&token=ff1dc100-ece2-4fb7-a807-16f4faec57ec");


    // Extract the audio file URL from the request
    const audioStorageLocation = req.query.audioStorageLocation as string;

    if (!audioStorageLocation) {
        resp.status(400).send("No audio provided");
        return;
    }

    // Initialize Firebase Storage
    const storage = new Storage();
    const storageFile = storage.bucket().file(audioStorageLocation);

    // Download the file from Firebase Storage
    const [fileBuffer] = await storageFile.download();

    // Prepare the form data for OpenAI API request
    const formData = new FormData();
    formData.append("file", fileBuffer, {
        filename: "audio.wav",
        contentType: "audio/wav",
    });
    formData.append("model", "whisper-1");

    // OpenAI API endpoint and headers
    const openAiUrl = "https://api.openai.com/v1/audio/transcriptions";

    try {
        // Making the request using axios
        const openAiResponse = await axios.post(openAiUrl, formData, {
            headers: {
                ...formData.getHeaders(),
                "Authorization": "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",
            },
        });

        // Sending back the response
        resp.send(openAiResponse.data);
    } catch (error) {
        console.error("Error transcribing audio:", error);
        resp.status(500).send("Internal server error");
    }
};
