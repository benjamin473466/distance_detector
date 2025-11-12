import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class GitAutoUploader(FileSystemEventHandler):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def on_modified(self, event):
        if event.is_directory:
            return
        print(f"File modified: {event.src_path}")
        self.commit_and_push()

    def on_created(self, event):
        if event.is_directory:
            return
        print(f"File created: {event.src_path}")
        self.commit_and_push()

    def commit_and_push(self):
        try:
            subprocess.run(["git", "add", "-A"], cwd=self.repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "Auto-commit changes"], cwd=self.repo_path, check=True)
            subprocess.run(["git", "push"], cwd=self.repo_path, check=True)
            print("Changes pushed to GitHub.")
        except subprocess.CalledProcessError as e:
            print(f"Error during Git operation: {e}")

if __name__ == "__main__":
    repo_path = os.path.dirname(os.path.abspath(__file__))
    event_handler = GitAutoUploader(repo_path)
    observer = Observer()
    observer.schedule(event_handler, path=repo_path, recursive=True)
    print("Monitoring for file changes. Press Ctrl+C to stop.")
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()