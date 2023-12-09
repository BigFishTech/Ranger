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

from src.board import Board
from src.voice.audio import AudioFormat, play_wav, record_file, Recorder


def upload_audio_to_firebase(file_name):
    storage_url = "ranger-8961d.appspot.com"

    # Get the current working directory
    current_dir = os.getcwd()

    # Construct the full file path
    file_path = os.path.join(current_dir, file_name)

    # Define the headers for the HTTP request
    headers = {"Content-Type": "audio/wav"}  # Assuming a WAV file format

    # Define the Firebase upload URL
    upload_url = (
        f"https://firebasestorage.googleapis.com/v0/b/{storage_url}/o?name={file_name}"
    )

    # Read the audio file data
    with open(file_path, "rb") as audio_file:
        file_data = audio_file.read()

    # Make the POST request to upload the file
    response = requests.post(upload_url, headers=headers, data=file_data)

    # Check if the upload was successful
    if response.status_code == 200:
        # Get the download URL
        # download_url = response.json().get("downloadTokens")
        return file_name
    else:
        return "Upload failed"


def download_audio_from_url(url, file_name):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the current working directory
        current_dir = os.getcwd()

        # Construct the full file path for the mp3 file
        file_path_mp3 = os.path.join(current_dir, file_name)

        # Write the content to a file
        with open(file_path_mp3, "wb") as audio_file:
            audio_file.write(response.content)

        print(f"MP3 file downloaded successfully: {file_path_mp3}")

        # Construct the file path for the wav file
        file_path_wav = os.path.splitext(file_path_mp3)[0] + ".wav"

        # Convert mp3 to wav using FFmpeg
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", file_path_mp3, file_path_wav], check=True
            )
            print(f"WAV file created successfully: {file_path_wav}")
        except subprocess.CalledProcessError:
            print("Failed to convert file to WAV format")
            return None

        return file_path_wav
    else:
        print("Failed to download file")
        return None


def call_cloud_function(audio_storage_location):
    # Replace with your Cloud Function's URL
    cloud_function_url = "https://testfunction-23pdjdacza-uc.a.run.app"

    # Prepare the JSON body
    json_data = {"audioStorageLocation": audio_storage_location}

    # Make the POST request
    response = requests.post(cloud_function_url, json=json_data)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the response text
        return response.text
    else:
        print("Failed to call Cloud Function:", response.status_code)
        return None


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

        # Example usage
        storage_file_location = upload_audio_to_firebase(args.filename)
        print("Uploaded file URL:", storage_file_location)

        # Example usage
        response_audio_url = call_cloud_function(storage_file_location)
        print("Response audio url:", response_audio_url)

        downloaded_file = download_audio_from_url(
            response_audio_url, "downloaded_audio.mp3"
        )
        print("Downloaded file:", downloaded_file)

        # print("Press button to play recorded sound.")
        # board.button.wait_for_press()

        print("Playing...")
        # play_wav(args.filename)
        play_wav(downloaded_file)
        print("Done.")


if __name__ == "__main__":
    main()
