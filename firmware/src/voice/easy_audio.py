import subprocess


def ffRecord(filename=None, device="default"):
    if filename is None:
        raise ValueError("Filename must be specified.")

    cmd = [
        "ffmpeg",
        "-f",
        "alsa",  # ALSA audio capture
        "-i",
        device,  # Input device
        "-ac",
        "2",  # Number of audio channels
        "-ar",
        "44100",  # Sample rate
        "-ab",
        "192000",  # Audio bit rate
        "-acodec",
        "libmp3lame",  # Audio codec (for WAV and raw formats)
        filename,
    ]

    return cmd


def record_file_async(filename, device="default"):
    if filename is None:
        raise ValueError("Filename must be specified.")

    cmd = ffRecord(filename=filename, device=device)
    return subprocess.Popen(cmd)


def record_file(filename, wait, device="default"):
    if wait is None:
        raise ValueError("Wait callback must be specified.")

    process = record_file_async(filename, device)
    try:
        wait()
    finally:
        process.terminate()
        process.wait()


def ffPlay(filename=None):
    cmd = ["ffplay", "-nodisp", "-autoexit", "-hide_banner"]

    if filename is not None:
        cmd.append(filename)

    return cmd


def play_mp3_async(filename_or_data):
    if isinstance(filename_or_data, (bytes, bytearray)):
        cmd = ffPlay(filename=None)
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        process.stdin.write(filename_or_data)
        return process

    if isinstance(filename_or_data, str):
        cmd = ffPlay(filename=filename_or_data)
        return subprocess.Popen(cmd)

    raise ValueError("Must be filename or byte-like object")


def play_mp3(filename_or_data):
    play_mp3_async(filename_or_data).wait()
