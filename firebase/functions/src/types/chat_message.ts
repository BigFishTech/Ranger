import { Timestamp } from "firebase-admin/firestore";

export interface ChatMessage {
    createdAt: Timestamp;
    userGenerated: boolean;
    text: string;
}

export interface GPTMessage {
    role: Role;
    content: string;
}

export type Role = "system" | "user" | "assistant";
