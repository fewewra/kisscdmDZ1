import tkinter as tk

class ShellGUI:
    def __init__(self, emulator):
        self.emulator = emulator
        self.window = tk.Tk()
        self.window.title("Shell Emulator")

        self.output = tk.Text(self.window, wrap="word", state="normal", height=20, width=80, bg="black", fg="white", insertbackground="white")
        self.output.pack(expand=True, fill="both")

        self.output.bind("<Return>", self.handle_input)
        self.output.insert("end", f"Welcome to Shell Emulator! Type your commands below.\n\n{self.get_prompt()}")
        self.output.mark_set("insert", "end")
        self.output.see("end")

        self.window.mainloop()

    def reset_terminal(self):
        #Сбрасывает терминал к начальному состоянию: очищает экран и устанавливает начальную директорию.
        self.emulator.vfs.change_directory("/")  # Возвращаемся в корневую директорию
        self.output.delete(1.0, tk.END)  # Очищаем экран
        self.output.insert("end", f"Welcome to Shell Emulator! Type your commands below.\n\n")

    def handle_input(self, event):
        input_text = self.get_last_input()
        command = input_text.strip()
        if command:
            self.output.delete(f"insert linestart", "insert")
            self.output.insert("end", f"{self.get_prompt()}{command}\n")
            result = self.emulator.execute_command(command)
            if result == "exit":
                self.window.quit()
            elif result == "CLEAR":
                self.reset_terminal()  # Полная очистка и сброс терминала #clear_screen()  # Выполняем очистку экрана
            else:
                self.output.insert("end", f"{result}\n")

            self.emulator.log_command(command)

        self.add_prompt()  # Добавляем новую строку приглашения
        self.output.see("end")
        return "break"

    def get_last_input(self):
        last_line = self.output.get("insert linestart", "insert").strip()
        prompt = self.get_prompt().strip()
        return last_line[len(prompt):] if last_line.startswith(prompt) else last_line

    def get_prompt(self):
        return f"{self.emulator.username}@shell: {self.emulator.vfs.current_path}$ "

    def add_prompt(self):
        # Добавляет строку приглашения в терминал.
        self.output.insert("end", self.get_prompt())
