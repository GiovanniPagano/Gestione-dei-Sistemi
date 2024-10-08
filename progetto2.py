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

        # Chiede la password per il nuovo utente
        password = simpledialog.askstring("Input", "Inserisci la password per l'utente:", show='*')
        if not password:
            messagebox.showerror("Errore", "Devi inserire una password valida.")
            return

        try:
            # Comando per aggiungere l'utente
            command = ["sudo", "useradd", "-m", username]  # -m crea la home directory
            self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")  # Stampa il comando
            result = subprocess.run(command, capture_output=True, text=True)

            # Controlla il risultato del comando
            if result.returncode == 0:
                self.command_history.append(command)
                # Imposta la password per il nuovo utente
                passwd_command = ["sudo", "passwd", username]
                self.output_listbox.insert(tk.END, f"Comando: {' '.join(passwd_command)}")  # Stampa il comando
                process = subprocess.Popen(passwd_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                process.communicate(input=f"{password}\n{password}\n")  # Imposta la nuova password
                
                if process.returncode == 0:
                    self.output_listbox.insert(tk.END, f"Utente '{username}' creato con successo.")
                    messagebox.showinfo("Successo", f"Utente '{username}' creato con successo.")
                    self.load_users()  # Ricarica la lista degli utenti
                else:
                    self.output_listbox.insert(tk.END, f"Errore durante l'impostazione della password: {process.stderr}")
                    messagebox.showerror("Errore", f"Errore durante l'impostazione della password: {process.stderr}")

            else:
                self.output_listbox.insert(tk.END, f"Errore durante la creazione dell'utente: {result.stderr}")
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
        command = []  # Inizializza la variabile command

        # Gestisce il comportamento in base all'opzione selezionata
        if selected_option in ["-L", "-U"]:
            # Blocca o sblocca l'utente senza parametri aggiuntivi
            command = ["sudo", "usermod", selected_option, selected_user]
        elif selected_option == "-p":
            # Chiede la nuova password
            new_password = simpledialog.askstring("Cambia Password", "Inserisci la nuova password per l'utente:", show='*')
            if not new_password:
                messagebox.showerror("Errore", "Inserisci una password valida.")
                return

            try:
                # Usa il comando passwd per cambiare la password
                passwd_command = ["sudo", "passwd", selected_user]
                self.output_listbox.insert(tk.END, f"Comando: {' '.join(passwd_command)}")  # Stampa il comando
                process = subprocess.Popen(passwd_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                process.communicate(input=f"{new_password}\n{new_password}\n")  # Imposta la nuova password

                if process.returncode == 0:
                    self.output_listbox.insert(tk.END, f"Password per '{selected_user}' modificata con successo.")
                    messagebox.showinfo("Successo", "Password modificata con successo.")
                else:
                    self.output_listbox.insert(tk.END, f"Errore durante la modifica della password: {process.stderr}")
                    messagebox.showerror("Errore", f"Errore durante la modifica della password: {process.stderr}")

            except Exception as e:
                self.output_listbox.insert(tk.END, f"Errore durante la modifica della password: {str(e)}")

            return  # Uscita dalla funzione, non eseguire il comando successivamente

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
                self.output_listbox.insert(tk.END, f"Comando: os.rename('{old_home_dir}', '{new_home_dir}')")  # Stampa l'operazione di rinomina
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile rinominare la directory home: {str(e)}")
                return

            command += ["-d", new_home_dir]  # Aggiungi l'opzione per la nuova home directory

        # Esegui il comando
        try:
            if command:  # Controlla se il comando è stato impostato
                self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")  # Stampa il comando
                result = subprocess.run(command, capture_output=True, text=True)
                self.command_history.append(command)

                if result.returncode == 0:
                    self.output_listbox.insert(tk.END, f"Modifica dell'utente '{selected_user}' riuscita con successo.")
                    messagebox.showinfo("Successo", "Modifica utente riuscita con successo.")
                    self.load_users()  # Ricarica la lista degli utenti
                else:
                    self.output_listbox.insert(tk.END, f"Errore durante la modifica dell'utente: {result.stderr}")
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
            self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")  # Stampa il comando
            result = subprocess.run(command, capture_output=True, text=True)
            self.command_history.append(command)

            if result.returncode == 0:
                self.output_listbox.insert(tk.END, f"Utente '{selected_user}' eliminato con successo.")
                messagebox.showinfo("Successo", "Utente eliminato con successo.")
                self.load_users()  # Ricarica la lista degli utenti dopo l'eliminazione
            else:
                self.output_listbox.insert(tk.END, f"Errore durante l'eliminazione dell'utente: {result.stderr}")
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

            for user in users_with_home:
                if user not in ["amministratore", "studente"]:  # Nascondi utenti specifici
                    self.user_listbox.insert(tk.END, user)

        except Exception as e:
            self.output_listbox.insert(tk.END, f"Errore durante il caricamento degli utenti: {str(e)}")

    def create_group(self):
        group_name = simpledialog.askstring("Input", "Inserisci il nome del gruppo da creare:")
        if group_name:
            command = ["sudo", "groupadd", group_name]
            self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")  # Stampa il comando
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                self.command_history.append(command)
                if result.returncode == 0:
                    self.output_listbox.insert(tk.END, f"Gruppo '{group_name}' creato con successo.")
                    messagebox.showinfo("Successo", f"Gruppo '{group_name}' creato con successo.")
                else:
                    self.output_listbox.insert(tk.END, f"Errore durante la creazione del gruppo: {result.stderr}")
                    messagebox.showerror("Errore", f"Errore durante la creazione del gruppo: {result.stderr}")
            except Exception as e:
                self.output_listbox.insert(tk.END, f"Errore durante la creazione del gruppo: {str(e)}")

    def delete_group(self):
        group_name = simpledialog.askstring("Input", "Inserisci il nome del gruppo da eliminare:")
        if group_name:
            confirm = messagebox.askyesno("Conferma", f"Vuoi eliminare il gruppo '{group_name}'?")
            if confirm:
                command = ["sudo", "groupdel", group_name]
                self.output_listbox.insert(tk.END, f"Comando: {' '.join(command)}")  # Stampa il comando
                try:
                    result = subprocess.run(command, capture_output=True, text=True)
                    self.command_history.append(command)
                    if result.returncode == 0:
                        self.output_listbox.insert(tk.END, f"Gruppo '{group_name}' eliminato con successo.")
                        messagebox.showinfo("Successo", f"Gruppo '{group_name}' eliminato con successo.")
                    else:
                        self.output_listbox.insert(tk.END, f"Errore durante l'eliminazione del gruppo: {result.stderr}")
                        messagebox.showerror("Errore", f"Errore durante l'eliminazione del gruppo: {result.stderr}")
                except Exception as e:
                    self.output_listbox.insert(tk.END, f"Errore durante l'eliminazione del gruppo: {str(e)}")

    def setup_ui(self):
        self.entry_frame = ctk.CTkFrame(self.root)
        self.entry_frame.pack(pady=10)

        # Lista utenti
        self.user_listbox = tk.Listbox(self.root)
        self.user_listbox.pack(padx=10, pady=10)

        # Pulsante per creare un nuovo utente
        self.new_user_button = ctk.CTkButton(self.root, text="Crea Utente", command=self.show_entry_fields)
        self.new_user_button.pack(pady=5)

        # Pulsante per modificare un utente
        self.mod_user_button = ctk.CTkButton(self.root, text="Modifica Utente", command=self.show_moduser_options)
        self.mod_user_button.pack(pady=5)

        # Pulsante per eliminare un utente
        self.delete_user_button = ctk.CTkButton(self.root, text="Elimina Utente", command=self.delete_non_root_users)
        self.delete_user_button.pack(pady=5)

        # Pulsante per creare un gruppo
        self.create_group_button = ctk.CTkButton(self.root, text="Crea Gruppo", command=self.create_group)
        self.create_group_button.pack(pady=5)

        # Pulsante per eliminare un gruppo
        self.delete_group_button = ctk.CTkButton(self.root, text="Elimina Gruppo", command=self.delete_group)
        self.delete_group_button.pack(pady=5)

        # Lista di output
        self.output_listbox = tk.Listbox(self.root, height=10, width=80)
        self.output_listbox.pack(padx=10, pady=10)

        # Carica la lista degli utenti all'avvio
        self.load_users()

if __name__ == "__main__":
    # Configura l'aspetto di customtkinter (opzionale)
    ctk.set_appearance_mode("System")  # Modalità: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Temi: "blue", "green", "dark-blue"

    root = ctk.CTk()
    root.title("Gestore Comandi Ubuntu")
    root.geometry("600x600")
    app = UbuntuCommandManager(root)
    root.mainloop()
