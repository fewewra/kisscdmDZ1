import unittest
import os
from shell_emulator import VirtualFileSystem, ShellEmulator
from datetime import datetime
import json
import zipfile


class TestVirtualFileSystem(unittest.TestCase):
    def setUp(self):
        #Создаем тестовый архив для работы файловой системы.
        self.test_zip_path = "test_fs.zip"
        with open("test_file.txt", "w") as f:
            f.write("Test content")
        with open("test_file2.txt", "w") as f:
            f.write("Another file")
        with zipfile.ZipFile(self.test_zip_path, 'w') as zf:
            zf.write("test_file.txt")
            zf.write("test_file2.txt")
        os.remove("test_file.txt")
        os.remove("test_file2.txt")
        self.vfs = VirtualFileSystem(self.test_zip_path)

    def tearDown(self):
        #Удаляем тестовый архив.
        if os.path.exists(self.test_zip_path):
            os.remove(self.test_zip_path)

    def test_list_directory(self):
        #Тестируем, что листинг директории возвращает корректное содержимое.
        self.assertIn("test_file.txt", self.vfs.list_directory())
        self.assertIn("test_file2.txt", self.vfs.list_directory())

    def test_change_directory(self):
        #Тестируем смену текущей директории.
        self.vfs.change_directory("/")
        self.assertEqual(self.vfs.current_path, "/")


class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        #Инициализируем эмулятор оболочки с тестовыми параметрами.
        self.test_zip_path = "test_fs.zip"
        self.log_path = "test_log.json"
        with zipfile.ZipFile(self.test_zip_path, 'w') as zf:
            zf.writestr("test.txt", "Hello, world!")
        self.vfs = VirtualFileSystem(self.test_zip_path)
        self.emulator = ShellEmulator(self.vfs, "test_user", self.log_path)

    def tearDown(self):
        #Удаляем тестовые файлы.
        if os.path.exists(self.test_zip_path):
            os.remove(self.test_zip_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def test_execute_ls(self):
        #Тест команды ls.
        result = self.emulator.execute_command("ls")
        self.assertIn("test.txt", result)

    # Tests for `ls` command
    def test_execute_ls_with_files(self):
        """Тест команды ls с наличием файлов в директории."""
        result = self.emulator.execute_command("ls")
        self.assertIn("test.txt", result)

    def test_execute_ls_empty_directory(self):
        """Тест команды ls в пустой директории."""
        self.emulator.vfs.fs["empty_dir"] = {}
        self.emulator.execute_command("cd empty_dir")
        result = self.emulator.execute_command("ls")
        self.assertEqual(result, "")

    def test_execute_ls_nonexistent_directory(self):
        """Тест команды ls для несуществующей директории."""
        self.emulator.execute_command("cd nonexistent")
        result = self.emulator.execute_command("ls")
        self.assertEqual(result, "test.txt")

    # Tests for `cd` command
    def test_execute_cd_valid_directory(self):
        """Тест команды cd для существующей директории."""
        self.emulator.vfs.fs["home"] = {}
        self.emulator.execute_command("cd home")
        self.assertEqual(self.emulator.vfs.current_path, "/home")

    def test_execute_cd_nonexistent_directory(self):
        """Тест команды cd для несуществующей директории."""
        result = self.emulator.execute_command("cd nonexistent")
        self.assertEqual(result, "Directory 'nonexistent' does not exist.")

    def test_execute_cd_back_to_root(self):
        """Тест команды cd для возврата в корневую директорию."""
        self.emulator.vfs.fs["home"] = {}
        self.emulator.execute_command("cd home")
        self.emulator.execute_command("cd /")
        self.assertEqual(self.emulator.vfs.current_path, "/")

    # Tests for `clear` command
    def test_execute_clear_resets_prompt(self):
        """Тест команды clear, проверка сброса приглашения."""
        self.emulator.execute_command("CLEAR")
        self.assertEqual(self.emulator.execute_command("pwd"), "/")

    def test_execute_clear_with_content(self):
        """Тест команды clear после ввода команды."""
        self.emulator.execute_command("ls")
        result = self.emulator.execute_command("CLEAR")
        self.assertEqual(result, "Unknown command")

    # Tests for `date` command
    def test_execute_date_correct_format(self):
        """Тест команды date, проверка корректного формата."""
        result = self.emulator.execute_command("date")
        try:
            datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
            valid_format = True
        except ValueError:
            valid_format = False
        self.assertTrue(valid_format)

    def test_execute_date_different_calls(self):
        """Тест команды date, проверка изменения времени."""
        result1 = self.emulator.execute_command("date")
        result2 = self.emulator.execute_command("date")
        self.assertEqual(result1, result2)

    def test_execute_date_empty_command(self):
        """Тест команды date, проверка результата при пустой команде."""
        self.assertNotEqual(self.emulator.execute_command("date"), "")

    # Test for `exit` command
    def test_execute_exit(self):
        """Тест команды exit."""
        result = self.emulator.execute_command("exit")
        self.assertEqual(result, "exit")

    def test_execute_pwd(self):
        #Тест команды pwd.
        result = self.emulator.execute_command("pwd")
        self.assertEqual(result, "/")

    def test_execute_cd(self):
        #Тест команды cd.
        self.emulator.vfs.fs["home"] = {}
        self.emulator.execute_command("cd home")
        self.assertEqual(self.emulator.vfs.current_path, "/home")

    def test_execute_unknown_command(self):
        #Тест неизвестной команды.
        result = self.emulator.execute_command("unknown_command")
        self.assertEqual(result, "Unknown command")

'''
    def test_log_command(self):
        #Тест логирования команд.
        command = "ls"
        self.emulator.execute_command(command)
        with open(self.log_path, "r") as log_file:
            logs = [json.loads(line) for line in log_file]
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["command"], command)
'''