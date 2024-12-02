import zipfile
from datetime import datetime
import json

class VirtualFileSystem:
    def __init__(self, zip_path):
        self.zip_path = zip_path
        self.current_path = "/"
        self.fs = {}
        self.load_fs()

    def load_fs(self):
        #Загружает файловую систему из zip-архива.
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                parts = file.strip('/').split('/')
                current_dir = self.fs
                for part in parts[:-1]:
                    current_dir = current_dir.setdefault(part, {})
                if file.endswith('/'):
                    current_dir.setdefault(parts[-1], {})
                else:
                    current_dir[parts[-1]] = None

    def list_directory(self):
        #Возвращает содержимое текущей директории.
        path_parts = self.current_path.strip("/").split("/") if self.current_path.strip("/") else []
        current_dir = self.fs

        for part in path_parts:
            if part in current_dir and isinstance(current_dir[part], dict):
                current_dir = current_dir[part]
            else:
                return []

        return list(current_dir.keys())

    def change_directory(self, path):
        #Меняет текущую директорию.
        if path == "/":
            self.current_path = "/"
            return

        parts = path.split("/")
        if path.startswith("/"):
            current_dir = self.fs
            new_path = "/"
        else:
            current_dir = self.get_current_dir()
            new_path = self.current_path.rstrip("/") + "/"

        for part in parts:
            if part == "..":
                if new_path != "/":
                    new_path = "/".join(new_path.rstrip("/").split("/")[:-1]) or "/"
                current_dir = self.get_parent_dir(new_path)
            elif part and part in current_dir:
                if isinstance(current_dir[part], dict):
                    new_path += f"{part}/"
                    current_dir = current_dir[part]
                else:
                    raise ValueError(f"'{part}' is not a directory.")
            elif part:
                raise ValueError(f"Directory '{part}' does not exist.")

        self.current_path = new_path.rstrip("/")

    def get_current_dir(self):
        #Возвращает текущую директорию как словарь.
        path_parts = self.current_path.strip("/").split("/") if self.current_path.strip("/") else []
        current_dir = self.fs
        for part in path_parts:
            current_dir = current_dir[part]
        return current_dir

    def get_parent_dir(self, path):
        #Возвращает родительскую директорию для заданного пути.
        path_parts = path.strip("/").split("/") if path.strip("/") else []
        current_dir = self.fs
        for part in path_parts[:-1]:
            current_dir = current_dir[part]
        return current_dir

    def write_file(self, filename, content):
        parts = self.current_path.strip('/').split('/')
        d = self.fs
        for part in parts:
            if part:
                d = d.get(part, {})
        d[filename] = content


class ShellEmulator:
    def __init__(self, vfs, username, log_path):
        self.vfs = vfs
        self.username = username
        self.log_path = log_path

    def execute_command(self, command):
        try:
            if command == "ls":
                return "\n".join(self.vfs.list_directory())
            elif command.startswith("cd"):
                self.vfs.change_directory(command[3:])
                return ""
            elif command == "pwd":
                return self.vfs.current_path
            elif command == "clear":
                return "CLEAR" #"\033[H\033[J"
            elif command == "date":
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elif command == "exit":
                return "exit"
            else:
                return "Unknown command"
        except Exception as e:
            return str(e)

    def log_command(self, command):
        entry = {"user": self.username, "command": command, "timestamp": datetime.now().isoformat()}
        with open(self.log_path, "a") as log_file:
            log_file.write(json.dumps(entry) + "\n")
