from pytube import YouTube
import os
from tools.security import Security
import requests
import yt_dlp

class Manager():


    def get_video_ids_from_playlist(playlist_url):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Extract metadata without downloading
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                if 'entries' in info:  # Check if it's a playlist
                    video_ids = [entry['id'] for entry in info['entries']]  # Extract video IDs
                    return video_ids
                else:
                    print("The provided URL is not a playlist.")
                    return []
        except Exception as e:
            print(f"Error: {e}")
            return []



    def get_video_info(url):
        """
        Extracts video IDs from a YouTube playlist or single video URL.
        
        Args:
            url (str): The YouTube URL (playlist or single video).
            
        Returns:
            list: A list of video IDs if it's a playlist.
            str: A single video ID if it's a single video.
            None: If the URL is invalid or unsupported.
        """
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Extract metadata without downloading
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Check if it's a playlist
                if 'entries' in info:  # Playlist contains 'entries'
                    video_ids = [entry['id'] for entry in info['entries']]  # Extract video IDs
                    return video_ids, info

                # If not a playlist, return single video ID
                elif 'id' in info:  # Single video info contains 'id'
                    return info['id'], info

                # If not recognized as playlist or video
                print("The provided URL is not a valid playlist or video.")
                return None

        except Exception as e:
            print(f"Error: {e}")
            return None


    def download_video(self, youtube_object, url, output_path):
        try:
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()
            stream_url = stream.url
            # print(f"This is the url: {stream_url}")
            video_title = stream.title
            video_title = Security().remove_characters(input_string=str(video_title).split(".")[0], characters=["/", "|", "\n", "#", "\\", "%"])[0]
            filename = video_title + ".mp4"
            print(video_title)

            # Check if partial download exists
            # Example usage
            # existing_bytes = get_size_in_mb(video_title + ".mp4")
            existing_bytes = self.get_existing_bytes(filename)
            # if existing_bytes_in_mb is not None:
            #     print(f"Existing bytes: {existing_bytes}")
            # else:
            #     print("MB No partial download found.")

            if existing_bytes is not None:
                print(f"Existing bytes: {existing_bytes}")
                resume_download(stream_url, filename=filename)
                print("Download completed successfully!")
            elif existing_bytes is None:
                print("No partial download found.")

            # # Download the video
            
                stream.download(output_path=output_path, filename=filename)
        except Exception as e:
            print(f"An error occurred: {e}")


    def resume_download(url, filename):
        """
        Resumes a partially downloaded video from the given URL.

        Args:
            url (str): The YouTube video stream URL.
            filename (str): The name of the file to save the downloaded content.

        Returns:
            None
        """
        try:
            existing_bytes = self.get_existing_bytes(filename)  # Replace with your actual partial file name
            headers = {'Range': f'bytes={existing_bytes}-'} if existing_bytes else {}
            response = requests.get(url, headers=headers, stream=True)

            with open(filename, 'ab') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)

            print(f"Download resumed successfully! Saved as {filename}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # # Example usage:
    # video_url = 'https://www.youtube.com/watch?v=YOUR_VIDEO_ID'
    # output_filename = 'partial_file.mp4'
    # resume_download(video_url, output_filename)


    def fetch_or_resume(self, url, filename):
        with open(filename, 'ab') as f:
            headers = {}
            pos = f.tell()
            if pos:
                headers['Range'] = f'bytes={pos}-'
            response = requests.get(url, headers=headers, stream=True)
            # if pos:
            #     validate_as_you_want_(pos, response)  # Validate as needed
            total_size = int(response.headers.get('content-length'))
            for data in tqdm(iterable=response.iter_content(chunk_size=1024), total=total_size // 1024, unit='KB'):
                f.write(data)


    def get_existing_bytes(output_path):
        try:
            # Open the partially downloaded file in binary mode
            with open(output_path, "rb") as file:
                # Get the file size (total bytes)
                total_bytes = len(file.read())
                print(output_path)
                return total_bytes
        except FileNotFoundError:
            # If the file doesn't exist (no partial download), return None
            return None

    def get_size_in_mb(self, file_path):
        try:
            file_size_bytes = os.path.getsize(file_path)
            file_size = file_size_bytes
            file_size_mb = file_size / (1024 * 1024)
            print(file_size)
            print(file_size_mb)
            return file_size
        except FileNotFoundError:
            return None


    # if __name__ == "__main__":
    #     video_url = input("Enter the YouTube video URL: ")
    #     output_directory = ""
    #     download_video(video_url, output_directory)