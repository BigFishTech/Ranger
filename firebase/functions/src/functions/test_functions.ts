import functions = require("firebase-functions");

export const testFunctionHandler = async (req: functions.https.Request, resp: functions.Response<string>) => {
    const audioUrl = req.body.audioUrl;

    functions.logger.info(audioUrl);

    resp.send("https://firebasestorage.googleapis.com/v0/b/ranger-8961d.appspot.com/o/bumbum.wav?alt=media&token=ff1dc100-ece2-4fb7-a807-16f4faec57ec");
};
