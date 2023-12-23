#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import time
import threading

import requests

from pydub import AudioSegment
import simpleaudio as sa
import io

from src.voice.easy_audio import record_file, play_audio


def stream_and_play_audio(filename):
    cloud_function_url = "https://testfunction-23pdjdacza-uc.a.run.app"

    def wait():
        import time

        time.sleep(5)

    record_file(filename=filename, wait=wait)

    print("Sending audio to cloud function")

    with open(filename, "rb") as f:
        # Send POST request with the file
        files = {"file": (filename, f, "audio/mpeg")}
        data = {"deviceId": "T8ErqY4ibxkrtNudaHO7"}
        response = requests.post(
            cloud_function_url, files=files, data=data, stream=True
        )

        # Check if the request was successful
        if response.status_code != 200:
            print("Failed to get audio")
            return

        # Load streamed data into a BytesIO buffer
        audio_buffer = io.BytesIO()
        for chunk in response.iter_content(chunk_size=1024):
            audio_buffer.write(chunk)
        audio_buffer.seek(0)  # Rewind the buffer to the beginning

        play_audio(audio_buffer)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", "-f", default="recording.mp3")
    args = parser.parse_args()

    stream_and_play_audio(args.filename)


if __name__ == "__main__":
    main()
