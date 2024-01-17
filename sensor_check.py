import tkinter as tk
from tkinter import ttk
import pandas as pd
import threading
import time


class DataTableApp:
    def __init__(self, root, data_frame):
        self.root = root
        self.root.title("Data Table")

        self.data_frame = data_frame

        # Create a Treeview widget
        self.tree = ttk.Treeview(root)
        self.tree["columns"] = list(data_frame.columns)

        # Set column headings
        for column in data_frame.columns:
            self.tree.heading(column, text=column)
            # Adjust column width as needed
            self.tree.column(column, anchor="center", width=100)

        # Insert initial data into the table
        self.update_table()

        self.tree.pack(padx=10, pady=10)

        # Start a thread to update the data intermittently
        self.update_thread = threading.Thread(
            target=self.update_data_intermittently, daemon=True)
        self.update_thread.start()

    def update_table(self):
        try:
            # Clear the existing data in the table
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insert data into the table
            for index, row in self.data_frame.iterrows():
                self.tree.insert("", index, values=tuple(row))
        except tk.TclError as e:
            # Handle the case where the widget has been destroyed
            print(f"Error updating table: {e}")

    def update_data_intermittently(self):
        while True:
            # Simulate updating data every 5 seconds (replace this with your actual update logic)
            time.sleep(5)

            # Update the DataFrame with new data
            new_data_frame = pd.DataFrame({
                "Name": ["John", "Jane", "Bob"],
                "Age": [25, 30, 22],
                "City": ["New York", "London", "Paris"]
            })

            # Update the data_frame attribute
            self.data_frame = new_data_frame

            # Update the table
            self.update_table()


if __name__ == "__main__":
    # Example Pandas DataFrame
    data_frame = pd.DataFrame({
        "Name": ["John", "Jane", "Bob"],
        "Age": [2453, 33450, 23452],
        "City": ["New York", "London", "Paris"]
    })
    time.sleep(5)

    root = tk.Tk()
    app = DataTableApp(root, data_frame)
    root.mainloop()
