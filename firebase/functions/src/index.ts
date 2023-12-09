import { initializeApp, applicationDefault } from "firebase-admin/app";
import { firestore } from "firebase-admin";
// import functions = require("firebase-functions");

initializeApp({
    credential: applicationDefault(),
    projectId: "ranger-8961d",
    storageBucket: "ranger-8961d.appspot.com",
});

firestore().settings({ ignoreUndefinedProperties: true });

import * as dotenv from "dotenv";
dotenv.config();

import { onRequest } from "firebase-functions/v2/https";
import { testFunctionHandler } from "./functions/test_functions";

/////////////////////////////////////////////////////////
// Test Functions
/////////////////////////////////////////////////////////

exports.testFunction = onRequest(testFunctionHandler);
