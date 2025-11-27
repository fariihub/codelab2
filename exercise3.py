import tkinter as tk
from tkinter import messagebox, simpledialog

FILE_NAME = "studentMarks.txt"

def get_grade(percentage: float) -> str:
    """Return grade letter based on percentage."""
    if percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    return "F"


def calculate_marks(cw1, cw2, cw3, exam):
    """
    Given 3 coursework marks (each /20) and an exam (/100),
    return total coursework, overall, percentage and grade.
    """
    cw_total = cw1 + cw2 + cw3               
    overall = cw_total + exam              
    percentage = round((overall / 160) * 100, 2)
    grade = get_grade(percentage)
    return cw_total, overall, percentage, grade

def load_students():
    students = []
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{FILE_NAME}' not found.")
        return students

    if not lines:
        return students
        
    start_index = 1 if lines[0].isdigit() else 0

    for line in lines[start_index:]:
        parts = line.split(",")
        if len(parts) != 6:
            continue

        sid = parts[0].strip()
        name = parts[1].strip()

        try:
            cw1, cw2, cw3 = int(parts[2]), int(parts[3]), int(parts[4])
            exam = int(parts[5])
        except ValueError:
            continue

        cw_total, overall, pct, grade = calculate_marks(cw1, cw2, cw3, exam)

        students.append({
            "id": sid,
            "name": name,
            "cw1": cw1, "cw2": cw2, "cw3": cw3,
            "exam": exam,
            "cw_total": cw_total,
            "overall": overall,
            "percentage": pct,
            "grade": grade
        })

    return students

def show_scroll(title, text):
    """Display long text in a scrollable window."""
    win = tk.Toplevel()
    win.title(title)
    win.geometry("700x600")
    win.configure(bg="white")

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True)

    text_widget = tk.Text(
        frame,
        wrap="word",
        bg="white",
        font=("Segoe UI", 11),
        padx=10,
        pady=10
    )
    text_widget.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")

    text_widget.configure(yscrollcommand=scrollbar.set)

    text_widget.insert("end", text)
    text_widget.configure(state="disabled")

    win.bind_all("<MouseWheel>", lambda e: text_widget.yview_scroll(int(-1*(e.delta/120)), "units"))

def format_one(s):
    """Format ONE student record."""
    return (
        f"Student Name: {s['name']}\n"
        f"Student Number: {s['id']}\n"
        f"Total Coursework Mark: {s['cw_total']} / 60\n"
        f"Exam Mark: {s['exam']} / 100\n"
        f"Overall Percentage: {s['percentage']}%\n"
        f"Grade: {s['grade']}\n"
    )

def format_all_students(students):
    """Format ALL student records + summary."""
    if not students:
        return "No student records available."

    text = ""
    for s in students:
        text += format_one(s)
        text += "-" * 50 + "\n"

    avg = round(sum(s["percentage"] for s in students) / len(students), 2)

    text += f"\nTotal Students: {len(students)}\n"
    text += f"Average Percentage: {avg}%"

    return text

def view_all_records():
    students = load_students()
    text = format_all_students(students)
    show_scroll("All Student Records", text)

def view_individual_record():
    sid = simpledialog.askstring("Find Student", "Enter Student Number:")
    if not sid:
        return

    students = load_students()
    found = [s for s in students if s["id"] == sid.strip()]

    if not found:
        messagebox.showerror("Error", "Student not found.")
        return

    show_scroll("Individual Record", format_one(found[0]))

def show_highest_score():
    students = load_students()
    if not students:
        return
    top = max(students, key=lambda s: s["overall"])
    show_scroll("Highest Score", format_one(top))

def show_lowest_score():
    students = load_students()
    if not students:
        return
    low = min(students, key=lambda s: s["overall"])
    show_scroll("Lowest Score", format_one(low))

root = tk.Tk()
root.title("Student Manager – Exercise 3")
root.geometry("480x500")
root.config(bg="#f2f2f2")

title = tk.Label(
    root,
    text="Student Manager – Exercise 3",
    font=("Segoe UI", 20, "bold"),
    bg="#f2f2f2"
)
title.pack(pady=20)

def menu_btn(label, cmd):
    btn = tk.Button(
        root,
        text=label,
        command=cmd,
        width=30,
        height=1,
        font=("Segoe UI", 12),
        bg="white"
    )
    btn.pack(pady=7)
    return btn

menu_btn("1. View All Records", view_all_records)
menu_btn("2. View Individual Record", view_individual_record)
menu_btn("3. Show Highest Total Score", show_highest_score)
menu_btn("4. Show Lowest Total Score", show_lowest_score)

root.mainloop()

