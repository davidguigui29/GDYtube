import os
import shutil
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

class Files:

    def ensure_env_file_exists(env_file=".env", env_sample_file="env.sample"):
        """
        Ensures that a .env file exists.
        If not, creates it by copying .env.sample.
        """
        
        if not os.path.exists(env_file):  # Check if .env file exists
            if os.path.exists(env_sample_file):  # Check if .env.sample exists
                shutil.copy(env_sample_file, env_file)  # Copy .env.sample to .env
                print(f"Created {env_file} from {env_sample_file}.")
            else:
                print(f"{env_sample_file} not found. Cannot create {env_file}.")
        else:
            print(f"{env_file} already exists.")





    def copy_file(source, destination):
        """
        Copies a file from the source path to the destination path.
        
        Args:
            source (str): The path to the source file.
            destination (str): The path to the destination file.
        
        Returns:
            bool: True if the file was copied successfully, False otherwise.
        """
        try:
            if not os.path.exists(source):
                print(f"Source file '{source}' does not exist.")
                return False
            
            # Ensure the destination directory exists
            destination_dir = os.path.dirname(destination)
            if destination_dir and not os.path.exists(destination_dir):
                os.makedirs(destination_dir, exist_ok=True)
            
            shutil.copy(source, destination)
            print(f"Copied '{source}' to '{destination}'.")
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False


