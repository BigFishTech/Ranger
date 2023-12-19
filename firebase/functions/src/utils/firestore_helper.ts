import { firestore } from "firebase-admin";
import { DocumentData, FieldValue, QueryDocumentSnapshot, Timestamp } from "firebase-admin/firestore";
import { UserData } from "../types/user_data";
import { ChatMessage } from "../types/chat_message";
import { DeviceProfile } from "../types/device_profile";

// import functions = require("firebase-functions");


const converter = <T extends DocumentData>() => ({
    toFirestore: (data: T): DocumentData => data,
    fromFirestore: (snap: QueryDocumentSnapshot<DocumentData>): T => snap.data() as T,
});

const dataPoint = <T extends DocumentData>(collectionPath: string) =>
    firestore().collection(collectionPath).withConverter(converter<T>());

export const db = {
    users: dataPoint<UserData>("Users"),
    devices: dataPoint<DeviceProfile>("Devices"),
    messages: (userId: string) => dataPoint<ChatMessage>(`Users/${userId}/Messages`),
};

// ///////////////////////////////////////
// Strongly Typed DB Helpers
// ///////////////////////////////////////

// Query recent messages from Firestore
export const getRecentMessages = async (userId: string, limit: number) => {
    const messages = await db.messages(userId).orderBy("createdAt", "desc").limit(limit).get();
    return messages.docs.map((message) => message.data());
};

// Get device profile from ID
export const getDeviceProfile = async (deviceId: string) => {
    const deviceProfile = await db.devices.doc(deviceId).get();
    return deviceProfile.data();
};

// Add a message to the database
export const addMessage = async (userId: string, message: ChatMessage) => {
    await db.messages(userId).add(message);
};

