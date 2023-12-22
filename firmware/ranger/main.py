import gpio_module
import audio_module
import network_module
import threading
import globals


def main():
    try:
        # Initialize GPIO
        gpio_module.init_gpio()

        # Set up callback for button press
        gpio_module.set_button_callback(on_button_press)

        # Main loop
        while True:
            # The main loop is kept minimal.
            # Most of the work is done in the callbacks and separate threads.
            pass

    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        # Clean up resources
        gpio_module.cleanup_gpio()


def on_button_press():
    audio_file = "recording5.mp3"

    print("Button pressed")

    # Check if currently processing a request
    if globals.is_processing:
        # Cancel the current process
        audio_module.stop_audio()  # Stop playing audio if it's playing
        globals.is_processing = False
        print("Canceled current process. Ready to start new recording.")

    if not globals.is_recording:
        print("Starting recording")
        start_recording(audio_file)
    else:
        print("Stopping recording")
        stop_recording_and_process(audio_file)


def stop_recording_and_process(audio_file):
    globals.is_recording = False
    globals.recording_finished.wait()  # Wait for recording to finish
    globals.recording_finished.clear()

    # Set the processing flag
    globals.is_processing = True

    # Send the audio file to the cloud
    buffer_data = network_module.send_voice_chat(audio_file)

    # Check if still processing before playing
    if globals.is_processing:
        print("Play audio")
        audio_module.play_audio(buffer_data)

    globals.is_processing = False


def start_recording(audio_file):
    globals.is_recording = True
    threading.Thread(
        target=audio_module.record_file, args=(audio_file, "default")
    ).start()


# def stop_recording_and_process(audio_file):
#     globals.is_recording = False
#     globals.recording_finished.wait()  # Wait for recording to finish
#     globals.recording_finished.clear()

#     # Send the audio file to the cloud
#     buffer_data = network_module.send_voice_chat(audio_file)

#     print("Play audio")

#     # Play the audio
#     audio_module.play_audio(buffer_data)


if __name__ == "__main__":
    main()
