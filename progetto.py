import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import customtkinter as ctk

class MacCommandManager:
    def __init__(self, root):
        self.root = root
        self.command_history = []

        # Configura UI
        self.setup_ui()

    def show_entry_fields(self, label_text, is_file=True):
        # Clear any existing entries
        for widget in self.entry_frame.winfo_children():
            widget.destroy()

        # Create label and entry fields based on type
        label = ctk.CTkLabel(self.entry_frame, text=label_text)
        label.pack(padx=5, pady=5)

        self.entry = ctk.CTkEntry(self.entry_frame, width=200)
        self.entry.pack(padx=5, pady=5)

        # Create submit button
        submit_button = ctk.CTkButton(self.entry_frame, text="Conferma", command=lambda: self.confirm_action(is_file))
        submit_button.pack(pady=5)

    def confirm_action(self, is_file):
        if is_file:
            self.run_touch()
        else:
            self.run_mkdir()

    def run_mkdir(self):
        # Clear previous output
        self.output_listbox.delete(0, tk.END)

        dir_name = self.entry.get()
        if not dir_name.strip():
            messagebox.showerror("Errore", "Inserisci un nome di directory valido.")
            return

        confirm = messagebox.askyesno("Conferma", f"Vuoi creare la directory '{dir_name}'?")
        if not confirm:
            return

        try:
            target_dir = filedialog.askdirectory(title="Seleziona la directory in cui creare la cartella")
            if not target_dir:
                messagebox.showerror("Errore", "Seleziona una directory valida.")
                return

            command = ["mkdir", os.path.join(target_dir, dir_name)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.command_history.append(command)

            self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")
            if result.returncode == 0:
                self.output_listbox.insert(tk.END, f"Directory '{dir_name}' creata con successo in '{target_dir}'.")
                messagebox.showinfo("Successo", "Directory creata con successo.")
            else:
                messagebox.showerror("Errore", f"Errore durante la creazione: {result.stderr}")

        except Exception as e:
            self.output_listbox.insert(tk.END, f"Errore durante mkdir: {str(e)}")

    def run_touch(self):
        # Clear previous output
        self.output_listbox.delete(0, tk.END)

        file_name = self.entry.get()
        if not file_name.strip():
            messagebox.showerror("Errore", "Inserisci un nome di file valido.")
            return

        confirm = messagebox.askyesno("Conferma", f"Vuoi creare il file '{file_name}'?")
        if not confirm:
            return

        try:
            target_dir = filedialog.askdirectory(title="Seleziona la directory in cui creare il file")
            if not target_dir:
                messagebox.showerror("Errore", "Seleziona una directory valida.")
                return

            command = ["touch", os.path.join(target_dir, file_name)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.command_history.append(command)

            self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")
            if result.returncode == 0:
                self.output_listbox.insert(tk.END, f"File '{file_name}' creato con successo in '{target_dir}'.")
                messagebox.showinfo("Successo", "File creato con successo.")
            else:
                messagebox.showerror("Errore", f"Errore durante la creazione del file: {result.stderr}")

        except Exception as e:
            self.output_listbox.insert(tk.END, f"Errore durante touch: {str(e)}")

    def run_ls(self):
        # Clear previous output
        self.output_listbox.delete(0, tk.END)

        directory = filedialog.askdirectory()
        if not directory:
            messagebox.showerror("Errore", "Seleziona una directory valida.")
            return
        try:
            command = ["ls", directory]
            result = subprocess.run(command, capture_output=True, text=True)
            self.command_history.append(command)

            self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")
            if result.returncode == 0:
                self.output_listbox.insert(tk.END, f"Contenuto della directory '{directory}':")
                for line in result.stdout.splitlines():
                    self.output_listbox.insert(tk.END, line)
            else:
                messagebox.showerror("Errore", f"Errore durante ls: {result.stderr}")

        except Exception as e:
            self.output_listbox.insert(tk.END, f"Errore durante ls: {str(e)}")

    def run_rm(self):
        # Clear previous output
        self.output_listbox.delete(0, tk.END)

        file_name = filedialog.askopenfilename()
        if not file_name:
            messagebox.showerror("Errore", "Seleziona un file valido.")
            return

        confirm = messagebox.askyesno("Conferma", f"Vuoi rimuovere il file '{file_name}'?")
        if not confirm:
            return

        try:
            command = ["rm", file_name]
            result = subprocess.run(command, capture_output=True, text=True)
            self.command_history.append(command)

            self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")
            if result.returncode == 0:
                self.output_listbox.insert(tk.END, f"File '{file_name}' rimosso con successo.")
                messagebox.showinfo("Successo", "File rimosso con successo.")
            else:
                messagebox.showerror("Errore", f"Errore durante la rimozione del file: {result.stderr}")

        except Exception as e:
            self.output_listbox.insert(tk.END, f"Errore durante rm: {str(e)}")

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Frame per output
        self.output_listbox = tk.Listbox(self.root, height=10, width=80)
        self.output_listbox.pack(pady=20)

        # Frame per i comandi
        commands_frame = ctk.CTkFrame(self.root)
        commands_frame.pack(pady=20)

        # Left column buttons
        left_frame = ctk.CTkFrame(commands_frame)
        left_frame.pack(side=tk.LEFT, padx=10)

        btn_mkdir = ctk.CTkButton(left_frame, text="Crea Directory", command=lambda: self.show_entry_fields("Inserisci nome directory:", is_file=False))
        btn_mkdir.pack(pady=5)

        btn_touch = ctk.CTkButton(left_frame, text="Crea File", command=lambda: self.show_entry_fields("Inserisci nome file:", is_file=True))
        btn_touch.pack(pady=5)

        # Right column buttons
        right_frame = ctk.CTkFrame(commands_frame)
        right_frame.pack(side=tk.RIGHT, padx=10)

        btn_ls = ctk.CTkButton(right_frame, text="Elenca Contenuto Dir", command=self.run_ls)
        btn_ls.pack(pady=5)

        btn_rm = ctk.CTkButton(right_frame, text="Rimuovi File", command=self.run_rm)
        btn_rm.pack(pady=5)

        # Frame per le entry
        self.entry_frame = ctk.CTkFrame(self.root)
        self.entry_frame.pack(pady=10)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Mac Command Manager")
    app = MacCommandManager(root)
    app.start()
