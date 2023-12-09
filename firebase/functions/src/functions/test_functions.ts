import functions = require("firebase-functions");

export const testFunctionHandler = async (req: functions.https.Request, resp: functions.Response<string>) => {
    const audioUrl = req.body.audioUrl;

    functions.logger.info(audioUrl);

    resp.send("Hello from Firebase!");
};
