import tkinter as tk
import random

# Load jokes from file
def load_jokes():
    with open("randomJokes.txt", "r") as file:
        jokes = file.readlines()
    return jokes

jokes = load_jokes()

# Select a random joke
def select_joke():
    global current_setup, current_punchline
    joke = random.choice(jokes)
    if "?" in joke:
        parts = joke.split("?", 1)
        current_setup = parts[0] + "?"
        current_punchline = parts[1]
    else:
        current_setup = joke
        current_punchline = "No punchline found."
    setup_label.config(text=current_setup)
    punchline_label.config(text="")

def show_punchline():
    punchline_label.config(text=current_punchline)

def quit_app():
    root.destroy()

# GUI Window
root = tk.Tk()
root.title("Alexa Joke Assistant")
root.geometry("450x300")
root.config(bg="#898EAA")

title_label = tk.Label(root, text="Alexa Joke Assistant", font=("Arial", 16, "bold"), fg="#F7F7F7", bg="#525775")
title_label.pack(pady=10)

setup_label = tk.Label(root, text="", font=("Arial", 14), wraplength=400, bg="#525775", fg="#F7F7F7")
setup_label.pack(pady=10)

punchline_label = tk.Label(root, text="", font=("Arial", 12, "italic"), wraplength=400, fg="#FFFFFF", bg="#525775")
punchline_label.pack(pady=10)

tell_joke_button = tk.Button(root, text="Alexa tell me a Joke", command=select_joke, width=25, bg="#525775", fg="#F7F7F7", activebackground="#525775", highlightbackground="#525775")
tell_joke_button.pack(pady=5)

punchline_button = tk.Button(root, text="Show Punchline", command=show_punchline, width=25, bg="#525775", fg="#F7F7F7", activebackground="#525775")
punchline_button.pack(pady=5)

next_button = tk.Button(root, text="Next Joke", command=select_joke, width=25, bg="#525775", fg="#F7F7F7", activebackground="#525775")
next_button.pack(pady=5)

quit_button = tk.Button(root, text="Quit", command=quit_app, width=25, bg="#FF9999")
quit_button.pack(pady=10)

root.mainloop()
