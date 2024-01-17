import random
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import threading
import time
import json

from config_window_gui import ConfigWindow
from table_gui import TableWindow

# set the taskbar icon, not necessary if compiling to exe, only on windows
# import ctypes
# myappid = 'ucsb.wotm.gui' # arbitrary string
# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# crashes sometimes when trying to close the gui, need to fix this, maybe to due with how the threads are being closed or on_closing is defined?
# nothing resizes well, especially the progress bar, need to fix this


class Gui(tk.Tk):
    def __init__(self):
        with open("testing_config.json", "r") as file:
            testing_config = json.load(file)

        # load info from config file
        self.config_file = testing_config
        self.gui_enable = testing_config["main computer settings"]["gui"]
        self.plotting_enable = testing_config["main computer settings"]["plotting"]

        # load the load profile
        # self.load_profile = pd.read_csv("load_profile.csv")
        # self.max_time = self.load_profile["Time"].max()
        self.max_time = 40000000000000

        # time between data refreshes
        self.time_refresh = 1  # in seconds

        # state variables
        self.running = False
        self.table_window_open = False
        # "Source Victron", "Load Victron", "BK Load", "PS"
        self.prefixes = ["Source in", "BCM", "Transmit Battery",
                         "400 Line", "Load Side", "Load Battery"]

        # other vars
        self.current_time = 0

        # reset data file
        with open("sensor_data.csv", "w") as file:
            file.write("Time,Source in Current (A),Source in Voltage (V),BCM LV IN Voltage (V),BCM LV IN Current (A),Transmit Battery Voltage (V),Transmit Battery Current (A),400 Line Voltage (V),400 Line Current (A),Load Side Voltage (V),Load Side Current (A),Load Battery Voltage (V),Load Battery Current (A),BCM Voltage In (V),BCM Voltage Out (V),BCM Current In (A),BCM Current Out (A),Source Victron Voltage (V),Source Victron Current (A),Source Victron VPV (V),Source Victron WPV (W),Load Victron Voltage (V),Load Victron Current (A),Load Victron VPV (V),Load Victron WPV (W),BK Load Voltage (V),BK Load Current (A),BK Load Power (W),PS Voltage (V),PS Current (A),PS Power (W)")
            file.write("\n")

        super().__init__()

        # setup the window
        self.title('Watts on the Moon Test - Main Computer GUI')

        # get users screen resolution and maximize window
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry('1200x600+50+50')
        self.state('zoomed')
        self.iconbitmap('ucsb_physics.ico')

        # frame for the plot
        self.plot_frame = ttk.Frame(self, borderwidth=1, relief="solid")
        self.plot_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

        # figure for the plot and create an axis for each prefix, ** bug with tkinter, plt.subplots() breaks window size/zoom ??
        self.fig = plt.Figure(figsize=(120, 5), dpi=75)
        self.axes = {prefix: self.fig.add_subplot(
            2, 3, i + 1) for i, prefix in enumerate(self.prefixes)}
        self.fig.subplots_adjust(
            left=0.04, right=0.96, bottom=0.07, top=0.95, wspace=0.1, hspace=0.25)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(sticky='nsew', padx=0, pady=0)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        # Create the buttons
        self.control_frame = ttk.Frame(self)
        self.control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ttk.Button(self.control_frame, text='Config', command=self.open_config_window).grid(
            row=0, column=1, sticky="e")
        ttk.Button(self.control_frame, text='Table', command=self.open_table_window).grid(
            row=0, column=2, sticky="e")
        ttk.Button(self.control_frame, text='Start Test',
                   command=self.start_test).grid(row=0, column=3, sticky="e")
        ttk.Button(self.control_frame, text='End Test',
                   command=self.end_test).grid(row=0, column=4, sticky="e")
        ttk.Button(self.control_frame, text='Clear Data',
                   command=self.clear_data).grid(row=0, column=5, sticky="e")

        # Create the progress bar
        self.progress_frame = ttk.Frame(self, borderwidth=1, relief="solid")
        self.progress_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.progress_fig = plt.Figure(
            figsize=((self.screen_width-12)/75, 1), dpi=75)
        self.progress_ax = self.progress_fig.add_subplot(111)
        self.progress_ax.axis('off')
        self.progress_fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        self.progress_canvas = FigureCanvasTkAgg(
            self.progress_fig, master=self.progress_frame)
        canvas_widget = self.progress_canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")

        # graph the load profile on the progress bar
        # self.progress_ax.plot(
        # self.load_profile["Time"], self.load_profile["Load Power (W)"], marker='o', label="Load Power (W)")
        # self.progress_ax.set_xlim(
        # self.load_profile["Time"].min(), self.load_profile["Time"].max())
        self.vline = self.progress_ax.axvline(x=0, color='r')

        self.progress_canvas.draw()

        # do i need all these?
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def start_gui(self):
        """Starts the gui and the thread"""
        self.running = True
        self.thread = threading.Thread(target=self.update_data)
        self.thread.daemon = True
        self.mainloop()

    def update_data(self):
        """Updates the dataframe, df, from sensor_data.csv"""
        while self.running:
            # self.safe_after(0, self._generate_rand_data)
            df = pd.read_csv("sensor_data.csv")

            # Update the graph with the new data
            self.safe_after(0, self.update_graph, df)

            if self.table_window_open == True:
                # Update the table with the new data
                self.safe_after(0, self.table_window.update_table, df)

            # Update the progress bar
            self.safe_after(0, self.update_progress, df)

            time.sleep(self.time_refresh)

    def update_graph(self, df):
        """Updates the graph with the new data"""
        if self.plotting_enable == 1:
            for ax in self.axes.values():
                ax.clear()

            for column in df.columns:
                for prefix, ax in self.axes.items():
                    if column.startswith(prefix):
                        ax.plot(df["Time"], df[column],
                                marker='o', label=column)
                        ax.set_title(f"{prefix}")
                        ax.set_xlabel("Time")
                        ax.grid(True)

            self.canvas.draw()

        else:
            print("Plotting is disabled")

    def open_config_window(self):
        self.config_window = ConfigWindow(self, self.config_file)

    def open_table_window(self):
        self.table_window = TableWindow(self, self.config_file)
        self.table_window_open = True

    def on_closing(self):
        """Called when closing the gui, destroys the gui and closes the thread"""
        # i think order is correct/safest but im not entirely sure
        self.running = False
        self.destroy()
        time.sleep(self.time_refresh)
        if self.thread is not None:
            self.thread.join()
        self.quit()

    def update_progress(self, df):
        """Updates the progress bar"""
        if not df.empty:
            time = df["Time"].iloc[-1]
            self.vline.set_xdata([time])
            self.progress_canvas.draw()

    def _generate_rand_data(self):
        """Testing function, adds 1 line of random data to sensor_data.csv"""
        if (self.current_time <= self.max_time):
            with open("sensor_data.csv", "a") as file:
                random_data = [random.randint(0, 100) for _ in range(30)]
                line = str(self.current_time) + "," + \
                    ",".join(map(str, random_data)) + "\n"
                file.write(line)
        self.current_time += 1

    def safe_after(self, delay, func, *args, **kwargs):
        """Executes a function after a delay, but only if the program is still running."""
        if self.running:
            self.after(delay, func, *args, **kwargs)

    def start_test(self):
        """Starts the test"""
        if self.thread is not None:
            self.running = True
            self.thread.start()

    def end_test(self):
        """Ends the test"""
        if self.running == True:
            self.running = False
            self.thread.join()
            self.thread = None
            self.current_time = 0
            self.export_data()
            # open the table window if it is not already open
            if self.table_window_open == False:
                self.open_table_window()
                # update the table with the exported data
                self.table_window.update_table(pd.read_csv("sensor_data.csv"))

    def export_data(self):
        """Exports the data to csv and png based on the configs"""
        if (self.config_file["gui_testing"]["output_csv"] == 1):
            # open a file dialog to select the csv file to export to
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file_path:  # check if a file path was selected
                df = pd.read_csv("sensor_data.csv")
                df.to_csv(file_path, index=False)
        if (self.config_file["gui_testing"]["output_png"] == 1):
            # open a file dialog to select the png file to export to
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png", filetypes=[("PNG Files", "*.png")])
            if file_path:  # check if a file path was selected
                self.fig.savefig(file_path)

    def clear_data(self):
        """Clear the data file, exept for the header"""
        pass


if __name__ == "__main__":
    app = Gui()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.start_gui()
