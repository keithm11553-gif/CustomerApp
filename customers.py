import json
import os
import sys
import tkinter as tk
from tkinter import messagebox


def app_folder():
    # When frozen by PyInstaller, save beside the application.
    # When run as a script, save beside the .py file.
    if getattr(sys, "frozen", False):
        folder = os.path.dirname(sys.executable)
        if sys.platform == "darwin":
            # On a Mac the executable sits inside the .app bundle
            # (CustomerApp.app/Contents/MacOS). "Beside the application"
            # means beside the bundle, three levels up.
            folder = os.path.dirname(os.path.dirname(os.path.dirname(folder)))
        return folder
    return os.path.dirname(os.path.abspath(__file__))


DATA_FILE = os.path.join(app_folder(), "customers.json")


def load_customers():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_customers(customers):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, indent=2)


class CustomerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CustomerApp")
        self.geometry("560x380")
        self.customers = load_customers()

        tk.Label(self, text="Customers").pack(anchor="w", padx=10, pady=(10, 0))
        self.listbox = tk.Listbox(self, width=60, height=9)
        self.listbox.pack(padx=10, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        form = tk.Frame(self)
        form.pack(padx=10, pady=5, fill="x")
        self.entries = {}
        for i, field in enumerate(["Name", "Address", "Phone", "Email"]):
            tk.Label(form, text=field, width=8, anchor="w").grid(row=i, column=0, pady=2)
            e = tk.Entry(form, width=50)
            e.grid(row=i, column=1, pady=2)
            self.entries[field.lower()] = e

        buttons = tk.Frame(self)
        buttons.pack(pady=8)
        tk.Button(buttons, text="Add", width=10, command=self.add_customer).pack(side="left", padx=4)
        tk.Button(buttons, text="Update", width=10, command=self.update_customer).pack(side="left", padx=4)
        tk.Button(buttons, text="Delete", width=10, command=self.delete_customer).pack(side="left", padx=4)
        tk.Button(buttons, text="Clear", width=10, command=self.clear_fields).pack(side="left", padx=4)

        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for c in self.customers:
            self.listbox.insert(tk.END, c.get("name", ""))

    def read_fields(self):
        return {k: e.get().strip() for k, e in self.entries.items()}

    def clear_fields(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.listbox.selection_clear(0, tk.END)

    def selected_index(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def on_select(self, _event=None):
        idx = self.selected_index()
        if idx is None:
            return
        c = self.customers[idx]
        for k, e in self.entries.items():
            e.delete(0, tk.END)
            e.insert(0, c.get(k, ""))

    def add_customer(self):
        data = self.read_fields()
        if not data["name"]:
            messagebox.showwarning("Missing name", "Please enter at least a name.")
            return
        self.customers.append(data)
        save_customers(self.customers)
        self.refresh_list()
        self.clear_fields()

    def update_customer(self):
        idx = self.selected_index()
        if idx is None:
            messagebox.showwarning("Nothing selected", "Select a customer to update first.")
            return
        data = self.read_fields()
        if not data["name"]:
            messagebox.showwarning("Missing name", "Please enter at least a name.")
            return
        self.customers[idx] = data
        save_customers(self.customers)
        self.refresh_list()

    def delete_customer(self):
        idx = self.selected_index()
        if idx is None:
            messagebox.showwarning("Nothing selected", "Select a customer to delete first.")
            return
        del self.customers[idx]
        save_customers(self.customers)
        self.refresh_list()
        self.clear_fields()


if __name__ == "__main__":
    CustomerApp().mainloop()
