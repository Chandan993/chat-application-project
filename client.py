import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import pyaudio
import wave

HOST = '127.0.0.1'
PORT = 1234

THEMES = {
    "Default": {
        "bg_primary": "#F0F0F0", 
        "bg_secondary": "white",
        "fg_primary": "black",
        "fg_secondary": "black",
        "button_bg": "#4CAF50",  
        "button_fg": "white",
        "dropdown_bg": "white",  
        "dropdown_fg": "black" 
    },
    "Dark": {
        "bg_primary": "#121212", 
        "bg_secondary": "#1F1F1F", 
        "fg_primary": "white",
        "fg_secondary": "white",
        "button_bg": "#2196F3",  
        "button_fg": "white",
        "dropdown_bg": "#1F1F1F",  
        "dropdown_fg": "white"   
    },
    "Ocean": {
        "bg_primary": "#81D4FA",  
        "bg_secondary": "#E3F2FD",  
        "fg_primary": "black",
        "fg_secondary": "black",
        "button_bg": "#1976D2",  
        "button_fg": "white",
        "dropdown_bg": "#E3F2FD",  
        "dropdown_fg": "black"      
    },
    "Sunset": {
        "bg_primary": "#FFAB91",  
        "bg_secondary": "#FFE0B2",  
        "fg_primary": "black",
        "fg_secondary": "black",
        "button_bg": "#FF5722",  
        "button_fg": "white",
        "dropdown_bg": "#FFE0B2",  
        "dropdown_fg": "black"      
    }
}

current_theme = "Default"  

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def add_message(message, bg_color):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, '\n')  
    message_box.window_create(tk.END, window=tk.Label(message_box, text=message, bg=bg_color, padx=10, pady=5, borderwidth=1, relief="solid"))
    message_box.see(tk.END)  
    message_box.config(state=tk.DISABLED)

def connect():
    try:
        client.connect((HOST, PORT))
        print("Successfully connected to server")
        add_message("[SERVER] Successfully connected to the server", "light grey")
    except:
        messagebox.showerror("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}")

    username = username_textbox.get()
    if username != '':
        client.sendall(username.encode())
    else:
        messagebox.showerror("Invalid username", "Username cannot be empty")

    threading.Thread(target=listen_for_messages_from_server, args=(client, )).start()

    username_textbox.config(state=tk.DISABLED)
    username_button.config(state=tk.DISABLED)

def send_message():
    message = message_textbox.get()
    if message != '':
        client.sendall(message.encode())
        add_message(message, "lightblue")  
        message_textbox.delete(0, len(message))
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")

def change_theme(event):
    global current_theme
    current_theme = theme_var.get()
    apply_theme(current_theme)

def apply_theme(theme_name):
    theme = THEMES[theme_name]
    root.configure(bg=theme["bg_primary"])

    top_frame.configure(bg=theme["bg_secondary"])
    middle_frame.configure(bg=theme["bg_primary"])
    bottom_frame.configure(bg=theme["bg_secondary"])

    username_label.configure(bg=theme["bg_secondary"], fg=theme["fg_primary"])
    username_textbox.configure(bg=theme["bg_secondary"], fg=theme["fg_primary"])
    username_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])

    message_textbox.configure(bg=theme["bg_secondary"], fg=theme["fg_primary"])
    message_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])

    message_box.configure(bg=theme["bg_primary"], fg=theme["fg_primary"])

    theme_menu['menu'].config(bg=theme["dropdown_bg"], fg=theme["dropdown_fg"])

def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    print("Recording...")
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def send_audio():
    threading.Thread(target=record_audio).start()
    messagebox.showinfo("Recording", "Recording audio...")

def listen_for_messages_from_server(client):
    while True:
        message = client.recv(2048).decode('utf-8')
        if message != '':
            username = message.split("~")[0]
            content = message.split('~')[1]

            add_message(f"[{username}] {content}", "lightgreen")  
        else:
            messagebox.showerror("Error", "Message received from client is empty")

root = tk.Tk()
root.geometry("500x600")
root.title("Chat Application")
root.resizable(False, False)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

top_frame = tk.Frame(root, width=600, height=100)
top_frame.grid(row=0, column=0, sticky=tk.NSEW)

middle_frame = tk.Frame(root, width=600, height=400)
middle_frame.grid(row=1, column=0, sticky=tk.NSEW)

bottom_frame = tk.Frame(root, width=600, height=100)
bottom_frame.grid(row=2, column=0, sticky=tk.NSEW)

username_label = tk.Label(top_frame, text="Enter username:")
username_label.pack(side=tk.LEFT, padx=10)

username_textbox = tk.Entry(top_frame)
username_textbox.pack(side=tk.LEFT)

username_button = tk.Button(top_frame, text="Join", command=connect)
username_button.pack(side=tk.LEFT, padx=15)

message_textbox = tk.Entry(bottom_frame)
message_textbox.pack(side=tk.LEFT, padx=10)

message_button = tk.Button(bottom_frame, text="Send", command=send_message)
message_button.pack(side=tk.LEFT, padx=10)

voice_button = tk.Button(bottom_frame, text="Record", command=send_audio)
voice_button.pack(side=tk.LEFT, padx=10,)

message_box = scrolledtext.ScrolledText(middle_frame, width=67, height=26.5)
message_box.pack(side=tk.TOP)

theme_var = tk.StringVar(root)
theme_var.set("Default")
theme_menu = tk.OptionMenu(root, theme_var, *THEMES.keys(), command=change_theme)
theme_menu.grid(row=3, column=0, pady=10, sticky="ew")

apply_theme(current_theme)

def main():
    root.mainloop()

if __name__ == '__main__':
    main()
