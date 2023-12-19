import subprocess
import logging


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


def record_file_async(filename, device="default"):
    if filename is None:
        raise ValueError("Filename must be specified.")

    cmd = ffRecord(filename=filename, device=device)
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        logging.error(f"Failed to start recording: {e}")
        raise


def record_file(filename, wait, device="default"):
    if wait is None:
        raise ValueError("Wait callback must be specified.")

    process = record_file_async(filename, device)
    try:
        wait()
    except Exception as e:
        logging.error(f"Error during recording wait function: {e}")
    finally:
        try:
            process.terminate()
            output, error = process.communicate()
            logging.info(f"Recording output: {output.decode()}")
            if error:
                logging.error(f"Recording error: {error.decode()}")
            process.wait()
        except Exception as e:
            logging.error(f"Error terminating recording process: {e}")


def ffPlay(filename=None):
    cmd = ["ffplay", "-nodisp", "-autoexit", "-hide_banner"]
    if filename is not None:
        cmd.append(filename)
    return cmd


def play_file_async(filename_or_data):
    if isinstance(filename_or_data, (bytes, bytearray)):
        cmd = ffPlay()
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, bufsize=0)

        # Write the byte array to ffplay's stdin and close it to avoid hanging
        try:
            process.stdin.write(filename_or_data)
            process.stdin.flush()
        finally:
            process.stdin.close()
        return process

    if isinstance(filename_or_data, str):
        cmd = ffPlay(filename=filename_or_data)
        return subprocess.Popen(cmd)

    raise ValueError("Must be a filename or byte-like object")


def play_file(filename_or_data):
    process = play_file_async(filename_or_data)
    process.wait()
