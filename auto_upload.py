import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class GitAutoUploader(FileSystemEventHandler):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def on_any_event(self, event):
        if event.is_directory and ".git" in event.src_path:
            return  # Ignore .git directory events
        print(f"File changed: {event.src_path}")
        self.commit_and_push()

    def commit_and_push(self):
        try:
            # Check for changes before committing
            result = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo_path, capture_output=True, text=True, check=True)
            if not result.stdout.strip():
                print("No changes to commit.")
                return

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