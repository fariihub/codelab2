import tkinter as tk
from tkinter import messagebox
import random

def load_jokes():
    try:
        with open("randomJokes.txt", "r", encoding="utf-8") as file:
            jokes = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        messagebox.showerror("File Missing", "randomJokes.txt not found!")
        return []
    except Exception as e:
        messagebox.showerror("Error", f"Unable to read file:\n{e}")
        return []

    valid_jokes = []
    for joke in jokes:
        if "?" in joke:
            valid_jokes.append(joke)
        else:
            valid_jokes.append(joke + "?Oops! Punchline missing.")

    return valid_jokes

class JokeApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Alexa Joke Assistant – Premium Edition")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.jokes = load_jokes()
        self.current_setup = ""
        self.current_punchline = ""
        self.animation_id = None

        self.canvas = tk.Canvas(root, width=600, height=500, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_gradient("#0A0F24", "#20295B")

        self.build_ui()

    def draw_gradient(self, color1, color2):
        """
        Beautiful vertical gradient background.
        """
        for i in range(500):
            r1, g1, b1 = self.hex_to_rgb(color1)
            r2, g2, b2 = self.hex_to_rgb(color2)
            r = int(r1 + (r2 - r1) * i / 500)
            g = int(g1 + (g2 - g1) * i / 500)
            b = int(b1 + (b2 - b1) * i / 500)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, 600, i, fill=color)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def build_ui(self):
        # Alexa Avatar
        self.avatar = tk.Label(
            self.root,
            text="🤖",
            font=("Arial", 60),
            bg="#0A0F24",
            fg="white"
        )
        self.avatar.place(x=260, y=20)

        self.setup_label = tk.Label(
            self.root,
            text="Press the button to hear a joke!",
            font=("Arial", 16, "bold"),
            bg="#0A0F24",
            fg="white",
            wraplength=550,
            justify="center"
        )
        self.setup_label.place(x=30, y=140)
        
        self.punchline_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14, "italic"),
            bg="#0A0F24",
            fg="#FFE66D",
            wraplength=550,
            justify="center"
        )
        self.punchline_label.place(x=30, y=220)

        self.tell_btn = tk.Button(
            self.root,
            text="Alexa tell me a Joke",
            command=self.new_joke,
            width=25,
            font=("Arial", 12, "bold"),
            bg="#FFE66D",
            fg="black",
            activebackground="#FFE66D"
        )
        self.tell_btn.place(x=200, y=300)

        self.show_btn = tk.Button(
            self.root,
            text="Show Punchline",
            command=self.show_punchline,
            width=20,
            font=("Arial", 12),
            bg="#3949AB",
            fg="white",
            state=tk.DISABLED
        )
        self.show_btn.place(x=220, y=350)

        self.next_btn = tk.Button(
            self.root,
            text="Next Joke",
            command=self.new_joke,
            width=15,
            font=("Arial", 11),
            bg="#5C6BC0",
            fg="white"
        )
        self.next_btn.place(x=240, y=390)

        self.quit_btn = tk.Button(
            self.root,
            text="Quit",
            command=self.root.destroy,
            width=10,
            font=("Arial", 11),
            bg="#E57373"
        )
        self.quit_btn.place(x=255, y=430)

    def new_joke(self):
        if not self.jokes:
            self.setup_label.config(text="No jokes found!")
            return

        joke = random.choice(self.jokes)
        parts = joke.split("?", 1)

        self.current_setup = parts[0] + "?"
        self.current_punchline = parts[1]

        self.avatar.config(text="🤖")
        self.animate_text(self.setup_label, self.current_setup)
        self.punchline_label.config(text="")
        self.show_btn.config(state=tk.NORMAL)

    def show_punchline(self):
        self.animate_text(self.punchline_label, self.current_punchline)
        self.avatar.config(text=random.choice(["😂", "🤣", "😆", "😹"]))

    def animate_text(self, widget, text, delay=30):
        widget.config(text="")
        self.cancel_animation()

        def reveal(i=0):
            if i <= len(text):
                widget.config(text=text[:i])
                self.animation_id = self.root.after(delay, reveal, i+1)

        reveal()

    def cancel_animation(self):
        if self.animation_id:
            try:
                self.root.after_cancel(self.animation_id)
            except:
                pass
            self.animation_id = None

if __name__ == "__main__":
    root = tk.Tk()
    app = JokeApp(root)
    root.mainloop()
