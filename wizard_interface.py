import tkinter as tk
from tkinter import Text, Scrollbar, Entry, Button
import asyncio
import threading
import websockets
import queue

class WizardInterface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Wizard Interface")

        self.chat_display = Text(self, wrap="word", width=60, height=20, state="disabled", font=("Arial", 12))
        self.chat_display.pack(side="left", padx=5, pady=5)

        chat_scroll = Scrollbar(self, command=self.chat_display.yview)
        chat_scroll.pack(side="left", fill="y")
        self.chat_display.config(yscrollcommand=chat_scroll.set)

        self.chat_entry = Entry(self, font=("Arial", 12))
        self.chat_entry.pack(padx=5, pady=5, fill="x")
        self.chat_entry.bind("<Return>", self.send_message)

        send_button = Button(self, text="Send", command=self.send_message, font=("Arial", 12))
        send_button.pack(padx=5, pady=5)

        self.message_queue = queue.Queue()
        self.websocket = None  
        self.loop = asyncio.new_event_loop()
        self.websocket_thread = threading.Thread(target=self.start_event_loop, daemon=True)
        self.websocket_thread.start()

        self.after(100, self.process_incoming_messages)

    def start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.websocket_handler())

    async def websocket_handler(self):
        uri = "wss://cs139-woz-production.up.railway.app/ws"  
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                while True:
                    message = await websocket.recv()
                    self.message_queue.put(message)
        except Exception as e:
            print(f"WebSocket connection error: {e}")

    def process_incoming_messages(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            self.display_message(f"User: {message}")
        self.after(100, self.process_incoming_messages)

    def send_message(self, event=None):
        """Handle sending a message."""
        message = self.chat_entry.get()
        if message.strip():
            self.display_message(f"You: {message}")
            self.chat_entry.delete(0, tk.END)
            if self.websocket:
                asyncio.run_coroutine_threadsafe(self.websocket_send(message), self.loop)
            else:
                self.display_message("System: Not connected to server.")

    async def websocket_send(self, message):
        try:
            await self.websocket.send(message)
        except Exception as e:
            print(f"Error sending message: {e}")

    def display_message(self, message):
        """Display a message in the chat display."""
        self.chat_display.config(state="normal")
        self.chat_display.insert("end", message + "\n")
        self.chat_display.config(state="disabled")
        self.chat_display.see("end")

if __name__ == "__main__":
    app = WizardInterface()
    app.mainloop()
