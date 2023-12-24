import asyncio
import keyboard
import time
import subprocess

import network_module
import audio_module

"""
This is the main module for the Ranger program. It runs forever, and handles the main
features of the project. Right now, it is simply responsible for the chat functionality.

The chat functionality works as follows: When the button is pressed, the device begins
recording audio from the microphone. When the button is pressed again, the device stops
recording audio, and sends that audio data to a cloud function. The cloud function
sends back the response audio data, which is then played aloud on the device.

There are some significant design decisions made here: 

• Use asyncio for the main loop. This allows the program to run efficiently, and allows
for each button press to be handled as a separate task. This is important because the
button press handler is a blocking function, and we don't want to block the main loop 
from responding to additional button presses. 

• Use ffmpeg to record audio. This allows for efficient audio recording, it works on RPI,
and it allows us to record directly into an efficient format for sending to the cloud.

• Record directly into a webm file. This is the most efficient format for sending to the
cloud function.

• Recieve opus audio data from the cloud function. This is the most efficient format for
sending audio data over the internet, and it is supported by open ai tts.

• Button debouncing. This is important because the user may spam the button.

Run the program with `python main.py`.
"""


class ButtonHandler:
    def __init__(self, loop):
        self.loop = loop
        self.current_task = None
        self.running_first_task = False
        self.running_second_task = False
        self.last_button_press = 0
        self.debounce_interval = 1.0  # seconds
        self.recording_process = None

    async def first_click_task(self):
        """
        This task is run when the button is pressed for the first time. It starts
        recording audio from the microphone using ffmpeg.
        """

        if not self.running_first_task:
            self.running_first_task = True
            print("First click task running - Starting recording.")
            self.recording_process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "avfoundation",
                    "-i",
                    ":2",
                    "-c:a",
                    "libvorbis",
                    "-f",
                    "webm",
                    "output.webm",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,
            )

    async def second_click_task(self):
        """
        This task is run when the button is pressed for the second time. It stops
        recording audio from the microphone, and sends the audio to the cloud.
        """

        print("Second click task running")
        if self.recording_process:
            print("Stopping recording.")
            self.recording_process.stdin.write(b"q")
            self.recording_process.stdin.flush()

            self.recording_process.wait()
            self.recording_process = None

            print("Sending audio to cloud.")
            buffer_data = network_module.send_voice_chat("output.webm")
            print("Play audio")
            # Play the audio
            audio_module.play_audio(buffer_data)

        print("Second click task completed.")
        self.running_second_task = False
        self.running_first_task = False

    def start_new_task(self):
        """
        This function is called when the button is pressed. It starts a new task
        depending on the current state of the button press.
        """

        current_time = time.time()
        if current_time - self.last_button_press < self.debounce_interval:
            print("Button press ignored due to debouncing.")
            return

        self.last_button_press = current_time

        if (
            self.current_task
            and not self.current_task.done()
            and self.running_second_task
        ):
            self.running_second_task = False
            self.current_task.cancel()
            print("Cancelled second click task.")
            return

        if not self.running_first_task:
            self.current_task = asyncio.run_coroutine_threadsafe(
                self.first_click_task(), self.loop
            )
        else:
            self.current_task = asyncio.run_coroutine_threadsafe(
                self.second_click_task(), self.loop
            )
            self.running_second_task = True


def button_pressed(handler):
    return lambda: handler.start_new_task()


async def main():
    loop = asyncio.get_running_loop()
    handler = ButtonHandler(loop)

    # Typically this will be a GPIO button press, but for testing we use the spacebar
    keyboard.add_hotkey("space", button_pressed(handler))
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
