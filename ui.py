"""
Macro AutoCraft – GUI Application
Pure UI layer: delegates all logic to autocraft and jsonHandler.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

import autocraft
import jsonHandler
from autocraft import startCrafting, WAIT_TIME
from jsonHandler import addNewMacro, importData, removeMacro
from models import UserMacro
from exceptions import *


class MacroCraftApp:
    """Main application window for Macro AutoCraft."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Macro AutoCraft")
        self.root.geometry("850x600")
        self.root.minsize(750, 500)

        self.is_crafting = False
        self.selected_difficulty = None

        # Load data from JSON via jsonHandler
        importData()

        self._build_top_bar()
        self._build_macro_list()
        self._build_add_form()
        self._refresh_macro_list()

    # ── UI construction ───────────────────────────────────────────────

    def _build_top_bar(self):
        """Top bar: iterations, progress bar, start button."""
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill=tk.X)

        # Number of crafting iterations
        ttk.Label(top, text="Iterations:").pack(side=tk.LEFT)
        self.iterations_var = tk.StringVar(value="1")
        vcmd_iter = (self.root.register(
            lambda P: len(P) <= 3 and (P == "" or P.isdigit())
        ), "%P")
        ttk.Entry(top, textvariable=self.iterations_var, width=6,
                  validate="key", validatecommand=vcmd_iter).pack(
            side=tk.LEFT, padx=(5, 15)
        )

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            top, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Status label
        self.progress_label = ttk.Label(top, text="Idle")
        self.progress_label.pack(side=tk.LEFT, padx=(0, 10))

        # Stop button — hard stops crafting immediately
        self.stop_btn = ttk.Button(
            top, text="Stop", command=self._stop_crafting, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.RIGHT, padx=(0, 5))

        # Pause/Resume — single button, text and command swap
        self.pause_btn = ttk.Button(
            top, text="Pause", command=self._pause_crafting, state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.RIGHT, padx=(0, 5))

        # Start button (disabled until a macro set is selected from the list)
        self.start_btn = ttk.Button(
            top, text="Start Crafting", command=self._start_crafting, state=tk.DISABLED
        )
        self.start_btn.pack(side=tk.RIGHT)

        # Secondary status label below the top bar for "waiting" messages
        self.secondary_label = ttk.Label(self.root, text="", anchor=tk.E)
        self.secondary_label.pack(fill=tk.X, padx=15)

    def _build_macro_list(self):
        """Center section: treeview listing all macro sets from MACRO_DICT."""
        center = ttk.LabelFrame(self.root, text="Macro Sets", padding=10)
        center.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("difficulty", "macros")
        self.tree = ttk.Treeview(
            center, columns=columns, show="headings", selectmode="browse"
        )
        self.tree.heading("difficulty", text="Difficulty")
        self.tree.heading("macros", text="Macros")
        self.tree.column("difficulty", width=120, anchor=tk.CENTER)
        self.tree.column("macros", width=500)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(center, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Selecting a row sets the difficulty for crafting
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Delete button below the list
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10)
        self.delete_btn = ttk.Button(
            btn_frame, text="Delete Selected",
            command=self._delete_selected, state=tk.DISABLED,
        )
        self.delete_btn.pack(side=tk.RIGHT, pady=5)

    def _refresh_macro_list(self):
        """Repopulate the treeview from MACRO_DICT."""
        self.tree.delete(*self.tree.get_children())
        for macro_set in jsonHandler.MACRO_DICT.macroDictionary:
            summary = ", ".join(
                f"key:{m.keybind} ({m.duration}s)" for m in macro_set.macros
            )
            self.tree.insert("", tk.END, values=(macro_set.difficulty, summary))

        # Reset selection
        self.selected_difficulty = None
        self.start_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)

    def _on_select(self, _event):
        """When a macro set is selected, store its difficulty and enable buttons."""
        selection = self.tree.selection()
        if selection:
            self.selected_difficulty = str(self.tree.item(selection[0])["values"][0])
            if not self.is_crafting:
                self.start_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.selected_difficulty = None
            self.start_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

    def _delete_selected(self):
        """Delete the selected macro set via jsonHandler.removeMacro."""
        if not self.selected_difficulty:
            return
        if not messagebox.askyesno(
            "Confirm", f"Delete macro set '{self.selected_difficulty}'?"
        ):
            return
        removeMacro(self.selected_difficulty)
        self._refresh_macro_list()

    # ── Add Macro Set form ────────────────────────────────────────────

    def _build_add_form(self):
        """Bottom section: form to create a new macro set."""
        add_frame = ttk.LabelFrame(self.root, text="Add New Macro Set", padding=10)
        add_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        # Header: difficulty input + action buttons
        header = ttk.Frame(add_frame)
        header.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(header, text="Difficulty:").pack(side=tk.LEFT)
        self.difficulty_var = tk.StringVar()
        ttk.Entry(header, textvariable=self.difficulty_var, width=15).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            header, text="+ Add Macro", command=self._add_macro_row
        ).pack(side=tk.RIGHT, padx=5)
        ttk.Button(
            header, text="Save Macro Set", command=self._save_macro_set
        ).pack(side=tk.RIGHT)

        # Container for dynamic macro rows
        self.macro_rows_frame = ttk.Frame(add_frame)
        self.macro_rows_frame.pack(fill=tk.X)

        # Each entry: (keybind_var, text_widget, row_frame)
        self.macro_rows: list[tuple] = []
        self._add_macro_row()

    MAX_MACROS = 3

    def _add_macro_row(self):
        """Append a keybind + content row to the form (max 3)."""
        if len(self.macro_rows) >= self.MAX_MACROS:
            return

        row = ttk.Frame(self.macro_rows_frame)
        row.pack(fill=tk.X, pady=2)

        # Label is set by _renumber_macro_rows
        label = ttk.Label(row)
        label.pack(side=tk.LEFT)

        ttk.Label(row, text="Key:").pack(side=tk.LEFT, padx=(10, 2))
        keybind_var = tk.StringVar()
        vcmd_key = (self.root.register(
            lambda P: len(P) <= 1
        ), "%P")
        ttk.Entry(row, textvariable=keybind_var, width=5,
                  validate="key", validatecommand=vcmd_key).pack(side=tk.LEFT)

        ttk.Label(row, text="Content:").pack(side=tk.LEFT, padx=(10, 2))
        text_widget = scrolledtext.ScrolledText(row, height=3, width=40)
        text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        remove_btn = ttk.Button(
            row, text="X", width=3,
            command=lambda f=row: self._remove_macro_row(f),
        )
        remove_btn.pack(side=tk.RIGHT)

        self.macro_rows.append((keybind_var, text_widget, row, label))
        self._renumber_macro_rows()

    def _remove_macro_row(self, frame: ttk.Frame):
        """Remove a macro row (keeps at least one)."""
        if len(self.macro_rows) <= 1:
            return
        self.macro_rows = [(k, t, f, l) for k, t, f, l in self.macro_rows if f != frame]
        frame.destroy()
        self._renumber_macro_rows()

    def _renumber_macro_rows(self):
        """Update macro labels to reflect current position."""
        for i, (_, _, _, label) in enumerate(self.macro_rows):
            label.config(text=f"Macro {i + 1}:")

    def _save_macro_set(self):
        """Validate form inputs and pass UserMacro list to addNewMacro."""
        difficulty = self.difficulty_var.get().strip()
        if not difficulty:
            messagebox.showwarning("Validation", "Please enter a difficulty value.")
            return

        user_macros: list[UserMacro] = []
        seen_keybinds: set[str] = set()
        for keybind_var, text_widget, _, _ in self.macro_rows:
            keybind = keybind_var.get().strip()
            content = text_widget.get("1.0", tk.END).strip()
            if not keybind or not content:
                messagebox.showwarning(
                    "Validation", "Each macro needs a keybind and content."
                )
                return
            if keybind in seen_keybinds:
                messagebox.showwarning(
                    "Validation", f"Duplicate keybind '{keybind}'. Each macro must have a unique keybind."
                )
                return
            seen_keybinds.add(keybind)
            user_macro = UserMacro()
            user_macro.keybind = keybind
            user_macro.content = content
            user_macros.append(user_macro)

        # Delegate to jsonHandler — all extraction/saving happens there
        try:
            addNewMacro(difficulty, user_macros)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Clear form and refresh list
        self.difficulty_var.set("")
        for _, _, frame, _ in self.macro_rows:
            frame.destroy()
        self.macro_rows.clear()
        self._add_macro_row()
        self._refresh_macro_list()
        messagebox.showinfo("Success", f"Macro set '{difficulty}' added!")

    # ── Crafting ──────────────────────────────────────────────────────

    def _start_crafting(self):
        """Validate inputs, call startCrafting in a thread, and poll progress."""
        if not self.selected_difficulty:
            messagebox.showwarning("Validation", "Please select a macro set.")
            return

        try:
            iterations = int(self.iterations_var.get())
            if iterations <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Iterations must be a positive integer.")
            return

        # Reset events before starting
        autocraft.clearEvents()
        autocraft.stop_event.clear()

        # Lock UI and enable crafting controls
        self.is_crafting = True
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)

        thread = threading.Thread(
            target=self._crafting_thread,
            args=(self.selected_difficulty, iterations),
            daemon=True,
        )
        thread.start()

        # Show countdown, then start polling progress
        self._countdown(WAIT_TIME, iterations)

    def _pause_crafting(self):
        """Request pause — disables both pause and stop until actually paused."""
        autocraft.pause_event.set()
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)

    def _resume_crafting(self):
        """Resume crafting from paused state."""
        autocraft.resume_event.set()
        self.pause_btn.config(text="Pause", command=self._pause_crafting, state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.secondary_label.config(text="")

    def _stop_crafting(self):
        """Hard stop crafting immediately."""
        autocraft.stop_event.set()
        # If paused, unblock the thread so it can exit
        autocraft.resume_event.set()
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)

    def _countdown(self, remaining: int, iterations: int):
        """Display a countdown in the status label, then start polling progress."""
        if remaining <= 0 or not self.is_crafting:
            self._poll_progress(iterations)
            return
        self.progress_label.config(text=f"Starting in {remaining}s...")
        self.root.after(1000, lambda: self._countdown(remaining - 1, iterations))

    def _crafting_thread(self, difficulty: str, iterations: int):
        """Wrapper that calls startCrafting on a background thread."""
        try:
            startCrafting(difficulty, iterations)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Crafting Error", str(e)))
        finally:
            self.root.after(0, self._crafting_finished)

    def _poll_progress(self, iterations: int):
        """Periodically read autocraft.progress and update the UI."""
        if not self.is_crafting:
            return

        # Read live progress from the autocraft module
        current = autocraft.progress
        pct = (current / iterations) * 100 if iterations > 0 else 0
        self.progress_var.set(pct)

        if not autocraft.crafting and autocraft.pause_event.is_set():
            # Actually paused — swap to Resume button
            self.progress_label.config(text=f"Paused at {current}/{iterations}")
            self.secondary_label.config(text="")
            self.pause_btn.config(text="Resume", command=self._resume_crafting, state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
        elif autocraft.pause_event.is_set() and autocraft.crafting:
            # Pause requested but still finishing current iteration
            self.progress_label.config(text=f"Crafting {current}/{iterations}")
            self.secondary_label.config(text="Waiting for this iteration to finish...")
        else:
            self.progress_label.config(text=f"Crafting {current}/{iterations}")
            self.secondary_label.config(text="")

        # Poll again in 500ms
        self.root.after(500, lambda: self._poll_progress(iterations))

    def _crafting_finished(self):
        """Reset UI state after crafting completes."""
        self.is_crafting = False
        self.progress_var.set(100)
        self.progress_label.config(text="Done!")
        self.secondary_label.config(text="")
        self.pause_btn.config(text="Pause", command=self._pause_crafting, state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        if self.selected_difficulty:
            self.start_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    MacroCraftApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
