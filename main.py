# Import Required Modules 
from CTkListbox import CTkListbox
import customtkinter as ctk
from CTkListbox import *
from tkinter import ttk
from tkinter import *
from pyyoutube import Api 
from pytube import YouTube, Playlist
from threading import Thread 
from tkinter import messagebox
from tkinter import filedialog
import errno, socket, ssl
import requests
import os
from dotenv import load_dotenv
from tools.security import Security
import logging
from pytube.exceptions import PytubeError
from urllib.error import HTTPError
from urllib.parse import urlparse, parse_qs
import yt_dlp
import platform
from pathlib import Path
import time
from tools.file_manager import Folders


# Set up logging (optional)
# logging.basicconfigure(level=logging.DEBUG)

load_dotenv(".env")

output_dir = "path.txt"



# Network errors, usually related to DHCP or wpa_supplicant (Wi-Fi).
NETWORK_ERRNOS = frozenset((
    errno.ENETUNREACH,  # "Network is unreachable"
    errno.ENETDOWN,  # "Network is down"
    errno.ENETRESET,  # "Network dropped connection on reset"
    errno.ENONET,  # "Machine is not on the network"
))

def is_connection_err(exc):
    """Return True if an exception is connection-related."""
    if isinstance(exc, ConnectionError):
        # https://docs.python.org/3/library/exceptions.html#ConnectionError
        # ConnectionError includes:
            # * BrokenPipeError (EPIPE, ESHUTDOWN)
        # * ConnectionAbortedError (ECONNABORTED)
        # * ConnectionRefusedError (ECONNREFUSED)
        # * ConnectionResetError (ECONNRESET)
        return True
    if isinstance(exc, socket.gaierror):
        # failed DNS resolution on connect()
        return True
    if isinstance(exc, (socket.timeout, TimeoutError)):
        # timeout on connect(), recv(), send()
        return True
    if isinstance(exc, OSError):
        # ENOTCONN == "Transport endpoint is not connected"
        return (exc.errno in NETWORK_ERRNOS) or (exc.errno == errno.ENOTCONN)
    if isinstance(exc, ssl.SSLError):
        # Let's consider any SSL error a connection error. Usually this is:
            # * ssl.SSLZeroReturnError: "TLS/SSL connection has been closed"
        # * ssl.SSLError: [SSL: BAD_LENGTH]
        return True
    return False


def check_internet():
    try:
        response = requests.get("https://www.bing.com", timeout=5)
        return response.status_code == 200
    except Exception as e:
        # messagebox.showerror("Error", "Check your connection\nAnd click OK to continue")
        
        return False





def check_entry_content():
    if url_input_field.get():
        get_videos.configure(state=NORMAL)  # Enable the button
    else:
        download_start.configure(state=DISABLED)
        get_path.configure(state=DISABLED)
        get_videos.configure(state=DISABLED)  # Disable the button
        list_box.delete(0, END)

def clear_entry():
    url_input_field.delete(0, END)  # Clear the entry's content
    check_entry_content()
    select_all_checkbox.configure(state=DISABLED)


def get_path():
    default_dir = Folders.get_download_folder()
    
    
    

    # Open a file dialog to select a directory
    
    # Filter out hidden files and folders (those starting with '.')
    def filter_hidden_files_and_dirs(file_list):
        return [f for f in file_list if not f.startswith('.')]

    # Get the list of files and directories in the default directory
    try:
        entries = os.listdir(default_dir)
        visible_entries = filter_hidden_files_and_dirs(entries)
    except PermissionError:
        visible_entries = []  # Handle permission errors (e.g., inaccessible directories)

    # If needed, you could display or process `visible_entries` before opening the dialog.
    # print("Visible files and folders:", visible_entries)
    
    # Open the file dialog
    path = filedialog.askdirectory(initialdir=default_dir, title="Select a Folder")
   

  
    if path:
        # download_videos(path=path)
        print(f"Selected path: {path}")
        with open(output_dir, "w") as path_file:
            path_file.write(path)
    
        # The listbox and select all check button become clickable only if the "choose" path button is clicked
        list_box.configure(state=NORMAL)
        select_all_checkbox.configure(state=NORMAL)

        return path

    else:
        print(f"No path selected. using the default {default_dir}")
        with open(output_dir, "w") as output_path:
            path = output_path.write(default_dir)
            print(path)
            list_box.configure(state=NORMAL)
            # messagebox.showerror("Error", "no path")
            return path




def paste_from_clipboard():
    # clear Input before pasting a new link
    clear_entry()
    status_label.configure(text="Thanks for using GDYtube!", text_color="white", fg_color="blue")
    list_box.delete(0, 'end') 
    

    clipboard_data = root.clipboard_get()
    url_input_field.insert(0, clipboard_data)
    check_entry_content()
    get_list_videos()
    
def check_selection(event):
    selected_indices = list_box.curselection()

    if len(selected_indices) == 0:
        print(f"{len(selected_indices)} item is selected")
        # select_all_checkbox.configure(state=NORMAL)
        select_all_checkbox_var.set(0)


    if selected_indices and len(selected_indices) == list_box.size():
        select_all_checkbox_var.set(1)
        print("All items are selected!")


    if selected_indices and len(selected_indices) != list_box.size():
        if len(selected_indices) == 1:
            print(f"{len(selected_indices)} item is selected!")

        else:
            select_all_checkbox_var.set(0)
            print(f"{len(selected_indices)} items are selected!")

    if selected_indices:
        download_start.configure(state=NORMAL)  # Enable the button
    else:
        download_start.configure(state=DISABLED)  # Disable the button


def select_all():
    state = select_all_checkbox_var.get()

def checkbutton_state():
    state = select_all_checkbox_var.get()
    # print(get_videos_button)

    num_items = list_box.size()
    if state == 1:
        print(f"Checkbutton state: {state}")
        
        # Select all items
        list_box.selection_set(0, num_items - 1)
        download_start.configure(state=NORMAL)  # Enable the button
        
    else:
        list_box.selection_clear(0, num_items - 1)
        download_start.configure(state=DISABLED)  # Disable the button

def straight_download(url=None):
    from pytube import Playlist

    # Input the URL of the playlist
    playlist_url = input('Enter the URL of the playlist: ')
    playlist = Playlist(playlist_url)

    # Print the number of videos in the playlist
    print(f'Number of videos in the playlist: {len(playlist.video_urls)}')

    # Download each video in the playlist
    for video_url in playlist.video_urls:
        print(video_url)

# straight_download()
def get_list_videos(): 
    status_label.configure(text="Getting your video or videos", text_color="white", fg_color="blue")
    # progress_bar.pack()

    list_box.delete(0, 'end') 

    # Call the function to check internet connection
    while check_internet() == False:
        print("No internet connection.")
        messagebox.showerror("Error", "Check your connection\nAnd click OK to continue")
        check_internet()
    else:
        print("Internet connection is available.")
        if get_path.cget("state") == "disabled":
            select_all_checkbox_var.set(0)
            checkbutton_state()
            list_box.configure(state=NORMAL)
            

    global playlist_item_by_id 
    # Create API Object 
    api = Api(api_key=os.environ.get("API_KEY")) 
    # try:       
            

    if "youtube" in url_input_field.get() and "playlist" in url_input_field.get(): 
        playlist_id = url_input_field.get()[len( 
            "https://www.youtube.com/playlist?list="):]
        print(playlist_id) 

        # Get list of video links 
        playlist_item_by_id = api.get_playlist_items( 
            playlist_id=playlist_id, count=None, return_json=True) 
        

        # Iterate through all video links and insert into listbox
        for index, videoid in enumerate(playlist_item_by_id['items']):
            video_id = videoid['contentDetails']['videoId']
            video_title = videoid['snippet']['title']
        
            list_box.insert(END, f" {str(index+1)}. {video_title}")
            
    elif "youtube.com/watch" in url_input_field.get():
        query_params = parse_qs(urlparse(url_input_field.get()).query)
        video_id = query_params.get('v', [None])[0]
        
        # Get the video and it title
        print("yes",video_id) 
    
        video_item = api.get_video_by_id(video_id=video_id, return_json=True)
        # print(video)

        video_info =video_item["items"][0]["snippet"]
        video_title =video_info["title"]
        
        list_box.insert(END, f"{video_title}")


    elif "youtu.be" in url_input_field.get():
        video_id = url_input_field.get().split('/')[-1].split('?')[0]  # Extract the part after the last '/' and before '?'
        print(f"Video ID: {video_id}")
        
        # Get the video and it title
        video_item = api.get_video_by_id(video_id=video_id, return_json=True)
        video_info =video_item["items"][0]["snippet"]
        video_title =video_info["title"]
        
        print(video_id) 
        list_box.insert(END, f"{video_title}")
    
        
    
    else:
        not_supported_link = url_input_field.get()
        list_box.insert(END, not_supported_link)
        status_label.configure(text="URL not supported", text_color="white", fg_color="red")


    # The list become clickable based on the state of the Choose path button
    # if get_path.cget("state") == "normal":
    #     list_box.configure(state=NORMAL)
    #     select_all_checkbox_var.set(0)
    #     print("yes")

    if get_path.cget("state") == "disabled":
        


        # Set the output path
        path = ""
        with open(output_dir, "r") as path_file:
            path = path_file.readline().strip()
            print(f"Output path: {path}")
        
        if path != "":
            print(path)
            list_box.configure(state=NORMAL)
            get_path.configure(state=NORMAL)
            select_all_checkbox.configure(state=NORMAL)
        else:

            select_all_checkbox_var.set(0)
            checkbutton_state()
            list_box.configure(state=DISABLED)
            get_path.configure(state=NORMAL)
    
        list_box.configure(state=NORMAL)
        # select_all_checkbox.configure(state=NORMAL)
            # Simulating the exception for demonstration purposes
            # raise pyyoutube.error.PyYouTubeException("YouTubeException(status_code=404,message=The playlist identified with the request's <code>url_input_field</code> parameter cannot be found.)")
    # except Exception as e:
        # #     # Handle the exception
    # #     error_message = str(e)  # Get the error message from the exception
    #     # print(e.with_traceback())
    #     print("No connection")
    #     messagebox.showerror("Error", f"An error occurred:\nVideo cannot be found with that link\nCheck your link")
        # messagebox.showerror("Error", f"An error occurred:\n{error_message}")


def packer(progress_label, progress_bar, status_label):
    progress_label.pack(pady=("5p", "2p"))
    progress_bar.pack(pady=("5p", "2p"))
    status_label.pack(pady=("5p", "2p"))

# packer() 



def threading(): 
    # Call download_videos function 
    t1 = Thread(target=download_videos) 
    t1.start() 

def connection_checker():
    while check_internet() == False:
        print("No internet connection.")
        messagebox.showerror("Error", "Check your connection\nAnd click OK to continue")
    else:
        print("Internet connection is available.")
        if get_path.cget("state") == "disabled":
            select_all_checkbox_var.set(0)
            checkbutton_state()
            list_box.configure(state=NORMAL) 




def download_videos():
    try:
        status_label.configure(text="About to start downloading!", text_color="white", fg_color="blue")
        connection_checker()

        # Disable buttons during download
        download_start.configure(state="disabled")
        get_path.configure(state="disabled")
        get_videos.configure(state="disabled")

        for i in list_box.curselection():
            video_id = ""
            video_title = list_box.get(i)

            # Check if the input is a playlist or a single video
            if "youtube" in url_input_field.get() and "playlist" in url_input_field.get():
                # playlist_url = url_input_field.get()
                # print(f"Downloading playlist: {playlist_url}")
                # links_to_download = [playlist_url]

                playlist_id = url_input_field.get()[len( 
                "https://www.youtube.com/playlist?list="):]
                # print(selected_option.get())
                # Get list of video links 
                # playlist_item_by_id = api.get_playlist_items(playlist_id=playlist_id, count=None, return_json=True) 
                video_id = playlist_item_by_id['items'][i]['contentDetails']['videoId']
                print(video_id) 
                links_to_download = [f"https://www.youtube.com/watch?v={video_id}"]
           
           
            
            elif "youtube.com/watch" in url_input_field.get():
                query_params = parse_qs(urlparse(url_input_field.get()).query)
                video_id = query_params.get('v', [None])[0]
                if video_id:
                    print(f"Video ID: {video_id}")
                else:
                    print("No video ID found.")
                links_to_download = [f"https://www.youtube.com/watch?v={video_id}"]


            # elif "youtube" in url_input_field.get() and "watch" in url_input_field.get():
            #     video_id = url_input_field.get()[len("https://www.youtube.com/watch?v="):]
            #     links_to_download = [f"https://www.youtube.com/watch?v={video_id}"]

            elif "youtu.be" in url_input_field.get():
                video_id = url_input_field.get().split('/')[-1].split('?')[0]  # Extract the part after the last '/' and before '?'
                print(f"Video ID: {video_id}")
                links_to_download = [f"https://www.youtube.com/watch?v={video_id}"]
            else:
                unsupported_link = url_input_field.get()
                print(f"Unsupported link: {unsupported_link}")
                continue  # Skip unsupported links

            # Set the output path
            output_path = ""
            with open(output_dir, "r") as path_file:
                output_path = path_file.readline().strip()
                print(f"Output path: {output_path}")
            


            # yt-dlp configuration
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),  # Save as title.ext
                "noplaylist": False,  # Allow playlists
                "progress_hooks": [on_download_progress],  # Hook for showing progress
                "quiet": False,
                "no_warnings": True,
            }

            # # Download videos
            # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            #     try:
            #         for link in links_to_download:
            #             status_label.configure(text=f"Downloading: {link}", text_color="white", fg_color="blue")
            #             ydl.download([link])
            #             print(f"Downloaded: {link}")
            #     except yt_dlp.utils.DownloadError as e:
            #         print(f"Download error: {e}")

            # Function to download a single link with retry logic
            def download_with_retries(ydl, link, max_retries=3):
                for attempt in range(max_retries):
                    try:
                        status_label.configure(text=f"Downloading: {link} (Attempt {attempt + 1}/{max_retries})",
                                            text_color="white", fg_color="blue")
                        ydl.download([link])
                        print(f"Downloaded: {link}")
                        return True  # Download successful
                    except yt_dlp.utils.DownloadError as e:
                        print(f"Download error on attempt {attempt + 1}: {e}")
                        status_label.configure(text=f"Download error. Trying again...", text_color="white", fg_color="red")
                        time.sleep(2)
                        if attempt < max_retries - 1:
                            time.sleep(1)  # Optional: Wait for 2 seconds before retrying
                return False  # All attempts failed

            # Download videos with retries
            max_retries = 3
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for link in links_to_download:
                    success = download_with_retries(ydl, link)
                    if not success:
                        print(f"Failed to download after {max_retries} attempts: {link}")
                        status_label.configure(text="Downloads Failed!", text_color="white", fg_color="red")
                        time.sleep(2)
                        print("Download Failed!")
                    if success:
                        # Re-enable buttons after the process
                        download_start.configure(state="normal")
                        get_path.configure(state="normal")
                        get_videos.configure(state="normal")

                        status_label.configure(text="All downloads completed!", text_color="white", fg_color="green")
                        print("All downloads completed!")

    except Exception as e:
        print(f"Unexpected error: {e}")
        status_label.configure(text="Error occurred!", text_color="white", fg_color="red")
        download_start.configure(state="normal")
        get_path.configure(state="normal")
        get_videos.configure(state="normal")



# call back function to update the progress


def on_download_progress(d):
    if d['status'] == 'downloading':
        total_size = d.get('total_bytes', None) or d.get('total_bytes_estimate', None)
        bytes_downloaded = d.get('downloaded_bytes', 0)

        if total_size is not None:
            percentage_completed = bytes_downloaded / total_size * 100
            print(f"Progress: {percentage_completed:.2f}%")
            progress_label.configure(text=f"{int(percentage_completed)}%")
            progress_label.update()
            progress_bar.set(float(percentage_completed / 100))
        else:
            print("Unable to determine total size.")
    elif d['status'] == 'finished':
        print("Download finished!")
        progress_label.configure(text="100%")
        progress_bar.set(1.0)


    
# Create Object ( root window)
# root = Tk() 
root = ctk.CTk()


# Title
root.title("GDYtube")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# iconbitmap(): The iconbitmap() method allows you to set an icon for your Tkinter window. It takes the path to an .ico file as its argument. 
# root.iconbitmap("/path/to/your_icon.ico")

# iconphoto(): The iconphoto() method sets the title bar icon for a Tkinter window. You can use various image types, including .png.
# Get the absolute path of the current script (main.py)
script_path = os.path.abspath(__file__)

# Construct the full path to the favicon.png file
favicon_path = os.path.join(os.path.dirname(script_path), 'app_data', 'favicon.png')

# print(f"Full path to favicon.png: {favicon_path}")
root.iconphoto(False, PhotoImage(file=favicon_path))



# Set geometry 
root.geometry('720x480') 
root.minsize(720, 500)
# root.maxsize(1080, 720)


content_frame = ctk.CTkFrame(root)
content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
# Add Label 
header_lable = ctk.CTkLabel(content_frame, text="GUIDASWORLD Youtube Playlist Downloader") 
under_header = ctk.CTkLabel(content_frame, text="Highest resolutions only")

header_lable.pack(pady=("10p", "5p"))
under_header.pack()

# Create a frame to hold playlist or one video radio button
radio_button_frame = ctk.CTkFrame(content_frame)
radio_button_frame.pack()

# Create radio buttons and associate them with the variable
selected_option = StringVar()
# selected_option.set("Enter Playlist URL")  # Set the default value
# option1 = Radiobutton(radio_button_frame, text="Standard", value="Enter video URL", variable=selected_option, command=show_selected)
# option2 = Radiobutton(radio_button_frame, text="Playlist", value="Enter Playlist URL", variable=selected_option, command=show_selected)

# # Pack the radio buttons and label horizontally
# option1.pack(side="left", padx=10)
# option2.pack(side="left", padx=10)


# Create a label to display the selected option
label = ctk.CTkLabel(radio_button_frame, text="Enter The Youtube Video/Playlist URL:")
label.pack(padx=10)

# Add Entry box 
url_input_field = ctk.CTkEntry(content_frame, width=400, height=40) 
url_input_field.pack(pady=5)

# Clear url input field
clear_url = ctk.CTkButton(content_frame, text="Clear link", command=clear_entry)
clear_url.pack(padx=10, pady=10) 

# Create a frame to hold the buttons
button_frame = ctk.CTkFrame(content_frame)
button_frame.pack()



# Create a "Paste" button
paste_button = ctk.CTkButton(button_frame, text="Paste", command=paste_from_clipboard)
paste_button.pack(side="left", padx=10)

# Create a "Get Videos" button
get_videos = ctk.CTkButton(button_frame, text="Get Videos", command=get_list_videos, state=DISABLED)
get_videos.pack(side="left", padx=10)

# Bind the function to the Entry widget
url_input_field.bind("<KeyRelease>", lambda event: check_entry_content())

# Choose a path for video
get_path = ctk.CTkButton(button_frame, text="Choose a path", command=get_path, state=DISABLED)
get_path.pack(side="left", padx=10)

# Create a resolution combo box
# resolutions = ["720p", "360p", "240p"]
# resolution_var = ctk.StringVar()
# resolutions_combobox = ctk.CTkComboBox(content_frame, values=resolutions, variable=resolution_var, button_color="#2d89df")
# # resolutions_combobox = ttk.Combobox(content_frame, values=resolutions, textvariable=resolution_var)
# resolutions_combobox.pack(pady=("10p", "5p"))
# resolutions_combobox.set("720p")


# Create a label and the progress bar to display the download progress
progress_label = ctk.CTkLabel(content_frame, text="0%")
progress_label.pack(pady=("5p", "2p"))


progress_bar = ctk.CTkProgressBar(content_frame, width=400)
progress_bar.set(0.0)
progress_bar.pack(pady=("5p", "2p"))

# # Create a style
# style = ttk.Style()
# style.configure("Rounded.TLabel", borderwidth=0, relief="flat", background="blue")

status_label = ctk.CTkLabel(content_frame, text="Thanks for using GDYtube!", bg_color='blue', width=400)
status_label.pack(pady=("5p", "2p"))


# Create a "Download Start" button
download_start = ctk.CTkButton(button_frame, text="Download Start", command=threading, state=DISABLED)
# download_start = ctk.CTkButton(button_frame, text="Download Start", command=threading, state=DISABLED)
download_start.pack(side="left", padx=10)


# Create a "Quit" button
quit_download = ctk.CTkButton(button_frame, text="Quit", command=quit)
quit_download.pack(side="left", padx=10)


def show_selected():
       # Display the selected option
    label.configure(text=selected_option.get())







# Checkbutton_frame = ctk.CTkFrame(content_frame)
# Checkbutton_frame.pack()

# Create select All checkbox
select_all_checkbox_var = IntVar()  # Variable to store the state
select_all_checkbox = ctk.CTkCheckBox(content_frame, text="Select All", variable=select_all_checkbox_var, command=checkbutton_state, state=DISABLED)
select_all_checkbox.pack(pady=10)

# Add Scrollbar 
scrollbar = Scrollbar(content_frame) 
scrollbar.pack(side=RIGHT, fill=BOTH) 
list_box = Listbox(content_frame, selectmode="multiple") 
list_box.pack(expand=YES, fill="both") 
list_box.configure(yscrollcommand=scrollbar.set) 
scrollbar.configure(command=list_box.yview) 

# Bind the selection event to the check_selection function
list_box.bind("<<ListboxSelect>>", check_selection)





# root = ctk.CTk()

# # Create the "Select All" checkbox
# select_all_checkbox_var = ctk.IntVar()  # Variable to store the state
# select_all_checkbox = ctk.CTkCheckBox(root, text="Select All", variable=select_all_checkbox_var, command=checkbutton_state, state=ctk.DISABLED)
# select_all_checkbox.pack(pady=10)

# # Add a scrollbar
# scrollbar = ctk.CTkScrollbar(root)
# scrollbar.pack(side=ctk.RIGHT, fill=ctk.BOTH)

# # Create the CTkListbox
# list_box = CTkListbox(root, selectmode="multiple")
# list_box.pack(expand=ctk.YES, fill="both")
# list_box.configure(yscrollcommand=scrollbar.set)
# scrollbar.configure(command=list_box.yview)

# # Bind the selection event to the check_selection function
# list_box.bind("<<ListboxSelect>>", check_selection)




# Execute Tkinter 
root.mainloop() 

