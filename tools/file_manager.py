import os
import platform
from pathlib import Path


class Folders:
    def get_download_folder():
        # Get the current operating system
        current_platform = platform.system()

        with open("path.txt", "w") as folder:
        # For Windows
            if current_platform == "Windows":
                # Windows typically stores downloads in the user's "Downloads" folder under the user directory
                download_folder = str(Path(os.path.expanduser("~")) / "Downloads")
                # folder.write(download_folder)

            # For macOS
            elif current_platform == "Darwin":  # macOS
                # macOS also stores downloads under the user's home directory
                download_folder = str(Path(os.path.expanduser("~")) / "Downloads")
                # folder.write(download_folder)

            # For Linux
            elif current_platform == "Linux":
                # Linux can vary, but commonly the "Downloads" folder is under the home directory
                download_folder = str(Path(os.path.expanduser("~")) / "Downloads")
                # folder.write(download_folder)

            else:
                raise ValueError("Unsupported platform")
            # download_folder = "/home/guidas/Documents"
            # Return the download folder path
            return download_folder
