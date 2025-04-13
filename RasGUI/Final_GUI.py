import serial
import threading
from test_gauge2 import Gauge
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # PIL for image handling
from vegetablesHeader import Tomato, Lettuce, Cucumber

# Initialize Window
window = Tk()
window.title("Vertical Farming")
window.geometry('1600x900')  # Increased height to fit logo

# Load and Add Logo
try:
    logo_image = Image.open("Vert.png")  # Update with your image name
    logo_image = logo_image.resize((565, 279), Image.ANTIALIAS)  # Resize if needed
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = Label(window, image=logo_photo)
    logo_label.grid(column=3, row=0, rowspan=2, padx=20, pady=10)
except Exception as e:
    print(f"Error loading image: {e}")
    logo_label = Label(window, text="Logo Not Found", font=("Arial", 12))
    logo_label.grid(column=3, row=0, rowspan=2, padx=20, pady=10)

# Default Values
ph = 7.0
solution_level = 50
tds = 1000
dli = 35
turbidity = 200

# Create UI
frame = Frame(window)
frame.grid(column=0, row=2, columnspan=5, padx=20, pady=10)

# Gauges for Variables
gauge_ph = Gauge(frame, title="pH LEVEL", value=ph, max_v=14, partition=7, size=170)
gauge_ph.grid(row=0, column=0, padx=10)

gauge_tds = Gauge(frame, title="TDS", value=tds, max_v=2000, partition=6, size=170)
gauge_tds.grid(row=0, column=1, padx=10)

gauge_dli = Gauge(frame, title="DLI", value=dli, max_v=60, partition=6, size=170)
gauge_dli.grid(row=0, column=2, padx=10)

gauge_turbidity = Gauge(frame, title="Turbidity", value=turbidity, max_v=1000, partition=5, size=170)
gauge_turbidity.grid(row=0, column=3, padx=10)

# Progress bar for Solution Level
solution_level_bar = ttk.Progressbar(frame, orient="vertical", length=200, mode="determinate", maximum=100)
solution_level_bar.grid(column=4, row=0, pady=10)
solution_level_bar['value'] = solution_level

# Solution Level Label with Unit
solution_level_label = Label(frame, text=f"Solution Level: {solution_level} mL", font=("Arial", 12))
solution_level_label.grid(column=4, row=1, pady=5)

# Vegetables Dropdown
vegetables = [Tomato(), Lettuce(), Cucumber()]
selected_vegetable = StringVar()
dropdown = ttk.Combobox(window, textvariable=selected_vegetable, values=[str(veg) for veg in vegetables], state="readonly")
dropdown.grid(column=1, row=1, pady=10)
dropdown.current(0)

# Update Gauges Function
def update_gauges(new_ph, new_tds, new_dli, new_turbidity, new_solution_level):
    gauge_ph.setValue(new_ph)
    gauge_tds.setValue(new_tds)
    gauge_dli.setValue(new_dli)
    gauge_turbidity.setValue(new_turbidity)
    solution_level_bar['value'] = new_solution_level

    # Update solution level label dynamically
    solution_level_label.config(text=f"Solution Level: {new_solution_level:.1f} mL")

# Serial Reading Function
def read_serial():
    global ph, solution_level, tds, dli, turbidity

    ser = serial.Serial('/dev/serial0', 9600, timeout=4)

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            print(f"Received: {data}")  # Debugging Output

            try:
                values = data.split(",")
                if len(values) == 5:  # Expecting 5 values now
                    turbidity = float(values[0])
                    tds = int(values[1])
                    solution_level = float(values[2])  # Solution Level in %
                    ph = float(values[3])
                    dli = int(values[4])

                    # Update UI
                    window.after(100, update_gauges, ph, tds, dli, turbidity, solution_level)

            except ValueError:
                print("Invalid data format received")

# Run Serial Read in Background Thread
threading.Thread(target=read_serial, daemon=True).start()

# Start GUI
window.mainloop()
