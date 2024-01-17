import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import json
from pandastable import Table, TableModel


class TableWindow(tk.Toplevel):
    def __init__(self, parent, config_file):
        super().__init__(parent)
        self.config_file = config_file
        self.geometry('883x742')  # Set the size of the window
        self.title('Table')  # Set the title of the window
        # Make the table_window transient with respect to the main window
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.on_closing_table)

        # state variables
        self.table_freeze = 0

        # Create a frame for the table
        self.table_frame = ttk.Frame(self)
        self.table_frame.grid(row=1, column=1, padx=10, pady=10, sticky='nesw')

        # Create a frame for the buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        ttk.Button(self.button_frame, text='Freeze Table',
                   command=self.freeze_table).grid(row=0, column=0, sticky="e")

    def update_table(self, df):
        """Checks if the table already exists, if it does, update it, if it doesn't, create it"""
        if hasattr(self, 'table'):
            # If it does, update it
            if self.table_freeze == 0:
                self.table.updateModel(TableModel(df))
                self.table.redraw()
        else:
            self.table = Table(self.table_frame, dataframe=df,
                               showtoolbar=False, showstatusbar=True, width=800, height=600)
            self.table.show()

    def freeze_table(self):
        """freezes the table to allow for easy sorting and viewing"""
        if self.table_freeze == 0:
            self.table_freeze = 1
        else:
            self.table_freeze = 0
        # print(self.table_freeze)

    def on_closing_table(self):
        """Called when closing the table_window, destroys the table_window"""
        self.master.table_window_open = False
        self.destroy()
