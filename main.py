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
    # Open a file dialog to select a directory
    path = filedialog.askdirectory()
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
        print("No path selected.")
        with open(output_dir, "r") as path:
            path = path.read().strip()
            print(path)
            list_box.configure(state=DISABLED)
            messagebox.showerror("Error", "no path")
            return None




def paste_from_clipboard():
    # clear Input before pasting a new link
    clear_entry()
    status_label.configure(text="Thanks for using GDYtube!", text_color="white", fg_color="blue")
    list_box.delete(0, 'end') 
    

    clipboard_data = root.clipboard_get()
    url_input_field.insert(0, clipboard_data)
    check_entry_content()
    
def check_selection(event):
    selected_indices = list_box.curselection()

    if len(selected_indices) == 0:
        print(f"{len(selected_indices)} item is selected")

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
        # print(selected_option.get())
        # Get list of video links 
        playlist_item_by_id = api.get_playlist_items( 
            playlist_id=playlist_id, count=None, return_json=True) 
        

        # Iterate through all video links and insert into listbox
        for index, videoid in enumerate(playlist_item_by_id['items']):
            video_id = videoid['contentDetails']['videoId']
            video_title = videoid['snippet']['title']
        
            list_box.insert(END, f" {str(index+1)}. {video_title}")
            

    elif "youtu.be" in url_input_field.get():
        video_id = url_input_field.get()[len("https://youtu.be/"):]
        
        # Get the video and it title
        video_item = api.get_video_by_id(video_id=video_id, return_json=True)
        video_info =video_item["items"][0]["snippet"]
        video_title =video_info["title"]
        
        print(video_id) 
        list_box.insert(END, f"{video_title}")
        
    elif "youtube" in url_input_field.get() and "watch" in url_input_field.get():
        video_id = url_input_field.get()[len("https://www.youtube.com/watch?v="):]
        # Get the video and it title
        print("yes",video_id) 
    
        video_item = api.get_video_by_id(video_id=video_id, return_json=True)
        # print(video)

        video_info =video_item["items"][0]["snippet"]
        video_title =video_info["title"]
        
        list_box.insert(END, f"{video_title}")
    
    else:
        not_supported_link = url_input_field.get()
        list_box.insert(END, not_supported_link)
        status_label.configure(text="URL not supported", text_color="white", fg_color="red")


    # The list become clickable based on the state of the Choose path button
    if get_path.cget("state") == "normal":
        list_box.configure(state=NORMAL)
        select_all_checkbox_var.set(0)
        print("yes")
    if get_path.cget("state") == "disabled":
        select_all_checkbox_var.set(0)
        checkbutton_state()
        list_box.configure(state=DISABLED)
        get_path.configure(state=NORMAL)
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
    
    status_label.configure(text="About to start downloading!", text_color="white", fg_color="blue")
    # resolution = resolution_var.get()
    # print(resolution)

    connection_checker()

    download_start.configure(state="disabled") 
    get_path.configure(state="disabled")
    get_videos.configure(state="disabled") 

        # Pack the labels and progress bar only when the download button is clicked


    # Iterate through all selected videos 
    # Counter variable to keep track of position number
    # position = 1
    for i in list_box.curselection():
        video_id = ""
        video_title = list_box.get(i)

        if "youtu.be" in url_input_field.get():
            video_id = url_input_field.get()[len("https://youtu.be/"):]
        
            print(video_id)

        # if selected_option.get() == "Enter Playlist URL":
            
        # print(video)
        # video_info =video_item["items"][0]["snippet"]
    
            
        elif "youtube" in url_input_field.get() and "playlist" in url_input_field.get(): 
            playlist_id = url_input_field.get()[len( 
                "https://www.youtube.com/playlist?list="):]
            # print(selected_option.get())
            # Get list of video links 
            # playlist_item_by_id = api.get_playlist_items(playlist_id=playlist_id, count=None, return_json=True) 
            video_id = playlist_item_by_id['items'][i]['contentDetails']['videoId']
            print(video_id) 
            


        elif "youtube" in url_input_field.get() and "watch" in url_input_field.get():
            video_id = url_input_field.get()[len("https://www.youtube.com/watch?v="):]
        
            print(video_id)

        else:
            unsupported_link = url_input_field.get()



            

        link = f"https://www.youtube.com/watch?v={video_id}"
        yt_obj = YouTube(link, on_progress_callback=on_progress)

        # video_title = yt_obj.title  # Get the video title
        stream = yt_obj.streams.get_highest_resolution()
        # stream_url = stream.url

        # # print(f"This is the url: {stream_url}")
        # video_title = stream.title

        # Handling Unwanted characters in title
        video_title = Security().remove_characters(input_string=str(video_title).split(".")[0], characters=["/", "|", "\n", "#", "\\", "%"])[0]
        filename = video_title + ".mp4"
        print(video_title)
        # str(video_title).split(".")[0]
        

        filters = yt_obj.streams.filter(progressive=True, file_extension='mp4') 

        output_path = ""
        # download the highest quality video 
        with open(output_dir, "r") as path_file:
            output_path = path_file.readline()
            print(output_path)

        existing_bytes = get_existing_bytes(output_path=filename)
        # if existing_bytes_in_mb is not None:
        #     print(f"Existing bytes: {existing_bytes}")
        # else:
        #     print("MB No partial download found.")

        # if existing_bytes is not None:
        #     print(f"Existing bytes: {existing_bytes}")
        #     # filename_prefix = str(video_title).split(".")[0] + ". "
        #     connection_checker()
        #     status_label.configure(text="Downloading!", text_color="white", fg_color="blue")
        #     resume_download(url=stream_url, filename=filename)
        #     print("Download completed successfully!")
        # elif existing_bytes is None:
        #     print("No partial download found.")

        
        connection_checker()
        status_label.configure(text="Downloading!", text_color="white", fg_color="blue")

        
        # filters.get_highest_resolution().download(output_path=output_path, filename=filename)
        filters.get_highest_resolution().download(output_path=output_path)
        # filters.get_by_resolution(resolution=resolution).download(output_path=output_path, filename_prefix=str(video_title).split(".")[0] + ". ")

        status_label.configure(text="Downloaded!", text_color="white", fg_color="green")

        # Increment position counter
        # position += 1

    # messagebox.showinfo("Success", "Video Successfully downloaded") 
    download_start.configure(state="normal") 
    get_path.configure(state="normal")
    get_videos.configure(state="normal") 

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
        existing_bytes = get_existing_bytes(filename)  # Replace with your actual partial file name
        headers = {'Range': f'bytes={existing_bytes}-'} if existing_bytes else {}
        with requests.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded_bytes = existing_bytes

            # Extract the filename from the URL
            # filename = os.path.basename(url)

            with open(filename, 'ab') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
                    downloaded_bytes += len(chunk)
                    bytes_remaining = total_size - downloaded_bytes
                    # print(f"Remaining bytes: {bytes_remaining} / {total_size} ({100 * downloaded_bytes / total_size:.2f}%)")
                    bytes_downloaded = total_size - bytes_remaining
                    percentage_completed = bytes_downloaded / total_size * 100
                    percentage = int(percentage_completed)
                    print(percentage)
                    progress_label.configure(text=str(int(percentage_completed)) + "%")
                    progress_label.update()
                    progress_bar.set(float(percentage_completed / 100))


        print(f"Download resumed successfully! Saved as {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

def download_it(url):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        downloaded_bytes = 0

        # Extract the filename from the URL
        filename = os.path.basename(url)

        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
                downloaded_bytes += len(chunk)
                bytes_remaining = total_size - downloaded_bytes
                # print(f"Remaining bytes: {bytes_remaining} / {total_size} ({100 * downloaded_bytes / total_size:.2f}%)")
                bytes_downloaded = total_size - bytes_remaining
                percentage_completed = bytes_downloaded / total_size * 100
                percentage = int(percentage_completed)
                print(percentage)

def get_existing_bytes(output_path):
    try:
        # Open the partially downloaded file in binary mode
        with open(output_path, "rb") as file:
            # Get the file size (total bytes)
            total_bytes = len(file.read())
            return total_bytes
    except FileNotFoundError:
        # If the file doesn't exist (no partial download), return None
        return None

# call back function to update the progress

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_completed = bytes_downloaded / total_size * 100
    print(percentage_completed)
    progress_label.configure(text=str(int(percentage_completed)) + "%")
    progress_label.update()
    progress_bar.set(float(percentage_completed / 100))

    
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
root.iconphoto(False, PhotoImage(file="app_data/favicon.png"))



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

