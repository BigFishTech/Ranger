import { Timestamp } from "firebase-admin/firestore";

export interface DeviceProfile {
    createdAt: Timestamp;
    userId?: string;
}
