import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import threading
import time


class LivePlottingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Plotting Data Table")

        # Create a frame for the plot
        self.plot_frame = ttk.Frame(root)
        self.plot_frame.grid(row=0, column=0, padx=10, pady=10)

        # Create a frame for the data table
        self.data_frame = ttk.Frame(root)
        self.data_frame.grid(row=0, column=1, padx=10, pady=10)

        # Create a figure for the plot
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack()

        # Create a treeview for the data table
        self.tree = ttk.Treeview(self.data_frame, columns=(
            "Time", "Value"), show="headings")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Value", text="Value")
        self.tree.pack()

        # Start a thread for generating random data and updating the plot
        self.running = True
        self.data_thread = threading.Thread(target=self.update_data)
        self.data_thread.start()

    def update_data(self):
        data = []
        x_axis = []
        while self.running:
            # Generate random data
            current_time = time.strftime("%H:%M:%S")
            random_value = random.randint(0, 100)

            # Update the data table
            self.tree.insert("", "end", values=(current_time, random_value))

            # Update the plot
            self.ax.clear()
            data.append(random_value)
            # x_axis.append(current_time)
            self.ax.plot(data, marker='o', color='b')
            self.ax.set_title("Live Plotting")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Value")

            self.canvas.draw()

            # Pause for a short time (you can adjust this as needed)
            time.sleep(1)

    def on_closing(self):
        # Stop the data thread when the application is closed
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LivePlottingApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
