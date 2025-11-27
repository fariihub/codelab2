import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
import threading
import time
from datetime import datetime

SCORES_FILE = "scores.json"
MAX_QUESTIONS = 10
LEADERBOARD_SIZE = 5

DEFAULT_THEME = "dark" 

DIFFICULTY_SETTINGS = {
    "Easy": {
        "operators": ["+", "-", "*"],
        "min": 1,
        "max": 10,
        "allow_decimal": False,
        "timer": 30,
    },
    "Medium": {
        "operators": ["+", "-", "*", "/"],
        "min": 1,
        "max": 50,
        "allow_decimal": False,
        "timer": 20,
    },
    "Hard": {
        "operators": ["+", "-", "*", "/"],
        "min": -50,
        "max": 100,
        "allow_decimal": True,
        "timer": 15,
    }
}

def safe_calculate(n1, op, n2):
    """Compute arithmetic without eval. Return a float result (or raise)."""
    try:
        if op == "+":
            return n1 + n2
        if op == "-":
            return n1 - n2
        if op == "*":
            return n1 * n2
        if op == "/":
            return n1 / n2
        raise ValueError(f"Unsupported operator '{op}'")
    except Exception:
        raise


def format_answer(ans, allow_decimal):
    """Format answer for display and comparison."""
    if allow_decimal:
        return round(float(ans), 2)
    else:
        return int(round(ans))

class Question:
    """Represents a single arithmetic question."""

    def __init__(self, n1, op, n2, allow_decimal=False):
        self.n1 = n1
        self.op = op
        self.n2 = n2
        self.allow_decimal = allow_decimal
        raw = safe_calculate(self.n1, self.op, self.n2)
        if not allow_decimal:
            self.answer = format_answer(raw, False)
        else:
            self.answer = format_answer(raw, True)

    def text(self):
        """Return the textual representation shown to user."""
        def fmt(x):
            if isinstance(x, int) or (isinstance(x, float) and x.is_integer()):
                return str(int(x))
            return f"{x:.2f}"
        return f"{fmt(self.n1)} {self.op} {fmt(self.n2)} = ?"

    def check(self, user_input):
        """Check user input (string) and return (is_correct, parsed_answer, expected)."""
        try:
            if user_input.strip() == "":
                return False, None, self.answer
            if self.allow_decimal:
                user_val = float(user_input)
                user_val = round(user_val, 2)
                expected = self.answer
                return abs(user_val - expected) < 0.01, user_val, expected
            else:
                user_val = int(round(float(user_input)))
                expected = int(self.answer)
                return user_val == expected, user_val, expected
        except Exception:
            return False, None, self.answer


class QuizEngine:
    """Engine that generates questions, tracks score and incorrect answers."""

    def __init__(self, difficulty_name="Easy", max_questions=MAX_QUESTIONS):
        self.difficulty_name = difficulty_name
        self.settings = DIFFICULTY_SETTINGS[difficulty_name]
        self.max_questions = max_questions
        self.score = 0
        self.asked = 0
        self.incorrect = []
        self.history = []
        self.current_question = None
        self.rng = random.Random()

    def new_question(self):
        """Generate a new Question according to difficulty."""
        ops = self.settings["operators"]
        minv = self.settings["min"]
        maxv = self.settings["max"]
        allow_decimal = self.settings["allow_decimal"]

        op = self.rng.choice(ops)
        
        if op == "/":
            if not allow_decimal:
                b = self.rng.randint(max(1, minv), maxv)
                a = b * self.rng.randint(max(1, minv), max(10, maxv // max(1, b)))
            else:
                b = self.rng.randint(max(1, minv), maxv)
                a = self.rng.uniform(minv, maxv)
        else:
            if allow_decimal:
                a = round(self.rng.uniform(minv, maxv), 2)
                b = round(self.rng.uniform(minv, maxv), 2)
            else:
                a = self.rng.randint(minv, maxv)
                b = self.rng.randint(minv, maxv)

        q = Question(a, op, b, allow_decimal=allow_decimal)
        self.current_question = q
        return q

    def submit_answer(self, user_input):
        """Check answer, update score and history. Return (correct, parsed, expected)."""
        if not self.current_question:
            raise RuntimeError("No current question to submit.")
        correct, parsed, expected = self.current_question.check(user_input)
        self.asked += 1
        if correct:
            self.score += 1
        else:
            self.incorrect.append((self.current_question, parsed, expected))
        qtext = self.current_question.text()
        self.history.append((qtext, parsed, expected, bool(correct)))
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
    """Handles leaderboard persistence to a JSON file."""

    def __init__(self, filename=SCORES_FILE, size=LEADERBOARD_SIZE):
        self.filename = filename
        self.size = size
        self.scores = self._load()

    def _load(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
        return []

    def _save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add_score(self, name, score, difficulty):
        entry = {
            "name": name,
            "score": score,
            "difficulty": difficulty,
            "date": datetime.utcnow().isoformat() + "Z"
        }
        self.scores.append(entry)
        self.scores.sort(key=lambda x: (-x["score"], x["date"]))
        self.scores = self.scores[: self.size]
        self._save()

    def top_scores(self):
        return self.scores.copy()

class QuizGUI:
    def __init__(self, master):
        self.master = master
        master.title("Maths Quiz — Distinction Edition")
        master.geometry("720x480")
        master.minsize(620, 420)
        self.theme = DEFAULT_THEME

        self.difficulty = tk.StringVar(value="Easy")
        self.player_name = tk.StringVar(value="Player")
        self.timer_seconds = tk.IntVar(value=DIFFICULTY_SETTINGS[self.difficulty.get()]["timer"])
        self.paused = False
        self._timer_thread = None
        self._timer_stop_event = threading.Event()

        self.engine = QuizEngine(difficulty_name=self.difficulty.get(), max_questions=MAX_QUESTIONS)
        self.leaderboard = Leaderboard()

        self._build_styles()
        self._build_frames()
        self._build_header()
        self._build_settings_panel()
        self._build_quiz_panel()
        self._build_footer()

        self.apply_theme(self.theme)

        self._update_timer_config_from_difficulty()
        self.show_start_screen()

    def _build_styles(self):
        self.style = ttk.Style(self.master)
        default_font = ("Helvetica", 12)
        self.style.configure("TLabel", font=default_font)
        self.style.configure("TButton", font=default_font)
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
        self.footer_frame.pack(fill="x", pady=(8, 0))

    def _build_header(self):
        self.title_label = ttk.Label(self.header_frame, text="Maths Quiz — Distinction Edition", style="Header.TLabel")
        self.title_label.pack(side="left")

        self.theme_btn = ttk.Button(self.header_frame, text="Toggle Theme", command=self._toggle_theme)
        self.theme_btn.pack(side="right")

    def _build_settings_panel(self):
        ttk.Label(self.left_panel, text="Player name:").pack(anchor="w", pady=(2, 0))
        self.name_entry = ttk.Entry(self.left_panel, textvariable=self.player_name)
        self.name_entry.pack(fill="x", pady=(0, 8))

        ttk.Label(self.left_panel, text="Difficulty:").pack(anchor="w")
        self.diff_combo = ttk.Combobox(self.left_panel, values=list(DIFFICULTY_SETTINGS.keys()), state="readonly", textvariable=self.difficulty)
        self.diff_combo.pack(fill="x", pady=(0, 8))
        self.diff_combo.bind("<<ComboboxSelected>>", self._on_difficulty_change)

        ttk.Label(self.left_panel, text="Time per question:").pack(anchor="w")
        self.timer_label = ttk.Label(self.left_panel, textvariable=self.timer_seconds)
        self.timer_label.pack(anchor="w", pady=(0, 8))

        ttk.Label(self.left_panel, text="Leaderboard (Top):").pack(anchor="w", pady=(8, 0))
        self.lb_list = tk.Listbox(self.left_panel, height=8)
        self.lb_list.pack(fill="both", pady=(4, 0))
        self._refresh_leaderboard_list()

    def _build_quiz_panel(self):
        self.start_frame = ttk.Frame(self.right_panel)
        self.start_frame.pack(fill="both", expand=True)

        self.instructions = ttk.Label(self.start_frame, text=(
            "Welcome! Choose your difficulty, enter your name, then press Start.\n"
            f"There are {MAX_QUESTIONS} questions per quiz. Good luck!"))
        self.instructions.pack(pady=(20, 10))

        self.start_btn = ttk.Button(self.start_frame, text="Start Quiz", command=self._start_quiz)
        self.start_btn.pack()

        self.quiz_frame = ttk.Frame(self.right_panel)

        self.top_quiz_frame = ttk.Frame(self.quiz_frame)
        self.top_quiz_frame.pack(fill="x", pady=(8, 6))

        self.progress_label = ttk.Label(self.top_quiz_frame, text="Question 0 / 0", style="TLabel")
        self.progress_label.pack(side="left")

        self.score_label = ttk.Label(self.top_quiz_frame, text="Score: 0")
        self.score_label.pack(side="right")

        self.question_label = ttk.Label(self.quiz_frame, text="", font=("Helvetica", 20, "bold"), wraplength=420, justify="center")
        self.question_label.pack(pady=(20, 10))

        self.answer_var = tk.StringVar()
        self.answer_entry = ttk.Entry(self.quiz_frame, textvariable=self.answer_var, font=("Helvetica", 14))
        self.answer_entry.pack(pady=(6, 6))
        self.answer_entry.bind("<Return>", lambda ev: self._submit_answer())

        self.timer_display = ttk.Label(self.quiz_frame, text="Time left: --")
        self.timer_display.pack()

        self.btn_frame = ttk.Frame(self.quiz_frame)
        self.btn_frame.pack(pady=(10, 0))

        self.submit_btn = ttk.Button(self.btn_frame, text="Submit", command=self._submit_answer)
        self.submit_btn.grid(row=0, column=0, padx=6)

        self.next_btn = ttk.Button(self.btn_frame, text="Skip", command=self._skip_question)
        self.next_btn.grid(row=0, column=1, padx=6)

        self.quit_btn = ttk.Button(self.btn_frame, text="Quit", command=self._confirm_quit)
        self.quit_btn.grid(row=0, column=2, padx=6)

        self.end_frame = ttk.Frame(self.right_panel)

        self.end_summary = ttk.Label(self.end_frame, text="", font=("Helvetica", 14))
        self.end_summary.pack(pady=(12, 8))

        self.review_list = tk.Listbox(self.end_frame)
        self.review_list.pack(fill="both", expand=True, pady=(4, 6))

        self.end_btn_frame = ttk.Frame(self.end_frame)
        self.end_btn_frame.pack(pady=(10, 0))

        self.save_btn = ttk.Button(self.end_btn_frame, text="Save Score", command=self._save_score)
        self.save_btn.grid(row=0, column=0, padx=6)

        self.restart_btn = ttk.Button(self.end_btn_frame, text="Restart", command=self._restart_quiz)
        self.restart_btn.grid(row=0, column=1, padx=6)

        self.return_home_btn = ttk.Button(self.end_btn_frame, text="Home", command=self.show_start_screen)
        self.return_home_btn.grid(row=0, column=2, padx=6)

    def _build_footer(self):
        self.footer_status = ttk.Label(self.footer_frame, text="Ready", anchor="w")
        self.footer_status.pack(fill="x")

    def apply_theme(self, theme):
        """Apply simple dark/light theme."""
        bg_dark = "#2a303f"
        fg_dark = "#8B8049"
        accent = "#2a8bd6"
        bg_light = "#acacac"
        fg_light = "#6200FF"
        accent_light = "#2a8bd6"

        if theme == "dark":
            bg = bg_dark
            fg = fg_dark
            accent_color = accent
            entry_bg = "#2a303f"
        else:
            bg = bg_light
            fg = fg_light
            accent_color = accent_light
            entry_bg = "#acacac"

        self.master.configure(bg=bg)
        self.container.configure(style="TFrame")
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("Header.TLabel", background=bg, foreground=accent_color)
        self.style.configure("TButton", background=bg, foreground=fg)
        self.title_label.configure(background=bg)
        self.header_frame.configure(style="TFrame")
        for widget in [self.name_entry, self.diff_combo, self.answer_entry]:
            try:
                widget.configure(background=entry_bg, foreground=fg)
            except Exception:
                pass
        for lb in [self.lb_list, self.review_list]:
            lb.configure(background=entry_bg, foreground=fg)

    def _toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme(self.theme)

    def _refresh_leaderboard_list(self):
        self.lb_list.delete(0, tk.END)
        for idx, e in enumerate(self.leaderboard.top_scores(), start=1):
            text = f"{idx}. {e['name']} — {e['score']}/ {MAX_QUESTIONS} ({e['difficulty']})"
            self.lb_list.insert(tk.END, text)

    def _update_timer_config_from_difficulty(self):
        d = self.difficulty.get()
        t = DIFFICULTY_SETTINGS.get(d, DIFFICULTY_SETTINGS["Easy"])["timer"]
        self.timer_seconds.set(t)
        self.engine = QuizEngine(difficulty_name=d, max_questions=MAX_QUESTIONS)

    def show_start_screen(self):
        self._stop_timer_thread()
        self._hide_all_right_frames()
        self.start_frame.pack(fill="both", expand=True)
        self.footer_status.config(text="Ready — set your name and difficulty, then Start.")

    def _hide_all_right_frames(self):
        for frame in [self.start_frame, self.quiz_frame, self.end_frame]:
            frame.pack_forget()

    def _on_difficulty_change(self, event=None):
        self._update_timer_config_from_difficulty()
        self.timer_label.config(text=f"{self.timer_seconds.get()}s")

    def _start_quiz(self):
        name = self.player_name.get().strip()
        if name == "":
            messagebox.showwarning("Name required", "Please enter your name before starting.")
            return
        self.engine = QuizEngine(difficulty_name=self.difficulty.get(), max_questions=MAX_QUESTIONS)
        self.answer_var.set("")
        self._hide_all_right_frames()
        self.quiz_frame.pack(fill="both", expand=True)
        self.footer_status.config(text="Quiz started.")
        self._update_timer_config_from_difficulty()
        self._present_next_question()

    def _present_next_question(self):
        self._stop_timer_thread()
        if self.engine.is_finished():
            self._end_quiz()
            return
        q = self.engine.new_question()
        q_index = self.engine.asked + 1
        self.progress_label.config(text=f"Question {q_index} / {self.engine.max_questions}")
        self.score_label.config(text=f"Score: {self.engine.score}")
        self.question_label.config(text=q.text())
        self.answer_var.set("")
        self.answer_entry.focus_set()
        self._start_timer_thread(self.timer_seconds.get())

    def _submit_answer(self):
        self._stop_timer_thread()
        user_text = self.answer_var.get()
        if user_text.strip() == "":
            if not messagebox.askyesno("Empty Answer", "You left the answer blank. Submit as blank (counts as wrong)?"):
                self._start_timer_thread(self.timer_seconds.get())
                return
        try:
            correct, parsed, expected = self.engine.submit_answer(user_text)
        except Exception as e:
            messagebox.showerror("Submission Error", f"An internal error occurred: {e}")
            return
        if correct:
            messagebox.showinfo("Correct!", "Great — that's correct!")
        else:
            messagebox.showinfo("Incorrect", f"That's not correct. Correct answer: {expected}")
        if self.engine.is_finished():
            self._end_quiz()
        else:
            self._present_next_question()

    def _skip_question(self):
        self._stop_timer_thread()
        try:
            self.engine.submit_answer("")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to skip: {e}")
            return
        if self.engine.is_finished():
            self._end_quiz()
        else:
            self._present_next_question()

    def _end_quiz(self):
        self._stop_timer_thread()
        self._hide_all_right_frames()
        self.end_frame.pack(fill="both", expand=True)
        self.end_summary.config(text=f"Quiz Complete — {self.player_name.get()} scored {self.engine.score} / {self.engine.max_questions}")
        self.review_list.delete(0, tk.END)
        for (qtext, user, expected, correct) in self.engine.history:
            mark = "✓" if correct else "✗"
            user_disp = "-" if user is None else str(user)
            self.review_list.insert(tk.END, f"{mark} {qtext} You: {user_disp} | Ans: {expected}")
        self._refresh_leaderboard_list()
        self.footer_status.config(text="Quiz finished. Save your score to leaderboard.")

    def _save_score(self):
        name = self.player_name.get().strip()
        if name == "":
            messagebox.showwarning("Name required", "Please enter name to save score.")
            return
        self.leaderboard.add_score(name, self.engine.score, self.difficulty.get())
        messagebox.showinfo("Saved", "Score saved to leaderboard.")
        self._refresh_leaderboard_list()
        self.save_btn.configure(state="disabled")

    def _restart_quiz(self):
        self.engine.reset()
        self.save_btn.configure(state="normal")
        self.show_start_screen()

    def _confirm_quit(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit the quiz?"):
            self.master.destroy()

    def _start_timer_thread(self, seconds):
        """Start a new timer thread for the current question."""
        self._stop_timer_thread()
        self._timer_stop_event.clear()
        self._timer_thread = threading.Thread(target=self._timer_run, args=(seconds,), daemon=True)
        self._timer_thread.start()

    def _stop_timer_thread(self):
        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_stop_event.set()
            self._timer_thread.join(timeout=0.1)
        self._timer_thread = None
        self._timer_stop_event.clear()
        self.timer_display.config(text="Time left: --")

    def _timer_run(self, seconds):
        remaining = seconds
        while remaining >= 0 and not self._timer_stop_event.is_set():
            self.timer_display.config(text=f"Time left: {remaining}s")
            time.sleep(1)
            remaining -= 1
        if self._timer_stop_event.is_set():
            return
        self.master.after(10, self._on_time_expired)

    def _on_time_expired(self):
        messagebox.showinfo("Time's up!", "Time expired for this question — it will be marked incorrect.")
        try:
            self.engine.submit_answer("")  # counts as wrong
        except Exception:
            pass
        if self.engine.is_finished():
            self._end_quiz()
        else:
            self._present_next_question()

    def on_close(self):
        self._stop_timer_thread()
        self.master.destroy()

def main():
    root = tk.Tk()
    app = QuizGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
