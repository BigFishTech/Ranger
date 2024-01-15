# from pydub import AudioSegment
# import simpleaudio as sa
# import asyncio


# def play_audio(audio_buffer):
#     # Load the audio file using pydub
#     audio = AudioSegment.from_file(audio_buffer)

#     # Play the audio
#     play_obj = sa.play_buffer(
#         audio.raw_data,
#         num_channels=audio.channels,
#         bytes_per_sample=audio.sample_width,
#         sample_rate=audio.frame_rate,
#     )

#     # Wait for playback to finish before exiting
#     play_obj.wait_done()


# async def async_play_audio(audio_buffer):
#     loop = asyncio.get_running_loop()
#     await loop.run_in_executor(None, play_audio, audio_buffer)

import sounddevice as sd
from pydub import AudioSegment
import numpy as np
import subprocess


def play_audio(audio_buffer):
    # Load the audio file using pydub
    audio = AudioSegment.from_file(audio_buffer)
    audio_samples = np.array(audio.get_array_of_samples())

    # Play the audio using sounddevice
    sd.play(audio_samples, samplerate=audio.frame_rate, device=3)
    sd.wait()  # Wait for playback to finish


def play_audio_from_file(file_name):
    """
    Plays an audio file using the aplay command.
    """
    try:
        # Use the aplay command to play the audio file
        subprocess.run(["aplay", file_name])
    except Exception as e:
        print(f"An error occurred while playing audio: {e}")
