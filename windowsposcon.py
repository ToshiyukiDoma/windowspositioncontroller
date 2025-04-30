import tkinter as tk
from tkinter import ttk
import win32gui
import win32con
import win32api

class MovableResizableWindowGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Window Position/Size Controller")

        self.target_title = tk.StringVar()
        self.hwnd = None
        self.aspect_ratio = None

        self.window_list = self.get_visible_window_titles()
        self.target_title.set(self.window_list[0] if self.window_list else "")

        # Window Selection
        ttk.Label(root, text="Select Application:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.window_combo = ttk.Combobox(root, textvariable=self.target_title, values=self.window_list)
        self.window_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.select_button = ttk.Button(root, text="Connect", command=self.connect_to_window)
        self.select_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        # Position Control
        ttk.Label(root, text="Position (X):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.x_slider = tk.Scale(root, from_=-2000, to=2000, orient=tk.HORIZONTAL, label="X", command=self.update_x_position)
        self.x_slider.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Label(root, text="Position (Y):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.y_slider = tk.Scale(root, from_=-2000, to=2000, orient=tk.HORIZONTAL, label="Y", command=self.update_y_position)
        self.y_slider.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Aspect Ratio Control
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        self.maintain_aspect_check = ttk.Checkbutton(root, text="Maintain Aspect Ratio", variable=self.maintain_aspect_var)
        self.maintain_aspect_check.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        ttk.Label(root, text="Current Aspect Ratio:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.aspect_ratio_label = ttk.Label(root, text="N/A")
        self.aspect_ratio_label.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        ttk.Label(root, text="Size (Height):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.height_entry = ttk.Entry(root)
        self.height_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.set_height_button = ttk.Button(root, text="Set Height", command=self.set_window_height)
        self.set_height_button.grid(row=5, column=2, padx=5, pady=5, sticky="e")

        ttk.Label(root, text="Size (Width):").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.width_entry = ttk.Entry(root, state=tk.DISABLED) # Initially disabled, updated based on aspect ratio
        self.width_entry.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        self.set_width_button = ttk.Button(root, text="Set Width", command=self.set_window_width)
        self.set_width_button.grid(row=6, column=2, padx=5, pady=5, sticky="e")

        self.connect_button = ttk.Button(root, text="Apply Settings", command=self.apply_settings, state=tk.DISABLED)
        self.connect_button.grid(row=7, column=0, columnspan=3, padx=5, pady=10)

        self.root.columnconfigure(1, weight=1)

    def is_visible_window(self, hwnd):
        """Checks if a window is visible and has a title."""
        if not win32gui.IsWindowVisible(hwnd):
            return False
        if not win32gui.GetWindowText(hwnd):
            return False
        # Exclude windows that are likely system or background elements
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if ex_style & win32con.WS_EX_TOOLWINDOW:
            return False
        if not win32gui.GetWindowRect(hwnd)[2] > win32gui.GetWindowRect(hwnd)[0] or not win32gui.GetWindowRect(hwnd)[3] > win32gui.GetWindowRect(hwnd)[1]:
            return False
        return True

    def get_visible_window_titles(self):
        titles = []
        def enum_windows_proc(hwnd, lParam):
            if self.is_visible_window(hwnd):
                titles.append(win32gui.GetWindowText(hwnd))
            return True
        win32gui.EnumWindows(enum_windows_proc, None)
        return sorted(list(set(titles))) # Use set to remove duplicates

    def connect_to_window(self):
        title = self.target_title.get()
        self.hwnd = win32gui.FindWindow(None, title)
        if self.hwnd:
            rect = win32gui.GetWindowRect(self.hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            if height > 0:
                self.aspect_ratio = width / height
                self.aspect_ratio_label.config(text=f"{self.aspect_ratio:.2f}")
            else:
                self.aspect_ratio = None
                self.aspect_ratio_label.config(text="N/A")

            self.x_slider.config(to=self.root.winfo_screenwidth(), from_=-self.root.winfo_screenwidth())
            self.y_slider.config(to=self.root.winfo_screenheight(), from_=-self.root.winfo_screenheight())
            self.x_slider.set(rect[0])
            self.y_slider.set(rect[1])
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(height))
            self.width_entry.config(state=tk.NORMAL)
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(width))
            self.width_entry.config(state=tk.DISABLED) # Initially controlled by aspect ratio

            self.connect_button.config(state=tk.NORMAL)
        else:
            self.aspect_ratio = None
            self.aspect_ratio_label.config(text="N/A")
            self.connect_button.config(state=tk.DISABLED)
            self.height_entry.delete(0, tk.END)
            self.width_entry.config(state=tk.NORMAL)
            self.width_entry.delete(0, tk.END)
            self.width_entry.config(state=tk.DISABLED)
            tk.messagebox.showerror("Error", f"Window with title '{title}' not found.")

    def update_x_position(self, value):
        if self.hwnd:
            rect = win32gui.GetWindowRect(self.hwnd)
            win32gui.MoveWindow(self.hwnd, int(value), rect[1], rect[2] - rect[0], rect[3] - rect[1], True)

    def update_y_position(self, value):
        if self.hwnd:
            rect = win32gui.GetWindowRect(self.hwnd)
            win32gui.MoveWindow(self.hwnd, rect[0], int(value), rect[2] - rect[0], rect[3] - rect[1], True)

    def set_window_height(self):
        if self.hwnd and self.aspect_ratio and self.maintain_aspect_var.get():
            try:
                height = int(self.height_entry.get())
                width = int(height * self.aspect_ratio)
                rect = win32gui.GetWindowRect(self.hwnd)
                win32gui.MoveWindow(self.hwnd, rect[0], rect[1], width, height, True)
                self.width_entry.config(state=tk.NORMAL)
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(width))
                self.width_entry.config(state=tk.DISABLED)
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid height value.")
        elif self.hwnd:
            try:
                height = int(self.height_entry.get())
                rect = win32gui.GetWindowRect(self.hwnd)
                win32gui.MoveWindow(self.hwnd, rect[0], rect[1], rect[2] - rect[0], height, True)
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid height value.")

    def set_window_width(self):
        if self.hwnd and self.aspect_ratio and self.maintain_aspect_var.get():
            try:
                width = int(self.width_entry.get())
                height = int(width / self.aspect_ratio)
                rect = win32gui.GetWindowRect(self.hwnd)
                win32gui.MoveWindow(self.hwnd, rect[0], rect[1], width, height, True)
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(height))
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid width value.")
        elif self.hwnd:
            try:
                width = int(self.width_entry.get())
                rect = win32gui.GetWindowRect(self.hwnd)
                win32gui.MoveWindow(self.hwnd, rect[0], rect[1], width, rect[3] - rect[1], True)
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid width value.")

    def apply_settings(self):
        if self.hwnd:
            try:
                x = self.x_slider.get()
                y = self.y_slider.get()
                height = int(self.height_entry.get())
                width = int(self.width_entry.get()) if not self.maintain_aspect_var.get() else int(height * self.aspect_ratio)

                win32gui.MoveWindow(self.hwnd, x, y, width, height, True)
                if self.maintain_aspect_var.get():
                    self.width_entry.config(state=tk.NORMAL)
                    self.width_entry.delete(0, tk.END)
                    self.width_entry.insert(0, str(width))
                    self.width_entry.config(state=tk.DISABLED)
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid position or size value.")
        else:
            tk.messagebox.showerror("Error", "No window connected.")

def main():
    root = tk.Tk()
    app = MovableResizableWindowGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()