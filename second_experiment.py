import tkinter as tk
from tkinter import Menu, Label, Button, Entry, Text, Scrollbar
from PIL import Image, ImageTk
import asyncio
import threading
import websockets
import queue

current_index = 0

data = data = [
    {
        'patient_name': 'John Doe',
        'patient_id': '0001',
        'health_info': 'No known allergies',
        'ct_slice': 'patient1.png',
        'segmented_slice': 'explain1.png',
        'pe_detected': True,
        'confidence': 97,
        'coordinates': (120, 220, 55)
    },
    {
        'patient_name': 'Emma Stone',
        'patient_id': '0002',
        'health_info': 'Hypertension',
        'ct_slice': 'patient2.png',
        'segmented_slice': 'explain2.png',
        'pe_detected': True,
        'confidence': 92,
        'coordinates': (130, 240, 60)
    },
    {
        'patient_name': 'Michael Brown',
        'patient_id': '0003',
        'health_info': 'Asthma',
        'ct_slice': 'patient3.png',
        'segmented_slice': 'explain3.png',
        'pe_detected': False,
        'confidence': 88,
        'coordinates': (140, 260, 70)
    },
    {
        'patient_name': 'Sophia Davis',
        'patient_id': '0004',
        'health_info': 'Smoker',
        'ct_slice': 'patient4.png',
        'segmented_slice': 'explain4.png',
        'pe_detected': False,
        'confidence': 84,
        'coordinates': (125, 235, 50)
    },
    {
        'patient_name': 'James Wilson',
        'patient_id': '0005',
        'health_info': 'No known allergies',
        'ct_slice': 'patient5.png',
        'segmented_slice': 'explain5.png',
        'pe_detected': True,
        'confidence': 96,
        'coordinates': (110, 210, 45)
    },
    {
        'patient_name': 'Olivia Taylor',
        'patient_id': '0006',
        'health_info': 'History of DVT',
        'ct_slice': 'patient6.png',
        'segmented_slice': 'explain6.png',
        'pe_detected': True,
        'confidence': 89,
        'coordinates': (135, 225, 65)
    },
    {
        'patient_name': 'Liam Martinez',
        'patient_id': '0007',
        'health_info': 'Obese',
        'ct_slice': 'patient7.png',
        'segmented_slice': 'explain7.png',
        'pe_detected': True,
        'confidence': 91,
        'coordinates': (145, 215, 50)
    },
    {
        'patient_name': 'Ava Anderson',
        'patient_id': '0008',
        'health_info': 'No known allergies',
        'ct_slice': 'patient8.png',
        'segmented_slice': 'explain8.png',
        'pe_detected': False,
        'confidence': 86,
        'coordinates': (155, 275, 55)
    },
    {
        'patient_name': 'Ethan Thomas',
        'patient_id': '0009',
        'health_info': 'Hypertension and Diabetic',
        'ct_slice': 'patient9.png',
        'segmented_slice': 'explain9.png',
        'pe_detected': True,
        'confidence': 94,
        'coordinates': (160, 280, 68)
    },
    {
        'patient_name': 'Mia Garcia',
        'patient_id': '0010',
        'health_info': 'Smoker',
        'ct_slice': 'patient10.png',
        'segmented_slice': 'explain10.png',
        'pe_detected': True,
        'confidence': 90,
        'coordinates': (165, 290, 62)
    },
]


class CTScanApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Pulmonary Embolism Detection")
        self.geometry("600x800") 

        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        chat_menu = Menu(self.menu_bar, tearoff=0)
        chat_menu.add_command(label="Toggle Chat Panel", command=self.toggle_chat_panel)
        self.menu_bar.add_cascade(label="Chat", menu=chat_menu)

        self.patient_name_label = Label(self, text="Patient Name: ", font=("Arial", 14))
        self.patient_name_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.patient_id_label = Label(self, text="Patient ID: ", font=("Arial", 14))
        self.patient_id_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.health_info_label = Label(self, text="Health Info: ", font=("Arial", 14))
        self.health_info_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.image_label = Label(self)
        self.image_label.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

        self.result_label = Label(self, text="", font=("Arial", 16, "bold"))
        self.result_label.grid(row=4, column=0, columnspan=3, pady=10)

        self.confidence_label = Label(self, text="", font=("Arial", 14))
        self.confidence_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        self.coordinates_label = Label(self, text="", font=("Arial", 14))
        self.coordinates_label.grid(row=6, column=0, sticky="w", padx=10, pady=5)

        button_frame = tk.Frame(self)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)

        detect_button = Button(button_frame, text="Detect", command=self.detect_pe, font=("Arial", 12), width=10)
        detect_button.grid(row=0, column=0, padx=10)

        explain_button = Button(button_frame, text="Explain", command=self.show_segmented_slice, font=("Arial", 12), width=10)
        explain_button.grid(row=0, column=1, padx=10)

        next_button = Button(button_frame, text="Next", command=self.next_patient, font=("Arial", 12), width=10)
        next_button.grid(row=0, column=2, padx=10)

        toggle_chat_button = Button(self, text="Toggle Chat Panel", command=self.toggle_chat_panel, font=("Arial", 12))
        toggle_chat_button.grid(row=8, column=0, pady=10)

        self.chat_panel_visible = False
        self.chat_frame = tk.Frame(self)

        chat_label = Label(self.chat_frame, text="Chat", font=("Arial", 14, "bold"))
        chat_label.pack(anchor="w", padx=5, pady=5)

        self.chat_display = Text(self.chat_frame, wrap="word", width=70, height=15, state="disabled", font=("Arial", 12))
        self.chat_display.pack(side="left", padx=5, pady=5)

        chat_scroll = Scrollbar(self.chat_frame, command=self.chat_display.yview)
        chat_scroll.pack(side="right", fill="y")
        self.chat_display.config(yscrollcommand=chat_scroll.set)

        self.chat_entry = Entry(self.chat_frame, font=("Arial", 12))
        self.chat_entry.pack(padx=5, pady=5, fill="x")
        self.chat_entry.bind("<Return>", self.send_message)

        send_button = Button(self.chat_frame, text="Send", command=self.send_message, font=("Arial", 12))
        send_button.pack(padx=5, pady=5)

        self.message_queue = queue.Queue()
        self.websocket = None

        self.loop = asyncio.new_event_loop()
        self.websocket_thread = threading.Thread(target=self.start_event_loop, daemon=True)
        self.websocket_thread.start()

        self.after(100, self.process_incoming_messages)

        self.load_patient(current_index)

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
            self.display_message(f"AI-Assistant: {message}")
        self.after(100, self.process_incoming_messages)

    def toggle_chat_panel(self):
        """Toggle the visibility of the chat panel."""
        if self.chat_panel_visible:
            self.chat_frame.grid_forget()
        else:
            self.chat_frame.grid(row=9, column=0, columnspan=3, padx=10, pady=5, sticky="n")
        self.chat_panel_visible = not self.chat_panel_visible

    def load_patient(self, index):
        """Load patient data and update the GUI elements."""
        patient = data[index]
        self.patient_name_label.config(text=f"Patient Name: {patient['patient_name']}")
        self.patient_id_label.config(text=f"Patient ID: {patient['patient_id']}")
        self.health_info_label.config(text=f"Health Info: {patient['health_info']}")

        self.result_label.config(text="")
        self.confidence_label.config(text="")
        self.coordinates_label.config(text="")

        try:
            img = Image.open(patient["ct_slice"])
            img = img.resize((250, 250))
            self.img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.img_tk)
        except Exception as e:
            print(f"Error loading image: {e}")
            self.image_label.config(image='')

    def detect_pe(self):
        """Display if pulmonary embolism is detected and show confidence and coordinates."""
        patient = data[current_index]

        if patient["pe_detected"]:
            self.result_label.config(text="Pulmonary Embolism Detected", fg="red")
        else:
            self.result_label.config(text="No Pulmonary Embolism Detected", fg="green")

        self.confidence_label.config(text=f"Confidence: {patient['confidence']}%")
        self.coordinates_label.config(text=f"Coordinates (x,y,z): {patient['coordinates']}")

    def show_segmented_slice(self):
        """Show the segmented CT slice."""
        patient = data[current_index]
        try:
            segmented_img = Image.open(patient["segmented_slice"])
            segmented_img = segmented_img.resize((250, 250))  # Resize to fit the window
            self.img_tk_segmented = ImageTk.PhotoImage(segmented_img)
            self.image_label.config(image=self.img_tk_segmented)
        except Exception as e:
            print(f"Error loading segmented image: {e}")
            self.image_label.config(image='')

    def next_patient(self):
        """Load the next patient."""
        global current_index
        current_index = (current_index + 1) % len(data) 
        self.load_patient(current_index)

    def send_message(self, event=None):
        """Handle sending a message in the chat panel."""
        message = self.chat_entry.get()
        if message.strip():
            self.display_message(f"You: {message}")
            self.chat_entry.delete(0, tk.END)
            # Send the message via the WebSocket
            if self.websocket:
                asyncio.run_coroutine_threadsafe(self.websocket_send(message), self.loop)
            else:
                self.display_message("Wizard: Not connected to server.")

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
    app = CTScanApp()
    app.mainloop()
