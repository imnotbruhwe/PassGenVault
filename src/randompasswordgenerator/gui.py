import tkinter as tk
from tkinter import messagebox
import pyperclip
import threading
from randompasswordgenerator import clear_clipboard, manager, generator


class PasswordManagerGui:
    def __init__(self, root):

        self.root = root
        self.root.title("PassGen Vault")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.vault = None

        self.service_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.length_var = tk.IntVar(value=16)
        self.numbers_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)

        self.master_password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        self.build_login_ui()

    def _action_generate(self):
        s = self.service_var.get()
        u = self.username_var.get()
        try:
            l = self.length_var.get()
        except tk.TclError:
            messagebox.showerror("Error","Length must be a whole number.")
            return
        n = self.numbers_var.get()
        c = self.special_var.get()
        if s == "" or u == "":
            messagebox.showwarning("Error", "Either Service or Username is empty.")
            return
        if l < 12:
            messagebox.showwarning("Error", "Password's length can't be less than 4.")
            return
        if self.vault.check_service_exists(s, u) == True:
            decision = messagebox.askyesno(
                "Collision",
                "Record for this service and username already exists. Overwrite?",
            )
            if decision is False:
                return

        result = generator.generate(l, n, c)
        self.vault.store_password(s, u, result)
        pyperclip.copy(result)
        timer = threading.Timer(60.0, clear_clipboard.clear_clip, args=[result])
        timer.daemon = True
        timer.start()

        messagebox.showinfo(
            "Success",
            "Password has been generated and is stored in clipboard for 60 seconds.",
        )

    def _action_retrieve(self):
        s = self.service_var.get()

        if s == "":
            messagebox.showwarning("Error", "Service field can not be empty.")
            return

        try:
            results = self.vault.retrieve_service_records(s)
        except manager.CorruptedRecordError as e:
            messagebox.showerror("Decryption Error", str(e))
            return

        if len(results) == 0:
            messagebox.showerror("Not Found", f"No records found for service: {s}.")
            return

        display_text = f"Records found for service: {s}\n"
        for username, password in results:
            display_text += f"User: {username}\nPassword: {password}\n"
            display_text += "-" * 30 + "\n"

        messagebox.showinfo("Retrieved Records", display_text)

    def _action_delete(self):

        s = self.service_var.get()
        u = self.username_var.get()

        if s == "" or u == "":
            messagebox.showwarning("Error", "Either Service or Username is empty.")
            return

        decision = messagebox.askyesno(
            "Confirmation", "Do you really want to delete the password?"
        )
        if decision:
            result = self.vault.delete_password(s, u)
            if result:
                messagebox.showinfo("Done", "Record removed.")
            else:
                messagebox.showerror("Error", "Deletion failed. No such record exists.")

    def build_login_ui(self):
        self.is_new_vault = not manager.vault_exists()

        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(expand=True)

        title = (
            "Create your Master Password:\n(it cannot be recovered!)"
            if self.is_new_vault
            else "Enter Master Password:"
        )
        tk.Label(self.login_frame, text=title, font=("Arial", 12)).grid(
            row=0, column=0, columnspan=2, pady=20
        )

        tk.Entry(
            self.login_frame, textvariable=self.master_password_var, show="*"
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        next_row = 2
        if self.is_new_vault:
            tk.Label(self.login_frame, text="Repeat password:").grid(
                row=2, column=0, columnspan=2
            )
            tk.Entry(
                self.login_frame, textvariable=self.confirm_password_var, show="*"
            ).grid(row=3, column=0, columnspan=2, padx=10, pady=10)
            next_row = 4

        button_text = "Create Vault" if self.is_new_vault else "Unlock Vault"
        tk.Button(
            self.login_frame, text=button_text, command=self._action_unlock
        ).grid(row=next_row, column=0, columnspan=2, pady=20)

    def _action_unlock(self):
        p = self.master_password_var.get()
        if p == "":
            messagebox.showwarning("Error", "Master Password can't be empty")
            return

        if self.is_new_vault:
            if len(p) < 12:
                messagebox.showwarning("Error", "Master Password must be at least 12 characters.")
                return
            if p != self.confirm_password_var.get():
                messagebox.showwarning("Error", "Passwords do not match.")
                return

        try:
            self.vault = manager.VaultManager(p)
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to load Vault:\n{e}")
            self.master_password_var.set("")
            self.confirm_password_var.set("")
            return

        self.master_password_var.set("")
        self.confirm_password_var.set("")
        self.login_frame.destroy()
        self.build_ui()


    def build_ui(self):

        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True)

        service_label = tk.Label(main_frame, text="Service")
        service_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        service_entry = tk.Entry(main_frame, textvariable=self.service_var)
        service_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        username_label = tk.Label(main_frame, text="Username")
        username_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        username_entry = tk.Entry(main_frame, textvariable=self.username_var)
        username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        length_label = tk.Label(main_frame, text="Length")
        length_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        length_entry = tk.Entry(main_frame, textvariable=self.length_var)
        length_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        numbers_check = tk.Checkbutton(
            main_frame, text="Include Numbers", variable=self.numbers_var
        )
        numbers_check.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        special_check = tk.Checkbutton(
            main_frame, text="Include Special Characters", variable=self.special_var
        )
        special_check.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        generate_button = tk.Button(
            main_frame, text="Generate Password", command=self._action_generate
        )
        generate_button.grid(row=5, columnspan=2, padx=10, pady=15)

        retrieve_button = tk.Button(main_frame,text="Retrieve Records For Given Service", command=self._action_retrieve)
        retrieve_button.grid(row=6, column=0, padx=10, pady=15, sticky="ew")

        delete_button = tk.Button(
            main_frame, text="Delete Record", command=self._action_delete
        )
        delete_button.grid(row=6, column=1, padx=10, pady=20, sticky="ew")


def run_gui():

    root = tk.Tk()
    app = PasswordManagerGui(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
