import pandas as pd
import tkinter as tk
from tkinter import ttk
import time
import threading

# NEED TO SYNCHRONIZE DATA UPLOAD FROM ALL THREE COMPUTERS TO ONE OBJECT -- THEN UPLOAD TO CSV TO AVOID LARGE EMPTY DATA POINTS


class DataHandler:
    def __init__(self, gui, num_computers) -> None:
        self.df_outline = pd.DataFrame(columns=["Time", "Source in Current (A)", "Source in Voltage (V)",
                                                "BCM LV IN Voltage (V)", "BCM LV IN Current (A)",
                                                "Transmit Battery Voltage (V)", "Transmit Battery Current (A)",
                                                "400 Line Voltage (V)", "400 Line Current (A)",
                                                'Load Side Voltage (V)', 'Load Side Current (A)',
                                                'Load Battery Voltage (V)', 'Load Battery Current (A)',
                                                'BCM Voltage In (V)', 'BCM Voltage Out (V)',
                                                'BCM Current In (A)', 'BCM Current Out (A)',
                                                'Source Victron Voltage (V)', 'Source Victron Current (A)',
                                                'Source Victron VPV (V)', 'Source Victron WPV (W)',
                                                'Load Victron Voltage (V)', 'Load Victron Current (A)',
                                                'Load Victron VPV (V)', 'Load Victron WPV (W)',
                                                'BK Load Voltage (V)', 'BK Load Current (A)', 'BK Load Power (W)',
                                                'PS Voltage (V)', 'PS Current (A)', 'PS Power (W)'])

        self.df = self.df_outline
        self.filepath = 'sensor_data.csv'
        self.num_computers = num_computers
        self.num_reports = 0

        self.display_gui = True if gui == 1 else False
        if self.display_gui == 1:
            self.root = tk.Tk()
            self.app = DataTableGUI(self.root)
            # self.app.mainloop()

    def update_data(self, time_elapsed, new_data):
        '''
        takes in json/dictionary
        '''

        # inelegant solution, but it should work
        temp_df = self.df_outline.to_dict()

        temp_df["Time"] = time_elapsed
        for sensor in new_data:
            if sensor in temp_df:
                temp_df[sensor] = new_data[sensor]
            else:
                print("Data handling - dataframe does not contain this sensor")

        # only update dataframe with new frame if all active computers have reported data
        if self.num_reports == self.num_computers:
            self.num_reports = 0
            self.df = self.df._append(temp_df, ignore_index=True)

            # update csv?
            self.export_to_csv()

    def export_to_csv(self,):
        self.df.to_csv(self.filepath, index=False)


# not working -- going to move this all to a seperate module -- decouple from data gandler
# going to update by just reading the data file instead of direct update calls
# gui module will also handle plotting data
# gui module will also handle start, stop buttons
class DataTableGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HOLY SHIT!")

        # creating a treeview for displaying table
        self.tree = ttk.Treeview(root, columns=(
            "Time", "Source in Current (A)", "Source in Voltage (V)",
            "BCM LV IN Voltage (V)", "BCM LV IN Current (A)",
            "Transmit Battery Voltage (V)", "Transmit Battery Current (A)",
            "400 Line Voltage (V)", "400 Line Current (A)",
            'Load Side Voltage (V)', 'Load Side Current (A)',
            'Load Battery Voltage (V)', 'Load Battery Current (A)',
            'BCM Voltage In (V)', 'BCM Voltage Out (V)',
            'BCM Current In (A)', 'BCM Current Out (A)',
            'Source Victron Voltage (V)', 'Source Victron Current (A)',
            'Source Victron VPV (V)', 'Source Victron WPV (W)',
            'Load Victron Voltage (V)', 'Load Victron Current (A)',
            'Load Victron VPV (V)', 'Load Victron WPV (W)',
            'BK Load Voltage (V)', 'BK Load Current (A)', 'BK Load Power (W)',
            'PS Voltage (V)', 'PS Current (A)', 'PS Power (W)'), show="headings")

        # setting the  column headings
        for column in self.tree["columns"]:
            self.tree.heading(column, text=column)
            # Adjust column width as needed
            self.tree.column(column, anchor="center", width=50)

        self.tree.pack(padx=10, pady=10)

    def update_data(self, new_data):

        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert data into the table
        for index, row in new_data.iterrows():
            self.tree.insert("", index, values=tuple(row))


if __name__ == "__main__":
    pass
