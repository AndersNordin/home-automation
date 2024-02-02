import time
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client.from_service_account_json("service-account.json")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file created: {event.src_path}")

            # Generate name based on current date and time
            prefix = "garage-camera"
            current_datetime = datetime.datetime.now()
            object_name = f"{prefix}-{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}"
            upload_blob(bucket_name, event.src_path, object_name)

def start_file_listener(folder_path):
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Usage
folder_path = "data"
bucket_name = "home-surveillance-cam"

start_file_listener(folder_path)
