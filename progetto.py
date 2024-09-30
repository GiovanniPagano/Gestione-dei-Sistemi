import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import os
import customtkinter as ctk

class UbuntuCommandManager:
    def __init__(self, root):
        self.root = root
        self.command_history = []

        # Configura UI
        self.setup_ui()

    def create_user(self, username):
        # Pulisci output precedente
        self.output_listbox.delete(0, tk.END)

        # Verifica che il nome utente sia valido
        if not username or not username.isalnum() or len(username) < 3:
            messagebox.showerror("Errore", "Il nome utente non è valido. Deve contenere solo lettere e numeri e avere almeno 3 caratteri.")
            return

        try:
            # Comando per aggiungere l'utente
            command = ["sudo", "useradd", "-m", username]  # -m crea la home directory
            result = subprocess.run(command, capture_output=True, text=True)

            # Controlla il risultato del comando
            if result.returncode == 0:
                self.output_listbox.insert(tk.END, f"Utente '{username}' creato con successo.")
                messagebox.showinfo("Successo", f"Utente '{username}' creato con successo.")
                self.load_users()  # Ricarica la lista degli utenti
            else:
                messagebox.showerror("Errore", f"Errore durante la creazione dell'utente: {result.stderr}")

        except Exception as e:
            self.output_listbox.insert(tk.END, f"Errore durante la creazione dell'utente: {str(e)}")

    def show_entry_fields(self):
        username = simpledialog.askstring("Input", "Inserisci nome utente:")
        if username:
            self.create_user(username)

    def show_moduser_options(self):
        # Clear any existing entries
        for widget in self.entry_frame.winfo_children():
            widget.destroy()

        # Crea una label e un menu a tendina per le opzioni di moduser
        label = ctk.CTkLabel(self.entry_frame, text="Seleziona il tipo di modifica per l'utente:")
        label.pack(padx=5, pady=5)

        # Opzioni disponibili per usermod
        self.option_var = tk.StringVar(value="-L")  # Valore di default
        moduser_options = ["-L (Blocca l'utente)", "-U (Sblocca l'utente)", "-p (Cambia la password)", "-g (Cambia il gruppo)", "-l (Cambia il nome utente)"]

        # Menu a tendina
        self.option_menu = ctk.CTkOptionMenu(self.entry_frame, variable=self.option_var, values=moduser_options)
        self.option_menu.pack(padx=5, pady=5)

        # Crea un pulsante di conferma
        submit_button = ctk.CTkButton(self.entry_frame, text="Conferma", command=self.confirm_mod_user)
        submit_button.pack(pady=5)

    def confirm_mod_user(self):
        # Pulisci output precedente
        self.output_listbox.delete(0, tk.END)

        # Seleziona l'utente attivo
        selected_user = self.user_listbox.get(tk.ACTIVE)
        if not selected_user:
            messagebox.showerror("Errore", "Seleziona un utente dalla lista.")
            return

        # Estrae l'opzione selezionata dal menu a tendina
        selected_option = self.option_var.get().split()[0]

        # Gestisce il comportamento in base all'opzione selezionata
        if selected_option in ["-L", "-U"]:
            # Blocca o sblocca l'utente senza parametri aggiuntivi
            command = ["sudo", "usermod", selected_option, selected_user]
        elif selected_option == "-p":
            # Chiede la nuova password
            new_password = simpledialog.askstring("Cambia Password", "Inserisci la nuova password per l'utente:")
            if not new_password:
                messagebox.showerror("Errore", "Inserisci una password valida.")
                return
            command = ["sudo", "usermod", selected_option, new_password, selected_user]
        elif selected_option == "-g":
            # Chiede il nuovo gruppo
            new_group = simpledialog.askstring("Cambia Gruppo", "Inserisci il nuovo gruppo per l'utente:")
            if not new_group:
                messagebox.showerror("Errore", "Inserisci un gruppo valido.")
                return
            command = ["sudo", "usermod", selected_option, new_group, selected_user]
        elif selected_option == "-l":
            # Chiede il nuovo nome utente
            new_username = simpledialog.askstring("Cambia Nome Utente", "Inserisci il nuovo nome utente:")
            if not new_username:
                messagebox.showerror("Errore", "Inserisci un nome utente valido.")
                return

            # Modifica anche la home directory
            command = ["sudo", "usermod", "-l", new_username, selected_user]

            # Cambia anche la home directory
            old_home_dir = f"/home/{selected_user}"
            new_home_dir = f"/home/{new_username}"
            try:
                os.rename(old_home_dir, new_home_dir)  # Cambia il nome della home directory
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile rinominare la directory home: {str(e)}")
                return

            command += ["-d", new_home_dir]  # Aggiungi l'opzione per la nuova home directory

        # Esegui il comando
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            self.command_history.append(command)

            self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")
            if result.returncode == 0:
                self.output_listbox.insert(tk.END, f"Modifica dell'utente '{selected_user}' riuscita con successo.")
                messagebox.showinfo("Successo", "Modifica utente riuscita con successo.")
                self.load_users()  # Ricarica la lista degli utenti
            else:
                messagebox.showerror("Errore", f"Errore durante la modifica dell'utente: {result.stderr}")

        except Exception as e:
            self.output_listbox.insert(tk.END, f"Errore durante la modifica dell'utente: {str(e)}")

    def delete_non_root_users(self):
        # Clear previous output
        self.output_listbox.delete(0, tk.END)

        selected_user = self.user_listbox.get(tk.ACTIVE)
        if not selected_user:
            messagebox.showerror("Errore", "Seleziona un utente dalla lista.")
            return

        confirm = messagebox.askyesno("Conferma", f"Vuoi eliminare l'utente '{selected_user}'?")
        if not confirm:
            return

        try:
            command = ["sudo", "userdel", "-r", selected_user]  # Comando per eliminare l'utente e la home directory
            result = subprocess.run(command, capture_output=True, text=True)
            self.command_history.append(command)

            self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")
            if result.returncode == 0:
                self.output_listbox.insert(tk.END, f"Utente '{selected_user}' eliminato con successo.")
                messagebox.showinfo("Successo", "Utente eliminato con successo.")
                self.load_users()  # Ricarica la lista degli utenti dopo l'eliminazione
            else:
                messagebox.showerror("Errore", f"Errore durante l'eliminazione dell'utente: {result.stderr}")

        except Exception as e:
            self.output_listbox.insert(tk.END, f"Errore durante l'eliminazione dell'utente: {str(e)}")

    def load_users(self):
        # Carica la lista degli utenti che hanno una home directory in /home
        self.user_listbox.delete(0, tk.END)
        try:
            users_with_home = []
            for user_dir in os.listdir("/home"):
                if os.path.isdir(os.path.join("/home", user_dir)):
                    users_with_home.append(user_dir)

            if "amministratore" in users_with_home:
                users_with_home.remove("amministratore")  # Non includere root tra gli utenti da eliminare

            for user in users_with_home:
                self.user_listbox.insert(tk.END, user)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il caricamento degli utenti: {str(e)}")

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

        btn_create_user = ctk.CTkButton(left_frame, text="Crea Utente", command=self.show_entry_fields)
        btn_create_user.pack(pady=5)

        btn_mod_user = ctk.CTkButton(left_frame, text="Modifica Utente", command=self.show_moduser_options)
        btn_mod_user.pack(pady=5)

        btn_delete_user = ctk.CTkButton(left_frame, text="Elimina Utente", command=self.delete_non_root_users)
        btn_delete_user.pack(pady=5)

        # Right column buttons
        right_frame = ctk.CTkFrame(commands_frame)
        right_frame.pack(side=tk.RIGHT, padx=10)

        self.user_listbox = tk.Listbox(right_frame, height=10, width=40)
        self.user_listbox.pack(pady=5)

        # Popola la lista degli utenti con directory in /home
        self.load_users()

        # Frame per le opzioni di input
        self.entry_frame = ctk.CTkFrame(self.root)
        self.entry_frame.pack(pady=10)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Ubuntu Command Manager")
    app = UbuntuCommandManager(root)
    app.start()
