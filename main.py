import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("650x520")
        
        self.history_file = "password_history.json"
        self.history = []
        self.load_history()
        self.setup_ui()

    def setup_ui(self):
        # --- Блок настроек ---
        settings_frame = tk.LabelFrame(self.root, text="Настройки пароля", padx=15, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=10)

        # Ползунок длины
        tk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_scale = tk.Scale(
            settings_frame, from_=4, to=32, orient="horizontal", 
            variable=self.length_var, tickinterval=7, length=350
        )
        self.length_scale.grid(row=0, column=1, columnspan=2, sticky="ew", padx=10)
        tk.Label(settings_frame, textvariable=self.length_var, font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5)

        # Чекбоксы символов
        self.use_letters = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=False)

        tk.Checkbutton(settings_frame, text="Буквы (a-z, A-Z)", variable=self.use_letters).grid(row=1, column=0, sticky="w", pady=5)
        tk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=1, sticky="w")
        tk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%)", variable=self.use_special).grid(row=1, column=2, sticky="w")

        settings_frame.columnconfigure(1, weight=1)

        # --- Блок генерации и отображения ---
        gen_frame = tk.Frame(self.root)
        gen_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(gen_frame, text="🔑 Сгенерировать", command=self.generate_password, 
                  bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(side="left", fill="x", expand=True, padx=2)
        
        tk.Button(gen_frame, text="📋 Копировать", command=self.copy_password, 
                  bg="#2196F3", fg="white").pack(side="left", fill="x", expand=True, padx=2)

        self.password_var = tk.StringVar()
        self.result_entry = tk.Entry(gen_frame, textvariable=self.password_var, 
                                     font=("Consolas", 13), justify="center", state="readonly")
        self.result_entry.pack(fill="x", padx=2)

        # --- Таблица истории ---
        hist_frame = tk.LabelFrame(self.root, text="История генераций", padx=10, pady=10)
        hist_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("time", "password", "length", "types")
        self.tree = ttk.Treeview(hist_frame, columns=columns, show="headings")
        
        self.tree.heading("time", text="Время")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("types", text="Типы символов")

        self.tree.column("time", width=130)
        self.tree.column("password", width=250)
        self.tree.column("length", width=50, anchor="center")
        self.tree.column("types", width=150)

        scrollbar = ttk.Scrollbar(hist_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(hist_frame, text="🗑 Очистить историю", command=self.clear_history, 
                  bg="#f44336", fg="white").pack(pady=5, fill="x")

        self.update_history_view()

    def generate_password(self):
        length = self.length_var.get()
        
        # Валидация длины
        if length < 4 or length > 32:
            messagebox.showwarning("Ошибка ввода", "Длина пароля должна быть от 4 до 32 символов.")
            return

        # Формирование пула символов
        char_pool = ""
        selected_types = []
        
        if self.use_letters.get():
            char_pool += string.ascii_letters
            selected_types.append("Буквы")
        if self.use_digits.get():
            char_pool += string.digits
            selected_types.append("Цифры")
        if self.use_special.get():
            char_pool += string.punctuation
            selected_types.append("Спецсимволы")

        if not char_pool:
            messagebox.showwarning("Ошибка ввода", "Выберите хотя бы один тип символов!")
            return

        # Генерация пароля
        password = ''.join(random.choice(char_pool) for _ in range(length))
        self.password_var.set(password)

        # Запись в историю
        entry = {
            "password": password,
            "length": length,
            "types": ", ".join(selected_types),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.insert(0, entry)
        # Ограничиваем историю 50 записями для производительности
        if len(self.history) > 50:
            self.history.pop()
            
        self.save_history()
        self.update_history_view()

    def copy_password(self):
        pwd = self.password_var.get()
        if not pwd:
            messagebox.showinfo("Информация", "Сначала сгенерируйте пароль.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(pwd)
        messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")

    def update_history_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in self.history:
            self.tree.insert("", "end", values=(
                item["time"], 
                item["password"], 
                item["length"], 
                item["types"]
            ))

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except IOError:
            messagebox.showerror("Ошибка", "Не удалось сохранить историю.")

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.history = []

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю генераций?"):
            self.history = []
            self.save_history()
            self.update_history_view()
            self.password_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    # Применение темы для современного вида
    style = ttk.Style()
    style.theme_use("clam")
    app = PasswordGeneratorApp(root)
    root.mainloop()
