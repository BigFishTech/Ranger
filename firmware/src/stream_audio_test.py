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
import subprocess
import os

# from pydub import AudioSegment
# from pydub.playback import play
import soundfile as sf
import sounddevice as sd
import io

from src.board import Board
from src.voice.audio import AudioFormat, play_wav, record_file, Recorder


def stream_and_play_audio():
    cloud_function_url = "https://testfunction-23pdjdacza-uc.a.run.app"

    # Send request to Google Cloud Function
    response = requests.get(cloud_function_url, stream=True)

    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to get audio")
        return

    # Load streamed data into a BytesIO buffer
    audio_buffer = io.BytesIO()
    for chunk in response.iter_content(chunk_size=1024):
        audio_buffer.write(chunk)
    audio_buffer.seek(0)  # Rewind the buffer to the beginning

    with sf.SoundFile(audio_buffer, format="OGG") as sound_file:
        sd.play(sound_file.read(dtype="float32"), sound_file.samplerate)
        sd.wait()

    # Load audio using pydub
    # audio = AudioSegment.from_file(
    #     audio_buffer, format="opus"
    # )  # or format="opus" based on your stream format

    # # Play audio
    # play(audio)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", "-f", default="recording.wav")
    args = parser.parse_args()

    with Board() as board:
        print("Press button to start recording.")
        board.button.wait_for_press()

        done = threading.Event()
        board.button.when_pressed = done.set

        def wait():
            start = time.monotonic()
            while not done.is_set():
                duration = time.monotonic() - start
                print("Recording: %.02f seconds [Press button to stop]" % duration)
                time.sleep(0.5)

        record_file(AudioFormat.CD, filename=args.filename, wait=wait, filetype="wav")

        stream_and_play_audio()


if __name__ == "__main__":
    main()
