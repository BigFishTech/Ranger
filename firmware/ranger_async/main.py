import asyncio
import keyboard
import time
import subprocess
import os

import network_module
import audio_module


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
    keyboard.add_hotkey("space", button_pressed(handler))
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())


# import asyncio
# import keyboard
# import time


# class ButtonHandler:
#     def __init__(self, loop):
#         self.loop = loop
#         self.current_task = None
#         self.running_first_task = False
#         self.running_second_task = False
#         self.last_button_press = 0
#         self.debounce_interval = 1.0  # seconds

#     async def first_click_task(self):
#         self.running_first_task = True
#         print("First click task running.")
#         while True:
#             await asyncio.sleep(1)

#     async def second_click_task(self):
#         print("Second click task running.")
#         await asyncio.sleep(5)
#         print("Second click task completed.")
#         self.running_second_task = False

#     def start_new_task(self):
#         current_time = time.time()
#         if current_time - self.last_button_press < self.debounce_interval:
#             print("Button press ignored due to debouncing.")
#             return

#         self.last_button_press = current_time

#         if (
#             self.current_task
#             and not self.current_task.done()
#             and self.running_second_task
#         ):
#             self.running_second_task = False
#             self.current_task.cancel()
#             print("Cancelled second click task.")
#             return

#         if not self.running_first_task:
#             self.current_task = asyncio.run_coroutine_threadsafe(
#                 self.first_click_task(), self.loop
#             )
#             self.running_first_task = True
#         else:
#             self.running_first_task = False
#             self.current_task = asyncio.run_coroutine_threadsafe(
#                 self.second_click_task(), self.loop
#             )
#             self.running_second_task = True


# def button_pressed(handler):
#     return lambda: handler.start_new_task()


# async def main():
#     loop = asyncio.get_running_loop()
#     handler = ButtonHandler(loop)
#     keyboard.add_hotkey("space", button_pressed(handler))
#     await asyncio.Future()


# if __name__ == "__main__":
#     asyncio.run(main())


# is_recording = False
# current_task = None
# debounce_period = 0.3  # 300 milliseconds
# button_pressed_event = asyncio.Event()

# async def on_button_press():
#     global is_recording, current_task

#     # Debouncing logic
#     button_pressed_event.set()
#     await asyncio.sleep(debounce_period)
#     if not button_pressed_event.is_set():
#         return  # Another press occurred during the debounce period
#     button_pressed_event.clear()

#     # Cancel any ongoing task
#     if current_task:
#         await cancel_current_task()

#     # Toggle the recording state
#     is_recording = not is_recording

#     if is_recording:
#         # Start a new recording task
#         current_task = asyncio.create_task(record_audio_async("audio.mp3"))
#     else:
#         # Stop recording and start processing the audio
#         current_task = asyncio.create_task(send_audio_and_play_response("audio.mp3"))

#     # Await the current task if necessary
#     if current_task:
#         await current_task

# async def cancel_current_task():
#     global current_task
#     if current_task and not current_task.done():
#         current_task.cancel()
#         try:
#             # Await the task to handle any exceptions it might raise
#             await current_task
#         except asyncio.CancelledError:
#             # The task has been cancelled, which is expected
#             pass
#         finally:
#             current_task = None

# async def main():
#     global current_task
#     while True:
#         await on_button_press()

#         if is_recording:
#             # Logic to handle the end of recording and sending audio
#             current_task = asyncio.create_task(send_audio_and_play_response("audio.mp3"))
#             await current_task
#         else:
#             # Logic to start recording
#             current_task = asyncio.create_task(record_audio_async("audio.mp3"))
#             await current_task


# if __name__ == "__main__":
#     asyncio.run(main())


# def main():
#     try:
#         # Initialize GPIO
#         gpio_module.init_gpio()

#         # Set up callback for button press
#         gpio_module.set_button_callback(on_button_press)

#         # Main loop
#         while True:
#             # The main loop is kept minimal.
#             # Most of the work is done in the callbacks and separate threads.
#             pass

#     except KeyboardInterrupt:
#         print("Program terminated by user")
#     finally:
#         # Clean up resources
#         gpio_module.cleanup_gpio()


# def on_button_press():
#     audio_file = "recording5.mp3"

#     print("Button pressed")

#     # Check if currently processing a request
#     if globals.is_processing:
#         # Cancel the current process
#         audio_module.stop_audio()  # Stop playing audio if it's playing
#         globals.is_processing = False
#         print("Canceled current process. Ready to start new recording.")

#     if not globals.is_recording:
#         print("Starting recording")
#         start_recording(audio_file)
#     else:
#         print("Stopping recording")
#         stop_recording_and_process(audio_file)


# def stop_recording_and_process(audio_file):
#     globals.is_recording = False
#     globals.recording_finished.wait()  # Wait for recording to finish
#     globals.recording_finished.clear()

#     # Set the processing flag
#     globals.is_processing = True

#     # Send the audio file to the cloud
#     buffer_data = network_module.send_voice_chat(audio_file)

#     # Check if still processing before playing
#     if globals.is_processing:
#         print("Play audio")
#         audio_module.play_audio(buffer_data)

#     globals.is_processing = False


# def start_recording(audio_file):
#     globals.is_recording = True
#     threading.Thread(
#         target=audio_module.record_file, args=(audio_file, "default")
#     ).start()


# # def stop_recording_and_process(audio_file):
# #     globals.is_recording = False
# #     globals.recording_finished.wait()  # Wait for recording to finish
# #     globals.recording_finished.clear()

# #     # Send the audio file to the cloud
# #     buffer_data = network_module.send_voice_chat(audio_file)

# #     print("Play audio")

# #     # Play the audio
# #     audio_module.play_audio(buffer_data)


# if __name__ == "__main__":
#     main()
