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

from src.board import Board

# from src.voice.audio import AudioFormat, play_wav, record_file, Recorder
from src.voice.easy_audio import record_file, play_mp3


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

    # Load the audio file using pydub
    audio = AudioSegment.from_file(audio_buffer, format="mp3")

    # Play the audio
    play_obj = sa.play_buffer(
        audio.raw_data,
        num_channels=audio.channels,
        bytes_per_sample=audio.sample_width,
        sample_rate=audio.frame_rate,
    )

    # Wait for playback to finish before exiting
    play_obj.wait_done()


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

        record_file(filename=args.filename, wait=wait)

        play_mp3(args.filename)

        # stream_and_play_audio()


if __name__ == "__main__":
    main()
