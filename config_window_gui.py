import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import json


class ConfigWindow(tk.Toplevel):
    def __init__(self, parent, config_file):
        super().__init__(parent)
        self.config_file = config_file
        self.geometry('500x500')  # Set the size of the window
        self.title('Configuration')  # Set the title of the window
        # Make the config_window transient with respect to the main window
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.on_closing_config)

        # state variables

        # Create variables to hold the state of the checkboxes
        self.output_csv = tk.IntVar()
        self.output_png = tk.IntVar()
        self.test_duration = tk.IntVar()
        self.state_variables_dict = {
            "output_csv": self.output_csv,
            "output_png": self.output_png,
            "test_duration": self.test_duration
        }

        # Bind trace method to the variables
        # self.output_csv.trace_add("write", self.set_unsaved_changes)
        # self.output_png.trace_add("write", self.set_unsaved_changes)
        # self.test_duration.trace_add("write", self.set_unsaved_changes)

        # Create a command to validate the test duration input
        validate_command = (self.register(self.validate_only_numbers), "%P")

        # Create the input fields, with values set to the variables
        output_csv_button = ttk.Checkbutton(
            self, text="Output csv", variable=self.output_csv)
        output_png_button = ttk.Checkbutton(
            self, text="Output png", variable=self.output_png)
        test_duration_input = ttk.Entry(
            self, textvariable=self.test_duration, validate="key", validatecommand=validate_command)
        test_duration_label = ttk.Label(self, text="Test Duration (s)")

        # Add the inputs to the window using grid
        output_csv_button.grid(row=0, column=0, sticky="w")
        output_png_button.grid(row=1, column=0, sticky="w")
        test_duration_input.grid(row=2, column=0, sticky="w")
        test_duration_label.grid(row=2, column=1, sticky="w")

        # Create the buttons
        save_button = ttk.Button(
            self, text="Save Changes", command=self.save_config)
        export_button = ttk.Button(
            self, text="Save and Export ", command=self.export_config)
        import_button = ttk.Button(
            self, text="Import and Save", command=self.import_config)

        # Add the buttons to the window using grid
        save_button.grid(row=3, column=0, sticky="e")
        export_button.grid(row=3, column=1, sticky="e")
        import_button.grid(row=3, column=2, sticky="e")

        # Update the inputs to match the config file
        self.after(0, self.update_inputs)

    def unsaved_changes(self):
        for key, var in self.state_variables_dict.items():
            if var.get() != self.config_file["gui_testing"][key]:
                return True
        else:
            return False

    def save_config(self):
        # Save the current state of the checkboxes to the default config file
        self.config_file["gui_testing"]["output_csv"] = self.output_csv.get()
        self.config_file["gui_testing"]["output_png"] = self.output_png.get()
        self.config_file["gui_testing"]["test_duration"] = self.test_duration.get()

        with open("testing_config.json", "w") as file:
            json.dump(self.config_file, file, indent=4)
        # self.unsaved_changes = False

    def export_config(self):
        # open a file dialog to select the config file to export to
        self.after(0, self.save_config)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:  # check if a file path was selected
            with open(file_path, "w") as file:
                json.dump(self.config_file, file, indent=4)
            self.unsaved_changes = False

    def import_config(self):
        # open a file dialog to select the config file to import
        file_path = filedialog.askopenfilename(
            defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:  # check if a file path was selected
            with open(file_path, "r") as file:
                self.config_file = json.load(file)
            with open("testing_config.json", "w") as file:
                json.dump(self.config_file, file, indent=4)
            self.unsaved_changes = False
            # update the inputs to match the imported config
            self.after(0, self.update_inputs)

    def update_inputs(self):
        # Update the inputs to match the config file
        self.output_csv.set(self.config_file["gui_testing"]["output_csv"])
        self.output_png.set(self.config_file["gui_testing"]["output_png"])
        self.test_duration.set(
            self.config_file["gui_testing"]["test_duration"])

    def validate_only_numbers(self, new_value):
        return new_value.isdigit()

    def on_closing_config(self):
        """Called when closing the config window, checks to make sure changes are saved"""
        if self.unsaved_changes() == True:
            if messagebox.askyesno("Unsaved Changes", "Do you want to save your changes before quiting?"):
                self.save_config()
                self.destroy()
            else:
                self.destroy()
        else:
            self.destroy()
