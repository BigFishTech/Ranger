import subprocess
import logging
import globals

from pydub import AudioSegment
import simpleaudio as sa
import asyncio


def ffRecord(filename=None, device="default"):
    if filename is None:
        raise ValueError("Filename must be specified.")

    # cmd = [
    #     "ffmpeg",
    #     "-y",  # Overwrite output files without asking
    #     # "-loglevel",  # Suppress warnings
    #     # "error",
    #     # "-f",
    #     # "alsa",  # ALSA audio capture
    #     # "-i",
    #     # device,  # Input device
    #     # "-ac",
    #     # "2",  # Number of audio channels
    #     "-ar",
    #     "44100",  # Sample rate
    #     "-b:a",
    #     "192k",  # Audio bit rate
    #     "-acodec",
    #     "libmp3lame",  # Audio codec
    #     # "-bufsize",
    #     # "32k",  # Buffer size
    #     filename,
    # ]

    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output files without asking
        "-loglevel",  # Suppress warnings
        "error",
        "-f",
        "avfoundation",
        "-i",
        ":2",  # Input device
        filename,
    ]

    return cmd


async def record_file(filename, device="default"):
    if filename is None:
        raise ValueError("Filename must be specified.")

    cmd = ffRecord(filename=filename, device=device)
    process = None

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while globals.is_recording:
            # You can add a sleep here to reduce CPU usage
            pass

        globals.recording_finished.set()

    except Exception as e:
        logging.error(f"Failed to start recording: {e}")
        raise
    finally:
        if process:
            try:
                process.terminate()
                output, error = process.communicate()
                logging.info(f"Recording output: {output.decode()}")
                if error:
                    logging.error(f"Recording error: {error.decode()}")
                process.wait()
            except Exception as e:
                logging.error(f"Error terminating recording process: {e}")


def play_audio(audio_buffer):
    # Load the audio file using pydub
    audio = AudioSegment.from_file(audio_buffer)

    # Play the audio
    play_obj = sa.play_buffer(
        audio.raw_data,
        num_channels=audio.channels,
        bytes_per_sample=audio.sample_width,
        sample_rate=audio.frame_rate,
    )

    # Wait for playback to finish before exiting
    play_obj.wait_done()


async def async_play_audio(audio_buffer):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, play_audio, audio_buffer)
