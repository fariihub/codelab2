import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

SCORES_FILE = "scores.json"
MAX_QUESTIONS = 10
LEADERBOARD_SIZE = 5

DEFAULT_THEME = "dark"

DIFFICULTY_SETTINGS = {
    "Easy": {"operators": ["+", "-", "*"], "min": 1, "max": 10, "allow_decimal": False, "timer": 30},
    "Medium": {"operators": ["+", "-", "*", "/"], "min": 1, "max": 50, "allow_decimal": False, "timer": 20},
    "Hard": {"operators": ["+", "-", "*", "/"], "min": -50, "max": 100, "allow_decimal": True, "timer": 15}
}

def safe_calculate(n1, op, n2):
    if op == "+": return n1 + n2
    if op == "-": return n1 - n2
    if op == "*": return n1 * n2
    if op == "/": return n1 / n2
    raise ValueError("Invalid operator")


def format_answer(ans, allow_decimal):
    return round(float(ans), 2) if allow_decimal else int(round(ans))

class Question:
    def __init__(self, n1, op, n2, allow_decimal=False):
        self.n1 = n1
        self.op = op
        self.n2 = n2
        self.allow_decimal = allow_decimal
        raw = safe_calculate(n1, op, n2)
        self.answer = format_answer(raw, allow_decimal)

    def text(self):
        def fmt(v):
            if isinstance(v, float) and v.is_integer():
                return str(int(v))
            return f"{v:.2f}" if isinstance(v, float) else str(v)
        return f"{fmt(self.n1)} {self.op} {fmt(self.n2)} = ?"

    def check(self, user_input):
        if user_input.strip() == "":
            return False, None, self.answer
        try:
            if self.allow_decimal:
                u = round(float(user_input), 2)
                return abs(u - self.answer) < 0.01, u, self.answer
            else:
                u = int(round(float(user_input)))
                return u == self.answer, u, self.answer
        except:
            return False, None, self.answer


class QuizEngine:
    def __init__(self, difficulty_name="Easy", max_questions=10):
        self.settings = DIFFICULTY_SETTINGS[difficulty_name]
        self.max_questions = max_questions
        self.difficulty_name = difficulty_name
        self.score = 0
        self.asked = 0
        self.incorrect = []
        self.history = []
        self.current_question = None
        self.rng = random.Random()

    def new_question(self):
        ops = self.settings["operators"]
        minv, maxv = self.settings["min"], self.settings["max"]
        allow = self.settings["allow_decimal"]

        op = self.rng.choice(ops)

        if op == "/":
            if not allow:
                b = self.rng.randint(max(1, minv), maxv)
                a = b * self.rng.randint(1, 10)
            else:
                b = self.rng.uniform(minv, maxv)
                a = self.rng.uniform(minv, maxv)
        else:
            a = round(self.rng.uniform(minv, maxv), 2) if allow else self.rng.randint(minv, maxv)
            b = round(self.rng.uniform(minv, maxv), 2) if allow else self.rng.randint(minv, maxv)

        q = Question(a, op, b, allow)
        self.current_question = q
        return q

    def submit_answer(self, txt):
        correct, parsed, expected = self.current_question.check(txt)
        self.asked += 1

        if correct:
            self.score += 1
        else:
            self.incorrect.append((self.current_question, parsed, expected))

        self.history.append((self.current_question.text(), parsed, expected, correct))
        return correct, parsed, expected

    def is_finished(self):
        return self.asked >= self.max_questions

    def reset(self):
        self.score = 0
        self.asked = 0
        self.incorrect.clear()
        self.history.clear()
        self.current_question = None


class Leaderboard:
    def __init__(self, filename=SCORES_FILE, size=5):
        self.filename = filename
        self.size = size
        self.scores = self._load()

    def _load(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=2)
        except:
            pass

    def add_score(self, name, score, difficulty):
        entry = {"name": name, "score": score, "difficulty": difficulty,
                 "date": datetime.utcnow().isoformat() + "Z"}
        self.scores.append(entry)
        self.scores.sort(key=lambda x: (-x["score"], x["date"]))
        self.scores = self.scores[:self.size]
        self._save()

    def top_scores(self):
        return self.scores.copy()

class QuizGUI:
    def __init__(self, master):
        self.master = master
        master.title("Maths Quiz — Distinction Edition")
        master.geometry("720x480")

        self.theme = DEFAULT_THEME
        self.difficulty = tk.StringVar(value="Easy")
        self.player_name = tk.StringVar(value="Player")

        self.after_id = None
        self.time_left = 0

        self.engine = QuizEngine("Easy", MAX_QUESTIONS)
        self.leaderboard = Leaderboard()

        self._build_styles()
        self._build_frames()
        self._build_header()
        self._build_settings_panel()
        self._build_quiz_panel()
        self._build_footer()

        self.apply_theme(self.theme)
        self.show_start_screen()

    def _build_styles(self):
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))

    def _build_frames(self):
        self.container = ttk.Frame(self.master, padding=10)
        self.container.pack(fill="both", expand=True)

        self.header_frame = ttk.Frame(self.container)
        self.header_frame.pack(fill="x", pady=(0, 8))

        self.content_frame = ttk.Frame(self.container)
        self.content_frame.pack(fill="both", expand=True)

        self.left_panel = ttk.Frame(self.content_frame, width=220)
        self.left_panel.pack(side="left", fill="y", padx=(0, 8))

        self.right_panel = ttk.Frame(self.content_frame)
        self.right_panel.pack(side="left", fill="both", expand=True)

        self.footer_frame = ttk.Frame(self.container)
        self.footer_frame.pack(fill="x", pady=8)

    def _build_header(self):
        ttk.Label(self.header_frame, text="Maths Quiz — Distinction Edition",
                  style="Header.TLabel").pack(side="left")

        ttk.Button(self.header_frame, text="Toggle Theme",
                   command=self._toggle_theme).pack(side="right")

    def _build_settings_panel(self):
        ttk.Label(self.left_panel, text="Player name:").pack(anchor="w")
        self.name_entry = ttk.Entry(self.left_panel, textvariable=self.player_name)
        self.name_entry.pack(fill="x", pady=5)

        ttk.Label(self.left_panel, text="Difficulty:").pack(anchor="w")
        self.diff_combo = ttk.Combobox(self.left_panel, state="readonly",
                                       values=list(DIFFICULTY_SETTINGS.keys()),
                                       textvariable=self.difficulty)
        self.diff_combo.pack(fill="x", pady=5)
        self.diff_combo.bind("<<ComboboxSelected>>", self._on_difficulty_change)

        ttk.Label(self.left_panel, text="Leaderboard:").pack(anchor="w")
        self.lb_list = tk.Listbox(self.left_panel, height=7)
        self.lb_list.pack(fill="both")
        self._refresh_leaderboard_list()

    def _build_quiz_panel(self):
        self.start_frame = ttk.Frame(self.right_panel)
        ttk.Label(self.start_frame,
                  text=f"Welcome! Choose difficulty and press Start.\nTotal {MAX_QUESTIONS} questions.").pack(pady=20)

        ttk.Button(self.start_frame, text="Start Quiz",
                   command=self._start_quiz).pack()

        self.quiz_frame = ttk.Frame(self.right_panel)
        self.progress_label = ttk.Label(self.quiz_frame, text="Question 0/0")
        self.progress_label.pack()

        self.score_label = ttk.Label(self.quiz_frame, text="Score: 0")
        self.score_label.pack()

        self.question_label = ttk.Label(self.quiz_frame, text="", font=("Helvetica", 20))
        self.question_label.pack(pady=10)

        self.answer_var = tk.StringVar()
        self.answer_entry = ttk.Entry(self.quiz_frame, textvariable=self.answer_var, font=("Helvetica", 14))
        self.answer_entry.pack(pady=10)
        self.answer_entry.bind("<Return>", lambda e: self._submit_answer())

        self.timer_display = ttk.Label(self.quiz_frame, text="Time left: --")
        self.timer_display.pack()

        btns = ttk.Frame(self.quiz_frame)
        btns.pack(pady=10)

        ttk.Button(btns, text="Submit", command=self._submit_answer).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Skip", command=self._skip_question).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Quit", command=self._confirm_quit).grid(row=0, column=2, padx=5)

        self.end_frame = ttk.Frame(self.right_panel)
        self.end_summary = ttk.Label(self.end_frame, text="", font=("Helvetica", 14))
        self.end_summary.pack(pady=10)

        self.review_list = tk.Listbox(self.end_frame)
        self.review_list.pack(fill="both", expand=True)

        end_btns = ttk.Frame(self.end_frame)
        end_btns.pack(pady=10)

        self.save_btn = ttk.Button(end_btns, text="Save Score", command=self._save_score)
        self.save_btn.grid(row=0, column=0, padx=5)

        ttk.Button(end_btns, text="Restart", command=self._restart_quiz).grid(row=0, column=1, padx=5)
        ttk.Button(end_btns, text="Home", command=self.show_start_screen).grid(row=0, column=2, padx=5)

    def _build_footer(self):
        self.footer_status = ttk.Label(self.footer_frame, text="Ready")
        self.footer_status.pack(fill="x")

    def apply_theme(self, theme):
        if theme == "dark":
            bg = "#030E2E"
            fg = "#5DD9FF"
            entry_bg = "white"
        else:
            bg = "#acacac"
            fg = "#4C00FF"
            entry_bg = "white"

        self.master.configure(bg=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("Header.TLabel", background=bg, foreground=fg)

        for widget in [self.name_entry, self.diff_combo, self.answer_entry]:
            widget.configure(background=entry_bg)

        self.lb_list.configure(bg=entry_bg, fg=fg)
        self.review_list.configure(bg=entry_bg, fg=fg)

    def _toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme(self.theme)

    def show_start_screen(self):
        self._cancel_timer()
        self._hide_frames()
        self.start_frame.pack(fill="both", expand=True)
        self.footer_status.config(text="Ready.")

    def _hide_frames(self):
        for f in [self.start_frame, self.quiz_frame, self.end_frame]:
            f.pack_forget()

    def _on_difficulty_change(self, e=None):
        diff = self.difficulty.get()
        self.engine = QuizEngine(diff, MAX_QUESTIONS)
        self.footer_status.config(text=f"Difficulty set to {diff}")

    def _start_quiz(self):
        if self.player_name.get().strip() == "":
            messagebox.showwarning("Name required", "Enter your name first.")
            return

        self.engine = QuizEngine(self.difficulty.get(), MAX_QUESTIONS)
        self._cancel_timer()
        self._hide_frames()
        self.quiz_frame.pack(fill="both", expand=True)
        self.footer_status.config(text="Quiz started.")
        self._present_next_question()

    def _present_next_question(self):
        self._cancel_timer()

        if self.engine.is_finished():
            return self._end_quiz()

        q = self.engine.new_question()

        self.progress_label.config(text=f"Question {self.engine.asked+1}/{self.engine.max_questions}")
        self.score_label.config(text=f"Score: {self.engine.score}")
        self.question_label.config(text=q.text())

        self.answer_var.set("")
        self.answer_entry.focus()

        duration = DIFFICULTY_SETTINGS[self.difficulty.get()]["timer"]
        self._start_timer(duration)

    def _submit_answer(self):
        self._cancel_timer()
        txt = self.answer_var.get().strip()
        correct, parsed, expected = self.engine.submit_answer(txt)

        if correct:
            messagebox.showinfo("Correct!", "Nice job!")
        else:
            messagebox.showinfo("Incorrect", f"Correct answer was {expected}")

        self._present_next_question()

    def _skip_question(self):
        self._cancel_timer()
        self.engine.submit_answer("")
        self._present_next_question()

    def _end_quiz(self):
        self._cancel_timer()
        self._hide_frames()
        self.end_frame.pack(fill="both", expand=True)

        self.end_summary.config(
            text=f"{self.player_name.get()} scored {self.engine.score}/{self.engine.max_questions}"
        )

        self.review_list.delete(0, tk.END)
        for qtext, user, exp, correct in self.engine.history:
            mark = "✓" if correct else "✗"
            user_disp = "-" if user is None else str(user)
            self.review_list.insert(tk.END, f"{mark} {qtext} You: {user_disp} | Ans: {exp}")

        self.footer_status.config(text="Quiz finished.")

    def _save_score(self):
        name = self.player_name.get().strip()
        if not name:
            messagebox.showwarning("Error", "Enter a name.")
            return

        self.leaderboard.add_score(name, self.engine.score, self.difficulty.get())
        self.save_btn.configure(state="disabled")
        messagebox.showinfo("Saved", "Score saved!")
        self._refresh_leaderboard_list()

    def _restart_quiz(self):
        self.engine.reset()
        self.save_btn.configure(state="normal")
        self.show_start_screen()

    def _confirm_quit(self):
        if messagebox.askyesno("Quit?", "Quit the quiz?"):
            self.master.destroy()

    def _refresh_leaderboard_list(self):
        self.lb_list.delete(0, tk.END)
        for idx, e in enumerate(self.leaderboard.top_scores(), 1):
            self.lb_list.insert(tk.END, f"{idx}. {e['name']} — {e['score']} ({e['difficulty']})")

    def _start_timer(self, seconds):
        self._cancel_timer()
        self.time_left = seconds
        self._update_timer()

    def _update_timer(self):
        self.timer_display.config(text=f"Time left: {self.time_left}s")

        if self.time_left <= 0:
            self.master.after(200, self._on_time_expired)
            return

        self.time_left -= 1
        self.after_id = self.master.after(1000, self._update_timer)

    def _cancel_timer(self):
        if self.after_id:
            try:
                self.master.after_cancel(self.after_id)
            except:
                pass
        self.after_id = None

    def _on_time_expired(self):
        messagebox.showinfo("Time's Up!", "This question is marked incorrect.")
        self.engine.submit_answer("")
        self._present_next_question()

    def on_close(self):
        self._cancel_timer()
        self.master.destroy()

def main():
    root = tk.Tk()
    app = QuizGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
