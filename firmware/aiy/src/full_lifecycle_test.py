import RPi.GPIO as GPIO
import pyaudio
import wave
import requests
import threading

# Configuration
BUTTON_PIN = 17  # GPIO pin number for the button
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5  # Max recording duration, can be controlled by button
AUDIO_FILE = "recording.wav"
CLOUD_FUNCTION_URL = "https://your-cloud-function-url"

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Recording state
is_recording = False
stop_recording = threading.Event()


def record_audio():
    global is_recording
    is_recording = True
    stop_recording.clear()

    stream = audio.open(
        format=AUDIO_FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    frames = []

    while not stop_recording.is_set():
        data = stream.read(CHUNK)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Save the recorded data as a WAV file
    with wave.open(AUDIO_FILE, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(AUDIO_FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    is_recording = False
    send_to_cloud(AUDIO_FILE)


def send_to_cloud(file_path):
    with open(file_path, "rb") as audio_file:
        files = {"file": audio_file}
        response = requests.post(CLOUD_FUNCTION_URL, files=files)
        print(f"File uploaded, server responded: {response.text}")


def button_callback(channel):
    global is_recording
    if not is_recording:
        threading.Thread(target=record_audio).start()
    else:
        stop_recording.set()


# Add event listener to the button
GPIO.add_event_detect(
    BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300
)

try:
    while True:
        # Main loop does nothing, just waiting for button presses
        pass
except KeyboardInterrupt:
    print("Program stopped by user")
finally:
    GPIO.cleanup()
    audio.terminate()
