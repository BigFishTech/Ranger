import requests
import io

import aiohttp
import asyncio

SEND_VOICE_CHAT_URL = "https://testfunction-23pdjdacza-uc.a.run.app"
DEVICE_ID = "T8ErqY4ibxkrtNudaHO7"


def send_voice_chat(audio_file_path):
    """
    Sends the audio file to the cloud function and returns the response.
    """
    try:
        with open(audio_file_path, "rb") as f:
            # Send POST request with the file
            files = {"file": (audio_file_path, f, "audio/webm")}
            data = {"deviceId": DEVICE_ID}
            response = requests.post(
                SEND_VOICE_CHAT_URL, files=files, data=data, stream=True
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

            return audio_buffer
    except requests.RequestException as e:
        print(f"An error occurred while sending audio to cloud: {e}")
        return None


# import aiohttp
# import asyncio
# import io

# SEND_VOICE_CHAT_URL = "https://testfunction-23pdjdacza-uc.a.run.app"
# DEVICE_ID = "T8ErqY4ibxkrtNudaHO7"

# async def send_voice_chat(audio_file_path):
#     """
#     Asynchronously sends the audio file to the cloud function and returns the response.
#     """
#     try:
#         # Open the file in binary mode
#         async with aiohttp.ClientSession() as session:
#             with open(audio_file_path, "rb") as f:
#                 # Prepare the data to send
#                 files = {"file": (audio_file_path, f, "audio/mpeg")}
#                 data = {"deviceId": DEVICE_ID}

#                 # Perform the POST request asynchronously
#                 async with session.post(
#                     SEND_VOICE_CHAT_URL, data=data, files=files
#                 ) as response:
#                     if response.status != 200:
#                         print("Failed to get audio")
#                         return None

#                     # Asynchronously read the streamed data
#                     audio_buffer = io.BytesIO()
#                     async for chunk in response.content.iter_chunked(1024):
#                         audio_buffer.write(chunk)
#                     audio_buffer.seek(0)  # Rewind the buffer to the beginning

#                     return audio_buffer
#     except aiohttp.ClientError as e:
#         print(f"An error occurred while sending audio to cloud: {e}")
#         return None
