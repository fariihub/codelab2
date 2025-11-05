# =====================================================
# Project: 01 - Maths Quiz Application
# Author: Farwa Batool
# Module: CodeLab II – Programming Skills Portfolio
# Date: 27th November 2025
# =====================================================
# References:
# - ChatGPT (Prompt: “Create a Python GUI Maths Quiz using OOP and Tkinter”)
# - Python Documentation: https://docs.python.org/3/library/tkinter.html
# =====================================================

import tkinter as tk
from tkinter import messagebox
import random


class MathsQuiz:
    """
    A class representing a simple Maths Quiz application using Tkinter.
    This class demonstrates OOP principles such as encapsulation and abstraction.
    """

    def __init__(self, root):
        """Initialize GUI components and quiz state variables."""
        self.root = root
        self.root.title("Maths Quiz Application")
        self.root.geometry("400x300")
        self.root.config(bg="#20232a")

        # Quiz state
        self.score = 0
        self.question_count = 0
        self.current_question = ""
        self.correct_answer = 0

        # GUI components
        self.title_label = tk.Label(
            root, text="🧮 Maths Quiz", font=("Arial", 18, "bold"), fg="#61dafb", bg="#20232a"
        )
        self.title_label.pack(pady=10)

        self.question_label = tk.Label(
            root, text="", font=("Arial", 16), fg="white", bg="#20232a"
        )
        self.question_label.pack(pady=20)

        self.answer_entry = tk.Entry(root, font=("Arial", 14))
        self.answer_entry.pack()

        self.submit_btn = tk.Button(
            root,
            text="Submit Answer",
            font=("Arial", 12, "bold"),
            bg="#61dafb",
            fg="black",
            command=self.check_answer,
        )
        self.submit_btn.pack(pady=10)

        self.score_label = tk.Label(
            root, text=f"Score: {self.score}", font=("Arial", 14), fg="#61dafb", bg="#20232a"
        )
        self.score_label.pack(pady=10)

        self.next_question()

    def next_question(self):
        """Generate and display a new random arithmetic question."""
        operators = ['+', '-', '*', '/']
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operator = random.choice(operators)

        # Avoid division by zero and keep integer division simple
        if operator == '/':
            num1 = num1 * num2

        self.correct_answer = eval(f"{num1} {operator} {num2}")
        self.current_question = f"{num1} {operator} {num2} = ?"
        self.question_label.config(text=self.current_question)
        self.answer_entry.delete(0, tk.END)

    def check_answer(self):
        """Validate user input and update score."""
        try:
            user_answer = float(self.answer_entry.get())

            if abs(user_answer - self.correct_answer) < 0.01:
                self.score += 1
                messagebox.showinfo("Correct!", "Well done! 🎉")
            else:
                messagebox.showerror("Incorrect", f"The correct answer was {self.correct_answer}")

            self.question_count += 1
            self.score_label.config(text=f"Score: {self.score}")

            # Ask next question or end quiz
            if self.question_count < 5:
                self.next_question()
            else:
                messagebox.showinfo(
                    "Quiz Complete",
                    f"Final Score: {self.score}/5\nThank you for playing!"
                )
                self.root.destroy()

        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a numeric answer.")


# =====================================================
# Main Program Execution
# =====================================================

if __name__ == "__main__":
    window = tk.Tk()
    app = MathsQuiz(window)
    window.mainloop()
