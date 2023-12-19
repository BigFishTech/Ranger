import functions = require("firebase-functions");
import FormData from "form-data";
import axios from "axios";
import busboy from "busboy";
import { addMessage, getDeviceProfile, getRecentMessages } from "../utils/firestore_helper";
import { ChatMessage, GPTMessage } from "../types/chat_message";
import { Timestamp } from "firebase-admin/firestore";


export const testFunctionHandler = functions.https.onRequest(async (req, resp) => {
    const start1 = process.hrtime.bigint();

    if (req.method !== "POST") {
        resp.status(405).send("Method Not Allowed");
        return;
    }

    const bb = busboy({ headers: req.headers });

    let deviceId: string | undefined;
    const chunks: Buffer[] = [];

    await new Promise<void>((resolve, reject) => {
        bb
            .once("close", resolve)
            .once("error", reject)
            .on("file", (name, fileStream, info) => {
                fileStream.on("data", (chunk) => {
                    chunks.push(chunk);
                });

                fileStream.on("end", () => resolve());
                fileStream.on("error", (error) => reject(error));
            })
            .on("field", (fieldname: string, val: string | undefined, _fieldnameTruncated: unknown, _valTruncated: unknown, _encoding: unknown, _mimetype: unknown) => {
                if (fieldname === "deviceId") {
                    deviceId = val;
                }
            })
            .end(req.rawBody);
    });

    const end1 = process.hrtime.bigint();
    const timeTaken1 = Number(end1 - start1) / 1000000;
    functions.logger.log(`Audio chunks loaded: ${timeTaken1}ms`);
    const start2 = process.hrtime.bigint();

    const completeFileBuffer = Buffer.concat(chunks);

    // If device ID is not found, return error
    if (!deviceId) {
        resp.status(400).send("No device ID found");
        return;
    }

    // Get user ID from the device ID
    const deviceProfile = await getDeviceProfile(deviceId);
    const userId = deviceProfile?.userId;

    // If user ID is not found, return error
    if (!userId) {
        resp.status(400).send("No user connected to device");
        return;
    }

    // Query recent messages from Firestore
    const recentMessages = await getRecentMessages(userId, 5);

    const end2 = process.hrtime.bigint();
    const timeTaken2 = Number(end2 - start2) / 1000000;
    functions.logger.log(`Loaded chat history: ${timeTaken2}ms`);
    const start3 = process.hrtime.bigint();

    // Transcribe the audio
    const transcription = await getTranscription(completeFileBuffer);

    const end3 = process.hrtime.bigint();
    const timeTaken3 = Number(end3 - start3) / 1000000;
    functions.logger.log(`Transcribed audio: ${timeTaken3}ms`);
    const start4 = process.hrtime.bigint();

    // Save transcribed message to Firestore
    const requestMessage: ChatMessage = {
        createdAt: Timestamp.now(),
        userGenerated: true,
        text: transcription,
    };
    await addMessage(userId, requestMessage);

    // Compile message history of type GPTMessage from recentMessages and transcription
    const messageHistory: GPTMessage[] = recentMessages.reverse().map((message) => ({
        role: message.userGenerated ? "user" : "assistant",
        content: message.text,
    }));

    messageHistory.push({
        role: "user",
        content: transcription,
    });

    const end4 = process.hrtime.bigint();
    const timeTaken4 = Number(end4 - start4) / 1000000;
    functions.logger.log(`Added transcription to chat history: ${timeTaken4}ms`);
    const start5 = process.hrtime.bigint();

    // Get GPT chat completion
    const gptChatCompletion = await getGptChatCompletion(messageHistory);

    const end5 = process.hrtime.bigint();
    const timeTaken5 = Number(end5 - start5) / 1000000;
    functions.logger.log(`Chat completion generated: ${timeTaken5}ms`);
    const start6 = process.hrtime.bigint();

    // Save GPT chat completion to Firestore
    const responseMessage: ChatMessage = {
        createdAt: Timestamp.now(),
        userGenerated: false,
        text: gptChatCompletion,
    };
    await addMessage(userId, responseMessage);

    const end6 = process.hrtime.bigint();
    const timeTaken6 = Number(end6 - start6) / 1000000;
    functions.logger.log(`Added message to chat history: ${timeTaken6}ms`);
    const start7 = process.hrtime.bigint();

    // Get TTS audio from OpenAI
    const openAiUrlTTS = "https://api.openai.com/v1/audio/speech";

    // Prepare the request body for OpenAI TTS
    const requestBody = {
        model: "tts-1",
        input: gptChatCompletion,
        voice: "onyx",
        format: "opus",
    };

    // Request to OpenAI TTS
    const ttsResponse = await axios.post(openAiUrlTTS, requestBody, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        },
        responseType: "stream",
    });

    const end7 = process.hrtime.bigint();
    const timeTaken7 = Number(end7 - start7) / 1000000;
    functions.logger.log(`Speech request received: ${timeTaken7}ms`);

    resp.setHeader("Content-Type", "audio/ogg");
    ttsResponse.data.pipe(resp);
});


const getTranscription = async (fileBuffer: Buffer): Promise<string> => {
    // Prepare the form data for OpenAI API request
    const formData = new FormData();
    formData.append("file", fileBuffer, {
        filename: "audio.mp3",
        contentType: "audio/mpeg",
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

const getGptChatCompletion = async (messageHistory: GPTMessage[]): Promise<string> => {
    const openAiUrl = "https://api.openai.com/v1/chat/completions";

    const messages = [
        {
            role: "system",
            content: "You are the biggest bro of them all. Respond short and direct.",
        },
        ...messageHistory,
    ];

    functions.logger.log(messages);

    // Prepare the request body
    const requestBody = {
        model: "gpt-4-1106-preview",
        temperature: 0.9,
        messages: messages,
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
