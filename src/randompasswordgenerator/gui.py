import tkinter as tk
from tkinter import messagebox
import manager
import generator
import pyperclip
import threading
from randompasswordgenerator import clear_clipboard

class PasswordManagerGui:
    def __init__(self, root):

        self.root = root
        self.root.title("PassGen Vault")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        try:
            self.vault = manager.VaultManager()
        except Exception as e:
            messagebox.showerror("Initialization Error",f"Failed to load Vault:\n{e}")
            self.root.destroy()
            return

        self.service_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.length_var = tk.IntVar(value = 8)
        self.numbers_var = tk.BooleanVar(value = True)
        self.special_var = tk.BooleanVar(value = True)

        self.build_ui()

    def _action_generate(self):
        s = self.service_var.get()
        u = self.username_var.get()
        l = self.length_var.get()
        n = self.numbers_var.get()
        c = self.special_var.get()
        if s == "" or u == "":
            messagebox.showwarning("Error", "Either Service or Username is empty.")
            return
        if l < 4:
            messagebox.showwarning("Error", "Password's length can't be less than 4.")
            return
        if self.vault.check_service_exists(s, u) == True:
            decision = messagebox.askyesno("Collision",
                                           "Record for this service and username already exists. Overwrite?")
            if decision is False:
                return

        result = generator.generate(l, n, c)
        pyperclip.copy(result)
        timer = threading.Timer(60.0, clear_clipboard.clear_clip)
        timer.start()

        self.vault.store_password(s, u, result)
        messagebox.showinfo("Success", "The password has been generated and stored in the db.")

    def _action_retrieve(self):

        s = self.service_var.get()
        u = self.username_var.get()

        if s == "" or u == "":
            messagebox.showwarning("Error", "Either Service or Username is empty.")
            return

        self.vault.retrieve_password(s, u)

    def _action_delete(self):

        s = self.service_var.get()
        u = self.username_var.get()

        if s == "" or u == "":
            messagebox.showwarning("Error", "Either Service or Username is empty.")
            return

        decision = messagebox.askyesno("Confirmation", "Do you really want to delete the password?")
        if decision:
            self.vault.delete_password(s, u)
            messagebox.showinfo("Done", "Record removed.")

    def build_ui(self):

        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True)

        service_label = tk.Label(main_frame, text = "Service")
        service_label.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = "e")

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

        numbers_check = tk.Checkbutton(main_frame, text="Include Numbers", variable=self.numbers_var)
        numbers_check.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        special_check = tk.Checkbutton(main_frame, text="Include Special Characters", variable=self.special_var)
        special_check.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        generate_button = tk.Button(main_frame, text="Generate Password", command=self._action_generate)
        generate_button.grid(row=5, columnspan=2, padx=10, pady=15)

        retrieve_button = tk.Button(main_frame, text="Retrieve Username and Password", command=self._action_retrieve)
        retrieve_button.grid(row=6, column=0, padx=10, pady=15, sticky="ew")

        delete_button = tk.Button(main_frame, text="Delete Record", command=self._action_delete)
        delete_button.grid(row=6, column=1, padx=10, pady=20, sticky="ew")


def run_gui():

    root = tk.Tk()
    app = PasswordManagerGui(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()