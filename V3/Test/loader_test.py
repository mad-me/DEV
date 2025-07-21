import tkinter as tk
from tkinter import Label
import tkinter.font as tkFont
import os
from time import sleep
import threading
import ctypes
from ctypes import windll

class LoaderWidget(tk.Frame):
    def __init__(self, parent, show_terminal=False, **kwargs):
        super().__init__(parent, **kwargs)
        self.show_terminal = show_terminal
        self._register_ubuntu_font()
        self.config(bg="black")
        self.parent = parent
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        # Ubuntu-Schriftart verwenden (falls verfügbar)
        try:
            available_fonts = list(tkFont.families())
            ubuntu_variants = ["Ubuntu", "Ubuntu Light", "Ubuntu Medium", "Ubuntu Condensed", "Segoe UI", "Arial", "Helvetica"]
            self.font_family = "Arial"
            for font in ubuntu_variants:
                if font in available_fonts:
                    self.font_family = font
                    break
        except Exception as e:
            print("Fehler beim Laden der Schriftart:", e)
            self.font_family = "Arial"

        self.num_blocks = 16
        self.block_width = 22
        self.block_height = 20
        self.block_spacing = 8
        self.total_width = self.num_blocks * self.block_width + (self.num_blocks - 1) * self.block_spacing
        self.start_x = (self.screen_width - self.total_width) // 2
        self.text_y = self.screen_height // 2 - 40
        self.blocks_y = self.screen_height // 2 + 10

        self.text_label = Label(self, text="Loading...", font=(self.font_family, 15), bg="black", fg="#FFBD09")
        self.text_label.place(x=self.screen_width//2, y=self.text_y, anchor="center")

        self.blocks = []
        for i in range(self.num_blocks):
            block = Label(self, bg="#1F2732", width=2, height=1)
            x = self.start_x + i * (self.block_width + self.block_spacing)
            block.place(x=x, y=self.blocks_y)
            self.blocks.append(block)

        self.ok_label = Label(
            self, text="OK", font=(self.font_family, 18, "bold"),
            fg="#FFBD09", bg="black", cursor="hand2"
        )
        self.ok_label.place(x=self.screen_width//2, y=self.blocks_y+60, anchor="center")
        self.ok_label.place_forget()
        self.ok_label.bind("<Enter>", self.on_ok_hover)
        self.ok_label.bind("<Leave>", self.on_ok_leave)
        self.ok_label.bind("<Button-1>", lambda e: self._on_ok())

        # Optionales Terminalfenster (jetzt nach den Loader-Parametern!)
        if self.show_terminal:
            bahn_font = "Terminal"
            available_fonts = list(tkFont.families())
            if bahn_font not in available_fonts:
                bahn_font = "Arial"
            terminal_width = 700
            terminal_height = 600
            loader_right = self.start_x + self.total_width
            terminal_left = loader_right + ((self.screen_width - loader_right - terminal_width) // 2)
            terminal_top = (self.screen_height - terminal_height) // 2
            self.terminal_frame = tk.Frame(self, bg="#181818", highlightthickness=2, highlightbackground="#444")
            self.terminal_frame.place(x=terminal_left, y=terminal_top, width=terminal_width, height=terminal_height)
            self.close_btn = tk.Button(self.terminal_frame, text="✕", font=(bahn_font, 12, "bold"), fg="#FFBD09", bg="#181818", bd=0, activebackground="#333", activeforeground="#f7931e", command=self.terminal_frame.destroy, cursor="hand2")
            self.close_btn.place(relx=1.0, x=-8, y=8, anchor="ne", width=28, height=28)
            self._drag_data = None
            def start_move(event):
                self._drag_data = (event.x, event.y)
            def do_move(event):
                if self._drag_data and self.terminal_frame is not None:
                    dx = event.x - self._drag_data[0]
                    dy = event.y - self._drag_data[1]
                    x = self.terminal_frame.winfo_x() + dx
                    y = self.terminal_frame.winfo_y() + dy
                    self.terminal_frame.place(x=x, y=y)
            self.terminal_frame.bind("<Button-1>", start_move)
            self.terminal_frame.bind("<B1-Motion>", do_move)
            self.terminal_text = tk.Text(self.terminal_frame, bg="#181818", fg="#FFBD09", insertbackground="#FFBD09", font=(bahn_font, 12), wrap="word")
            self.terminal_text.pack(fill="both", expand=True, padx=8, pady=(40,0))
            self.terminal_text.insert("end", "[Terminal bereit]\n")
            self.terminal_text.config(state="disabled")
            self.terminal_entry = tk.Entry(self.terminal_frame, bg="#222", fg="#FFBD09", font=(bahn_font, 12), insertbackground="#FFBD09")
            self.terminal_entry.pack(fill="x", side="bottom", padx=8, pady=8)
            self.terminal_entry.bind("<Return>", self._on_terminal_input)
        else:
            self.terminal_frame = None
            self.terminal_text = None
            self.terminal_entry = None

        self.anim_thread = threading.Thread(target=self.play_animation, daemon=True)
        self.anim_thread.start()

    def on_ok_hover(self, event):
        self.ok_label.config(fg="#f7931e", font=(self.font_family, 22, "bold"))

    def on_ok_leave(self, event):
        self.ok_label.config(fg="#FFBD09", font=(self.font_family, 18, "bold"))

    def play_animation(self):
        import time
        start = time.time()
        while True:
            for j in range(self.num_blocks):
                self.blocks[j].config(bg="#FFBD09")
                self.update_idletasks()
                sleep(0.06)
                self.blocks[j].config(bg="#1F2732")
            if time.time() - start > 4:
                break
        self.text_label.config(text="Import abgeschlossen!")
        self.ok_label.place(x=self.screen_width//2, y=self.blocks_y+60, anchor="center")

    def print_terminal(self, text):
        if self.terminal_text is not None:
            self.terminal_text.config(state="normal")
            self.terminal_text.insert("end", text + "\n")
            self.terminal_text.see("end")
            self.terminal_text.config(state="disabled")

    def _on_terminal_input(self, event):
        if self.terminal_entry is not None and self.terminal_text is not None and self.terminal_frame is not None:
            cmd = self.terminal_entry.get().strip()
            if cmd:
                self.print_terminal(f"> {cmd}")
                if cmd.lower() == "help":
                    self.print_terminal("Verfügbare Befehle: help, clear, exit")
                elif cmd.lower() == "clear":
                    self.terminal_text.config(state="normal")
                    self.terminal_text.delete("1.0", "end")
                    self.terminal_text.config(state="disabled")
                elif cmd.lower() == "exit":
                    self.print_terminal("Terminal wird geschlossen...")
                    self.terminal_frame.destroy()
                else:
                    self.print_terminal(f"Unbekannter Befehl: {cmd}")
            self.terminal_entry.delete(0, "end")

    def _on_ok(self):
        # Wenn als Standalone-Fenster, schließe das Fenster
        if isinstance(self.parent, tk.Tk):
            self.parent.destroy()
        else:
            self.ok_label.place_forget()

    def _register_ubuntu_font(self):
        try:
            font_path = os.path.join(os.path.dirname(__file__), "Style", "assets", "fonts", "Ubuntu-Regular.ttf")
            if os.path.exists(font_path):
                windll.gdi32.AddFontResourceW(font_path)
                print(f"Ubuntu-Schriftart registriert: {font_path}")
            else:
                print(f"Ubuntu-Schriftart nicht gefunden: {font_path}")
        except Exception as e:
            print(f"Fehler beim Registrieren der Ubuntu-Schriftart: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.config(bg="black")
    root.attributes("-fullscreen", True)
    loader = LoaderWidget(root, show_terminal=True)
    loader.pack(fill="both", expand=True)
    root.mainloop() 