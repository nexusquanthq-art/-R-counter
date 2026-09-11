import json
import math
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
DATA_FILE = "trading_tracker.json"
RISK_PERCENT = 0.05          # 1R = 5%
DEFAULT_BALANCE = 100
LIQUIDATION_THRESHOLD = 0.01 # liquidated if balance < 1% of initial
MAX_R = 10000                # hard cap to prevent overflow

# ----------------------------------------------------------------------
# Data handling
# ----------------------------------------------------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # minimal validation
    required = {"balance", "total_R", "trades"}
    if not required.issubset(data.keys()):
        raise ValueError("Corrupted data file.")
    # Migration: add initial_balance if missing
    if "initial_balance" not in data:
        data["initial_balance"] = data["balance"]
    return data

def save_data(data):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    os.replace(tmp, DATA_FILE)

def init_new_data(balance):
    data = {
        "balance": balance,
        "initial_balance": balance,
        "total_R": 0,
        "target": None,
        "trades": []
    }
    save_data(data)
    return data

# ----------------------------------------------------------------------
# Application class
# ----------------------------------------------------------------------
class IronmindApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Ironmind")
        self.root.resizable(False, False)

        self.data = load_data()
        if self.data is None:
            self.first_run_setup()
        else:
            self.build_ui()

    # ------------------------------------------------------------------
    # First-run setup
    # ------------------------------------------------------------------
    def first_run_setup(self):
        """Pop up a dialog to set initial balance."""
        self.root.withdraw()
        dialog = tk.Toplevel()
        dialog.title("Welcome")
        tk.Label(dialog, text="No data found. Enter initial balance:").pack(padx=10, pady=5)
        entry = tk.Entry(dialog)
        entry.insert(0, str(DEFAULT_BALANCE))
        entry.pack(padx=10, pady=5)
        entry.focus()

        def on_ok():
            try:
                bal = float(entry.get())
                if bal <= 0:
                    messagebox.showerror("Error", "Balance must be positive.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid number.")
                return
            dialog.destroy()
            self.data = init_new_data(bal)
            self.root.deiconify()
            self.build_ui()

        tk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.root.quit())
        dialog.grab_set()
        self.root.wait_window(dialog)
        if self.data is None:
            self.root.quit()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def build_ui(self):
        """Construct the main interface."""
        self.balance_var = tk.StringVar()
        self.totalR_var = tk.StringVar()
        self.target_var = tk.StringVar(value="Not set")
        self.Rneeded_var = tk.StringVar(value="—")

        frame_dash = ttk.LabelFrame(self.root, text="Dashboard", padding=10)
        frame_dash.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_dash, text="Balance:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(frame_dash, textvariable=self.balance_var, font=("", 12, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Label(frame_dash, text="Total R:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(frame_dash, textvariable=self.totalR_var).grid(row=1, column=1, sticky="w")
        ttk.Label(frame_dash, text="Target:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(frame_dash, textvariable=self.target_var).grid(row=2, column=1, sticky="w")
        ttk.Label(frame_dash, text="R to goal:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(frame_dash, textvariable=self.Rneeded_var).grid(row=3, column=1, sticky="w")

        self.refresh_dashboard()

        frame_actions = ttk.Frame(self.root, padding=10)
        frame_actions.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame_actions, text="Log New Trade", command=self.log_trade).pack(fill="x", pady=2)
        ttk.Button(frame_actions, text="Set / Change Target", command=self.set_target).pack(fill="x", pady=2)
        ttk.Button(frame_actions, text="View Trade History", command=self.view_history).pack(fill="x", pady=2)
        ttk.Button(frame_actions, text="Exit", command=self.root.quit).pack(fill="x", pady=5)

    def refresh_dashboard(self):
        """Update the dashboard labels."""
        bal = self.data["balance"]
        self.balance_var.set(f"${bal:,.2f}")
        self.totalR_var.set(str(self.data["total_R"]))
        target = self.data.get("target")
        if target:
            self.target_var.set(f"${target:,.2f}")
            if bal >= target:
                self.Rneeded_var.set("Goal reached! 🎉")
            elif bal <= 0:
                self.Rneeded_var.set("Liquidated 💀")
            else:
                R_needed = math.ceil(math.log(target / bal) / math.log(1 + RISK_PERCENT))
                self.Rneeded_var.set(str(R_needed))
        else:
            self.target_var.set("Not set")
            self.Rneeded_var.set("—")

    # ------------------------------------------------------------------
    # Trade logging
    # ------------------------------------------------------------------
    def log_trade(self):
        """Open a dialog to log a trade."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Log New Trade")
        dialog.resizable(False, False)
        tk.Label(dialog, text="Trade P/L as percentage (e.g. +12 or -8):").pack(padx=10, pady=5)
        entry = tk.Entry(dialog)
        entry.pack(padx=10, pady=5)
        entry.focus()

        def submit():
            raw = entry.get().strip()
            try:
                pct = float(raw)
            except ValueError:
                messagebox.showerror("Invalid Input", "Enter a number like +12 or -8.", parent=dialog)
                return

            raw_R = pct / (RISK_PERCENT * 100)
            rounded_R = int(round(raw_R))

            old_balance = self.data["balance"]
            initial = self.data.get("initial_balance", old_balance)

            # ---- OVERFLOW GUARD ----
            if abs(rounded_R) > MAX_R:
                messagebox.showerror(
                    "Input Too Large",
                    f"The R value ({rounded_R}R) is too large to compute.\n"
                    f"Maximum allowed is {MAX_R}R.",
                    parent=dialog
                )
                return

            # ---- COMPOUNDING MATH ----
            try:
                if rounded_R >= 0:
                    new_balance = old_balance * ((1 + RISK_PERCENT) ** rounded_R)
                else:
                    new_balance = old_balance * ((1 - RISK_PERCENT) ** abs(rounded_R))
            except OverflowError:
                messagebox.showerror(
                    "Number Too Large",
                    "The result is too large to compute.\n"
                    "Try a smaller percentage.",
                    parent=dialog
                )
                return
            # --------------------------

            # ---- LIQUIDATION CHECK: below 1% of initial ----
            liquidated = False
            if new_balance < LIQUIDATION_THRESHOLD * initial:
                new_balance = 0
                liquidated = True
            # -----------------------------------------------

            self.data["balance"] = new_balance
            self.data["total_R"] += rounded_R

            trade = {
                "timestamp": datetime.now().isoformat(),
                "percentage": pct,
                "rounded_R": rounded_R,
                "balance_after": new_balance
            }
            self.data["trades"].append(trade)
            save_data(self.data)

            self.refresh_dashboard()
            dialog.destroy()

            if liquidated:
                self.handle_liquidation()
            else:
                messagebox.showinfo(
                    "Trade Logged",
                    f"{pct}% → {rounded_R}R\nNew balance: ${new_balance:,.2f}"
                )

        ttk.Button(dialog, text="Submit", command=submit).pack(pady=5)
        dialog.grab_set()
        self.root.wait_window(dialog)

    # ------------------------------------------------------------------
    # Liquidation handling
    # ------------------------------------------------------------------
    def handle_liquidation(self):
        """Ask user what to do after liquidation."""
        choice_win = tk.Toplevel(self.root)
        choice_win.title("You Got Liquidated 💀")
        choice_win.resizable(False, False)
        choice_win.grab_set()

        msg = (
            "You got liquidated.\n\n"
            "Your balance has hit zero.\n\n"
            "What do you want to do?"
        )
        tk.Label(choice_win, text=msg, justify="center", padx=20, pady=15).pack()

        btn_frame = ttk.Frame(choice_win, padding=10)
        btn_frame.pack(fill="x")

        def start_over():
            choice_win.destroy()
            self.reset_all_data()

        def add_balance():
            choice_win.destroy()
            self.add_new_balance()

        ttk.Button(btn_frame, text="Start Over (delete all data)", command=start_over).pack(fill="x", pady=3)
        ttk.Button(btn_frame, text="Add New Balance (keep history)", command=add_balance).pack(fill="x", pady=3)

        choice_win.protocol("WM_DELETE_WINDOW", lambda: None)  # force a choice
        self.root.wait_window(choice_win)

    def reset_all_data(self):
        """Delete all data and ask for new balance."""
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        self.data = None

        dialog = tk.Toplevel(self.root)
        dialog.title("Start Over")
        tk.Label(dialog, text="Enter new starting balance:").pack(padx=10, pady=5)
        entry = tk.Entry(dialog)
        entry.insert(0, str(DEFAULT_BALANCE))
        entry.pack(padx=10, pady=5)
        entry.focus()

        def on_ok():
            try:
                bal = float(entry.get())
                if bal <= 0:
                    messagebox.showerror("Error", "Balance must be positive.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid number.")
                return
            dialog.destroy()
            self.data = init_new_data(bal)
            self.refresh_dashboard()
            messagebox.showinfo("Fresh Start", f"New balance: ${bal:,.2f}")

        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def add_new_balance(self):
        """Add a new balance on top of existing data, keep history."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Balance")
        tk.Label(dialog, text="Enter new balance to continue:").pack(padx=10, pady=5)
        entry = tk.Entry(dialog)
        entry.insert(0, str(DEFAULT_BALANCE))
        entry.pack(padx=10, pady=5)
        entry.focus()

        def on_ok():
            try:
                bal = float(entry.get())
                if bal <= 0:
                    messagebox.showerror("Error", "Balance must be positive.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid number.")
                return
            dialog.destroy()
            self.data["balance"] = bal
            self.data["initial_balance"] = bal  # reset the 1% baseline
            save_data(self.data)
            self.refresh_dashboard()
            messagebox.showinfo("Balance Added", f"New balance: ${bal:,.2f}\nHistory kept.")

        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        dialog.grab_set()
        self.root.wait_window(dialog)

    # ------------------------------------------------------------------
    # Target
    # ------------------------------------------------------------------
    def set_target(self):
        """Open a dialog to set a financial target."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Target")
        dialog.resizable(False, False)
        tk.Label(dialog, text="Target dollar amount (must exceed current balance):").pack(padx=10, pady=5)
        entry = tk.Entry(dialog)
        entry.pack(padx=10, pady=5)
        entry.focus()

        def submit():
            raw = entry.get().strip()
            try:
                target = float(raw)
            except ValueError:
                messagebox.showerror("Invalid Input", "Enter a valid number.", parent=dialog)
                return
            if self.data["balance"] <= 0:
                messagebox.showerror("Error", "Balance is zero. Can't set target.", parent=dialog)
                return
            if target <= self.data["balance"]:
                messagebox.showerror("Error", "Target must be greater than current balance.", parent=dialog)
                return

            self.data["target"] = target
            save_data(self.data)
            self.refresh_dashboard()
            dialog.destroy()
            R_needed = math.ceil(math.log(target / self.data["balance"]) / math.log(1 + RISK_PERCENT))
            messagebox.showinfo("Target Set", f"Target: ${target:,.2f}\nR needed: {R_needed}")

        ttk.Button(dialog, text="Submit", command=submit).pack(pady=5)
        dialog.grab_set()
        self.root.wait_window(dialog)

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------
    def view_history(self):
        """Show a window with the trade history table."""
        trades = self.data["trades"]
        if not trades:
            messagebox.showinfo("Trade History", "No trades recorded yet.")
            return

        hist_win = tk.Toplevel(self.root)
        hist_win.title("Trade History")
        hist_win.geometry("550x300")
        columns = ("date", "pl", "R", "balance")
        tree = ttk.Treeview(hist_win, columns=columns, show="headings")
        tree.heading("date", text="Date")
        tree.heading("pl", text="P/L %")
        tree.heading("R", text="R")
        tree.heading("balance", text="Balance After")
        tree.column("date", width=150)
        tree.column("pl", width=80, anchor="center")
        tree.column("R", width=50, anchor="center")
        tree.column("balance", width=120, anchor="e")

        for t in trades:
            ts = t["timestamp"][:19].replace("T", " ")
            pl = f"{t['percentage']:+.2f}%"
            R = t["rounded_R"]
            bal = f"${t['balance_after']:,.2f}"
            tree.insert("", "end", values=(ts, pl, R, bal))

        tree.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Button(hist_win, text="Close", command=hist_win.destroy).pack(pady=5)

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = IronmindApp(root)
    root.mainloop()
