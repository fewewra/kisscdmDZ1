from shell_emulator import VirtualFileSystem, ShellEmulator
from shell_emulator_gui import ShellGUI
import csv
import json

def load_config(file_path):
    config = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for rows in reader:
            if rows and len(rows) == 2:  # Проверка, что строка не пустая и имеет два элемента
                config[rows[0]] = rows[1]
    return config


if __name__ == "__main__":
    config = load_config("config.csv")
    vfs = VirtualFileSystem(config["archive_path"])
    emulator = ShellEmulator(vfs, config["username"], config["log_path"])
    gui = ShellGUI(emulator)
    gui.run()
