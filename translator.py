from itertools import groupby
from operator import itemgetter
import os
import csv
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSizePolicy, QFileDialog, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import time

def remove_common_prefix(sequences_list):
    # Transpose the list to get all parts in each position across the sequences
    if len(sequences_list) == 1:
        return sequences_list
    
    transposed = list(zip(*sequences_list))
    
    # Determine the index up to which all parts are identical across all sequences
    prefix_length = 0
    for parts in transposed:
        if all(part == parts[0] for part in parts):
            prefix_length += 1
        else:
            break
    
    # Remove the common prefix from each sequence
    return [seq[prefix_length:] for seq in sequences_list]

# Building structure

building = [
    {
        "name": 'B0',
        "label": 'Building 0'
    },
    {
        "name": 'B1',
        "label": 'Building 1 North'
    },
    {
        "name": 'B2',
        "label": 'Building 2 South'
    },
    {
        "name": 'B3',
        "label": 'Building 3'
    },
    {
        "name": 'B4',
        "label": 'Building 4'
    },
    {
        "name": 'GC',
        "label": 'General Conditions'
    },
]

# Floor Level Structure

floors = [
    {
        "name": 'F01',
        "label": 'Floor 01'
    },
    {
        "name": 'F02',
        "label": 'Floor 02'
    },
    {
        "name": 'F03',
        "label": 'Floor 03'
    },
    {
        "name": 'F04',
        "label": 'Floor 04'
    },
    {
        "name": 'F05',
        "label": 'Roof'
    },
    {
        "name": 'F0',
        "label": 'Phase 0'
    },
    {
        "name": 'F1',
        "label": '1st Floor'
    },
    {
        "name": 'F2',
        "label": '2nd Floor'
    },
    {
        "name": 'F3',
        "label": 'Roof'
    },
    {
        "name": 'FD',
        "label": 'Door'
    },
    {
        "name": 'FX',
        "label": 'Ext'
    },
]

# Area Level Names

areas = [
    {
        "name": 'A0',
        "label": 'General Conditions'
    },
    {
        "name": 'AA',
        "label": 'Area A'
    },
    {
        "name": 'AB',
        "label": 'Area B'
    },
    {
        "name": 'AC',
        "label": 'Area C'
    },
    {
        "name": 'AD',
        "label": 'Area D'
    },
    {
        "name": 'AE',
        "label": 'Area A Exterior'
    },
    {
        "name": 'AF',
        "label": 'Area B Exterior'
    },
    {
        "name": 'AG',
        "label": 'Area C Exterior'
    },
    {
        "name": 'AH',
        "label": 'Area D Exterior'
    },
    {
        "name": 'AK',
        "label": 'Ceilings'
    },
    {
        "name": 'AX',
        "label": 'Ext'
    },
    {
        "name": 'Int',
        "label": 'Interior'
    },
    {
        "name": 'Ext',
        "label": 'Exterior'
    },

]


def get_full_data(csv_source):

    content = ''
    # Get datas from csv file
    with open(csv_source, 'r') as file:
        content = file.read() # Store All data from CSV file

    data = content.split('\n') # Split data per each row
    i = 0

    full_data = []

    for line in data:
        i = i + 1
        line_data = line.split(',') # Split row per each coma
        if line_data.__len__() != 2:
            continue # If length is not 2, or csv structure is not same, will continue
        line_hour = ''
        line_floor = ''
        line_build = ''
        line_area = ''
        line_full = ''
        line_label = ''

        try:
            line_full = line_data[0]
            line_hour = line_data[1]
            description = line_full.split('-')
            if description.__len__() != 2: # Continue if the length is not 2, or not well structured
                continue
            left_d = description[0] # Left part of description when split it by '-'
            right_d = description[1] # Right part

            # Start analyzing left part

            analyze_left = left_d.split(' ')

            for one in analyze_left:
                for build in building:
                    if one == build['name']:
                        line_build = build['label']

                for area in areas:
                    if one == area['name']:
                        line_area = area['label']

                    if one.__contains__(f"{area['name']}&"):
                        one_list = one.split('&')
                        line_area = area['label']
                        j = 0
                        for one_l in one_list:
                            if j == 0:
                                j = j+1
                                continue
                            line_area = f"{line_area} & {one_l}"


                for floor in floors:
                    if one == floor['name']:
                        line_floor = floor['label']

            # Start analyzing right part


        except Exception as e:
            print(f"An Error Occured in row {i}: {e}")

        line_full_data = {
            "build": line_build,
            "floor": line_floor,
            "area": line_area,
            "hour": line_hour,
            "full": line_full,
            "label": right_d
        }
        full_data.append(line_full_data)

    sorted_data = sorted(full_data, key=lambda x: (x["build"], x["floor"], x["area"]))

    return sorted_data

def sort_group_func(sorted_data):
    result = []
    for key, group in groupby(sorted_data, key=itemgetter("build", "floor", "area")):
        group = list(group)  # Convert group to a list to iterate multiple times
        full_sequences_lists = [item["label"].split() for item in group]  # Split each "full" field into sequences
        
        # Remove common repetitive prefix sequences
        updated_full_sequences_lists = remove_common_prefix(full_sequences_lists)
        
        # Update each "full" entry in the group
        for item, updated_sequences in zip(group, updated_full_sequences_lists):
            item["label"] = " ".join(updated_sequences)  # Rejoin sequences into a single string
            result.append(item)
    return result


# with open(csv_Target, mode='w', newline='') as file:
#     writer = csv.DictWriter(file, fieldnames=result[0].keys())
#     writer.writeheader()
#     writer.writerows(result)

def build_json_structure(data):
    structures = []

    # Store data in a structure that adapts to the available fields
    nodes = {}  

    for row in data:
        build, floor, area, hour, full, label = row['build'], row['floor'], row['area'], row['hour'], row['full'], row['label']

        work_item = {
            "label": label,
            "hours": int(hour) if hour else None,
            "fullCode": full
        }

        if build and not floor and not area:
            # Only "Build" is present, use it as a top-level node
            if build not in nodes:
                nodes[build] = {"label": build, "children": []}
            nodes[build]["children"].append(work_item)

        elif build and floor and not area:
            # "Build" and "Floor" are present, nest "Floor" under "Build"
            if build not in nodes:
                nodes[build] = {"label": build, "children": {}}
            if floor not in nodes[build]["children"]:
                nodes[build]["children"][floor] = {"label": floor, "children": []}
            nodes[build]["children"][floor]["children"].append(work_item)

        elif build and floor and area:
            # "Build", "Floor", and "Area" are present, nest "Area" under "Floor"
            if build not in nodes:
                nodes[build] = {"label": build, "children": {}}
            if floor not in nodes[build]["children"]:
                nodes[build]["children"][floor] = {"label": floor, "children": {}}
            if area not in nodes[build]["children"][floor]["children"]:
                nodes[build]["children"][floor]["children"][area] = {"label": area, "children": []}
            nodes[build]["children"][floor]["children"][area]["children"].append(work_item)

        elif floor and not build and not area:
            # Only "Floor" is present, use it as a top-level node
            if floor not in nodes:
                nodes[floor] = {"label": floor, "children": []}
            nodes[floor]["children"].append(work_item)

        elif floor and area and not build:
            # "Floor" and "Area" are present, nest "Area" under "Floor"
            if floor not in nodes:
                nodes[floor] = {"label": floor, "children": {}}
            if area not in nodes[floor]["children"]:
                nodes[floor]["children"][area] = {"label": area, "children": []}
            nodes[floor]["children"][area]["children"].append(work_item)

        elif area and not build and not floor:
            # Only "Area" is present, use it as a top-level node
            if area not in nodes:
                nodes[area] = {"label": area, "children": []}
            nodes[area]["children"].append(work_item)

    # Convert the nodes dictionary into the desired JSON format
    for node_key, node_data in nodes.items():
        if "children" in node_data and isinstance(node_data["children"], dict):
            # Convert nested dictionaries into lists
            floors = []
            for floor_key, floor_data in node_data["children"].items():
                if "children" in floor_data and isinstance(floor_data["children"], dict):
                    areas = []
                    for area_key, area_data in floor_data["children"].items():
                        areas.append(area_data)
                    floor_data["children"] = areas
                floors.append(floor_data)
            node_data["children"] = floors
        structures.append(node_data)

    return structures


# Process the data and build the JSON structure

class Worker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        try:
            for file in self.file_paths:
                sorted_data = get_full_data(file)
                result = sort_group_func(sorted_data)
                json_structure = build_json_structure(result)
                base_name = os.path.basename(file)
                json_file_name = os.path.splitext(base_name)[0] + ".json"
                output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Output")
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                json_file_path = os.path.join(output_folder, json_file_name)

                with open(json_file_path, mode='w') as json_target_file:
                    json.dump(json_structure, json_target_file, indent=2)
            self.finished.emit("Task Completed!")
        except Exception as e:
            self.error.emit("Task Error!")
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('CSV to JSON Parser')
        self.resize(240,120)
        large_font = QFont("Arial", 16)  # 16 is the font size
        widget = QWidget()
        layout = QVBoxLayout()

        self.loadBtn = QPushButton("Load files")
        self.status = QLabel("...")
        self.saveBtn = QPushButton("Convert && Save")
        self.loadBtn.setFont(large_font)
        self.saveBtn.setFont(large_font)
        self.status.setFont(large_font)
        self.loadBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.saveBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.status.setAlignment(Qt.AlignCenter)

        self.loadBtn.clicked.connect(self.load_files)
        self.saveBtn.clicked.connect(self.save_files)
        self.saveBtn.setEnabled(False)
        self.file_paths = []
        layout.addWidget(self.loadBtn)
        layout.addWidget(self.saveBtn)
        layout.addWidget(self.status)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def load_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open CSV Files", "", "CSV Files (*.csv);;All Files (*)")

        if file_paths:
            self.file_paths = file_paths
            self.status.setText(f"{file_paths.__len__()} files loaded")
        if self.file_paths:
            self.saveBtn.setEnabled(True)
        else:
            self.saveBtn.setEnabled(False)
    def save_files(self):
        self.saveBtn.setEnabled(False)
        self.status.setText("Task is running...")

        self.worker = Worker(self.file_paths)
        self.worker.finished.connect(self.TaskFinished)
        self.worker.error.connect(self.TaskError)
        self.worker.start()
    
    def TaskError(self):
        self.saveBtn.setEnabled(True)
        self.status.setText("An Error occur while Generating!")
    
    def TaskFinished(self):
        self.saveBtn.setEnabled(True)
        self.status.setText("Task Completed Successfully!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())