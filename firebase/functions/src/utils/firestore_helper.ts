import { firestore } from "firebase-admin";
import { DocumentData, FieldValue, QueryDocumentSnapshot, Timestamp } from "firebase-admin/firestore";

// import functions = require("firebase-functions");


const converter = <T extends DocumentData>() => ({
    toFirestore: (data: T): DocumentData => data,
    fromFirestore: (snap: QueryDocumentSnapshot<DocumentData>): T => snap.data() as T,
});

const dataPoint = <T extends DocumentData>(collectionPath: string) =>
    firestore().collection(collectionPath).withConverter(converter<T>());

export const db = {
    // users: dataPoint<UserData>("Users"),
    // chatRooms: (userId: string) => dataPoint<ChatRoom>(`Users/${userId}/ChatRooms`),
};

// ///////////////////////////////////////
// Strongly Typed DB Helpers
// ///////////////////////////////////////

