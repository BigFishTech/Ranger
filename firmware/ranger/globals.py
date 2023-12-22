import threading

is_recording = False
recording_finished = threading.Event()
is_processing = False
