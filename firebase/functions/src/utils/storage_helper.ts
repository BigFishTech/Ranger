import { storage } from "firebase-admin";

// Save a string to Firebase Storage
export const saveString = async (path: string, data: string, contentType: string = "text/plain"): Promise<void> => {
    const fileRef = storage().bucket().file(path);
    await fileRef.save(data, {
        contentType: contentType,
    });
};

// Load a string from Firebase Storage
export const loadString = async (path: string): Promise<string> => {
    const fileRef = storage().bucket().file(path);
    const [data] = await fileRef.download();
    return data.toString();
};

// Save a buffer to Firebase Storage
export const saveBuffer = async (path: string, buffer: Buffer, contentType: string = "application/octet-stream"): Promise<void> => {
    const fileRef = storage().bucket().file(path);
    await fileRef.save(buffer, {
        contentType: contentType,
    });
};

// Load a file as a buffer from Firebase Storage
export const loadBuffer = async (path: string): Promise<Buffer> => {
    const fileRef = storage().bucket().file(path);
    const [data] = await fileRef.download();
    return data;
};

// Delete a file from Firebase Storage
export const deleteFile = async (path: string): Promise<void> => {
    const fileRef = storage().bucket().file(path);
    await fileRef.delete();
};

// Get download URL for a file in Firebase Storage (assuming the file is publicly accessible)
export const getDownloadURL = async (path: string): Promise<string> => {
    const fileRef = storage().bucket().file(path);
    const [url] = await fileRef.getSignedUrl({
        action: "read",
        expires: "03-17-2025", // Set an appropriate expiration date
    });
    return url;
};

export const saveJSON = async (path: string, jsonData: unknown): Promise<void> => {
    const fileRef = storage().bucket().file(path);
    const jsonString = JSON.stringify(jsonData, null, 2); // Convert data to formatted JSON string
    await fileRef.save(jsonString, {
        contentType: "application/json",
    });
};

export const loadJSON = async <T>(path: string): Promise<T> => {
    const fileRef = storage().bucket().file(path);
    const [data] = await fileRef.download();
    return JSON.parse(data.toString()) as T;
};
