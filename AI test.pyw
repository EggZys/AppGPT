import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from openai import OpenAI
import os
import asyncio

previous_requests = []
keys = None

def load_keys():
    try:
        if os.path.exists('keys.txt'):
            with open('keys.txt', 'r') as f:
                return [line.strip() for line in f]
        else:
            return []
    except Exception as e:
        print(f"Ошибка при загрузке ключей: {e}")
        return []

keys = load_keys()

class ChatApp:
    def __init__(self, master):
        self.master = master
        master.title("Chat App")
        master.configure(bg='#2f2f2f')  # Dark background

        # Load OpenAI API key from file
        self.load_api_key()

        # Create frames for the chat area, input, and status
        self.chat_frame = tk.Frame(master, bg='#2f2f2f')
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        self.input_frame = tk.Frame(master, bg='#2f2f2f')
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_frame = tk.Frame(master, bg='#2f2f2f')
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a text widget for the chat area
        self.chat_area = tk.Text(self.chat_frame, wrap=tk.WORD, state=tk.DISABLED, bg='#2f2f2f', fg='#ffffff')
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        # Create an entry widget for input
        self.input_entry = tk.Entry(self.input_frame, bg='#2f2f2f', fg='#ffffff')
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Create a send button
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, bg='#2f2f2f', fg='#ffffff')
        self.send_button.pack(side=tk.LEFT)

        # Create a button to add API key
        self.add_key_button = tk.Button(self.input_frame, text="Add API Key", command=self.add_api_key_window, bg='#2f2f2f', fg='#ffffff')
        self.add_key_button.pack(side=tk.LEFT)

        # Create a status bar
        self.status_bar = ttk.Label(self.status_frame, text=f"Status: Ready (API Key: {'Loaded' if self.api_key else 'Not Loaded'})", style='Dark.TLabel')
        self.status_bar.pack(fill=tk.X)

    def load_api_key(self):
        self.api_key = None
        if keys:
            self.api_key = keys[0]

    def add_api_key_window(self):
        # Create a new window for adding an API key
        add_key_window = tk.Toplevel(self.master)
        add_key_window.title("Add API Key")
        add_key_window.configure(bg='#2f2f2f')

        # Create a label and entry for adding API key
        add_key_label = tk.Label(add_key_window, text="Add API Key:", bg='#2f2f2f', fg='#ffffff')
        add_key_label.pack(side=tk.TOP)
        add_key_entry = tk.Entry(add_key_window, bg='#2f2f2f', fg='#ffffff')
        add_key_entry.pack(side=tk.TOP)

        # Create a button to add the API key
        add_key_button = tk.Button(add_key_window, text="Add", command=lambda: self.add_api_key(add_key_entry.get()), bg='#2f2f2f', fg='#ffffff')
        add_key_button.pack(side=tk.TOP)

    def add_api_key(self, new_key):
        global keys
        if new_key:
            keys.append(new_key)
            with open('keys.txt', 'a') as f:
                f.write(new_key + '\n')
            self.status_bar.config(text=f"Status: Ready (API Key: {'Loaded'})")
            self.load_api_key()

    def send_message(self):
        # Check if API key is loaded
        if not self.api_key:
            messagebox.showerror("Error", "Please add your OpenAI API key.")
            return

        # Get the message from the input entry
        message = self.input_entry.get()

        # Clear the input entry
        self.input_entry.delete(0, tk.END)

        # Update the chat area
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"You: {message}\n")
        self.chat_area.config(state=tk.DISABLED)

        # Send the message to OpenAI and get a response
        global keys
        max_tries = 14
        retry_delay = 5

        for i in range(max_tries): 
            if not keys:
                print("Ключей нету!")

            key = keys.pop(0)
            try:
                client = OpenAI(api_key=key, base_url="https://api.aimlapi.com/")
                previous_requests.append(message)
                model='gpt-4o-mini',
                messages = [
                    {
                        "role": "system",
                        "content": "You are an AI assistant who knows everything and speaks all language ",
                    },
                ] + [{ "role": "user", "content": message } for message in previous_requests]

                response = client.chat.completions.create(model="gpt-4o", messages=messages)

                keys.append(key)

                # Display the response
                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(tk.END, f"AI: {response.choices[0].message.content}\n")
                self.chat_area.config(state=tk.DISABLED)

                return response.choices[0].message.content
            except Exception as e:
                print(f"Ошибка с ключом {key}: {e}")  
                if i < max_tries - 1:
                    asyncio.sleep(retry_delay)

# Create the main window
root = tk.Tk()
app = ChatApp(root)

# Run the main event loop
root.mainloop()