import tkinter as tk
from tkinter import messagebox

FILE_NAME = "studentMarks.txt"

def get_grade(percentage: float) -> str:
    if percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    else:
        return "F"


def calculate_marks(cw1, cw2, cw3, exam):
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
    except:
        return []

    if not lines:
        return []

    try:
        int(lines[0])
        data_lines = lines[1:]
    except:
        data_lines = lines

    for line in data_lines:
        parts = line.split(",")
        if len(parts) != 6:
            continue

        sid, name = parts[0], parts[1]
        cw1, cw2, cw3, exam = map(int, parts[2:6])

        cw_total, overall, percent, grade = calculate_marks(cw1, cw2, cw3, exam)

        students.append({
            "id": sid,
            "name": name,
            "cw1": cw1, "cw2": cw2, "cw3": cw3,
            "exam": exam,
            "cw_total": cw_total,
            "overall": overall,
            "percentage": percent,
            "grade": grade
        })

    return students


def save_students(students):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(str(len(students)) + "\n")
        for s in students:
            f.write(f"{s['id']},{s['name']},{s['cw1']},{s['cw2']},{s['cw3']},{s['exam']}\n")

def show_scroll(title, text):
    win = tk.Toplevel()
    win.title(title)
    win.geometry("700x600")
    win.configure(bg="white")

    frame = tk.Frame(win, bg="white")
    frame.pack(fill="both", expand=True)

    text_widget = tk.Text(
        frame,
        font=("Segoe UI", 11),
        wrap="word",
        bg="white",
        padx=10,
        pady=10
    )
    text_widget.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")

    text_widget.configure(yscrollcommand=scrollbar.set)

    for line in text.split("\n"):
        if "Grade: A" in line:
            text_widget.insert("end", line + "\n", "A")
        elif "Grade: B" in line:
            text_widget.insert("end", line + "\n", "B")
        elif "Grade: C" in line:
            text_widget.insert("end", line + "\n", "C")
        elif "Grade: D" in line:
            text_widget.insert("end", line + "\n", "D")
        elif "Grade: F" in line:
            text_widget.insert("end", line + "\n", "F")
        else:
            text_widget.insert("end", line + "\n")

    text_widget.tag_config("A", foreground="green")
    text_widget.tag_config("B", foreground="blue")
    text_widget.tag_config("C", foreground="goldenrod")
    text_widget.tag_config("D", foreground="orange")
    text_widget.tag_config("F", foreground="red")

    text_widget.configure(state="disabled")

    def on_mousewheel(event):
        text_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

    win.bind_all("<MouseWheel>", on_mousewheel)

def format_one(s):
    return (
        f"Student Name: {s['name']}\n"
        f"Student Number: {s['id']}\n"
        f"Total Coursework Mark: {s['cw_total']} / 60\n"
        f"Exam Mark: {s['exam']} / 100\n"
        f"Overall Percentage: {s['percentage']}%\n"
        f"Grade: {s['grade']}\n"
    )


def format_all(students):
    if not students:
        return "No records."

    text = ""
    for s in students:
        text += format_one(s)
        text += "-" * 50 + "\n"

    avg = round(sum(s["percentage"] for s in students) / len(students), 2)
    text += f"\nTotal Students: {len(students)}"
    text += f"\nAverage Percentage: {avg}%"

    return text

def input_window(title, fields):
    win = tk.Toplevel()
    win.title(title)
    win.geometry("350x350")
    win.configure(bg="#f5f5f5")

    entries = {}
    row = 0

    for label, key in fields:
        tk.Label(win, text=label, bg="#f5f5f5",
                 font=("Segoe UI", 10)).grid(row=row, column=0,
                                             sticky="w", padx=10, pady=5)
        entry = tk.Entry(win, width=25, font=("Segoe UI", 10))
        entry.grid(row=row, column=1, padx=10, pady=5)
        entries[key] = entry
        row += 1

    result = {}

    def save():
        for k, ent in entries.items():
            result[k] = ent.get().strip()
        win.destroy()

    tk.Button(win, text="Save", width=10, command=save,
              bg="white").grid(row=row, column=0, pady=15)
    tk.Button(win, text="Cancel", width=10, command=win.destroy,
              bg="white").grid(row=row, column=1)

    win.wait_window()
    return result

def view_all():
    show_scroll("All Students", format_all(load_students()))


def view_individual():
    data = input_window("View Student", [("Enter Student Number:", "id")])
    sid = data.get("id", "")
    if not sid:
        return

    students = load_students()
    found = [s for s in students if s["id"] == sid]

    if found:
        show_scroll("Student Record", format_all(found))
    else:
        messagebox.showerror("Error", "Student not found.")


def show_highest():
    students = load_students()
    if not students:
        return
    top = max(students, key=lambda s: s["overall"])
    show_scroll("Highest Score", format_one(top))


def show_lowest():
    students = load_students()
    if not students:
        return
    low = min(students, key=lambda s: s["overall"])
    show_scroll("Lowest Score", format_one(low))


def sort_records():
    data = input_window("Sort Records", [("Enter 'asc' or 'desc':", "order")])
    order = data.get("order", "").lower()

    students = load_students()
    if order == "asc":
        students.sort(key=lambda s: s["overall"])
    elif order == "desc":
        students.sort(key=lambda s: s["overall"], reverse=True)
    else:
        messagebox.showerror("Error", "Invalid order.")
        return

    show_scroll("Sorted Records", format_all(students))


def add_student():
    fields = [
        ("Student ID (1000–9999):", "id"),
        ("Name:", "name"),
        ("CW1 (0–20):", "cw1"),
        ("CW2 (0–20):", "cw2"),
        ("CW3 (0–20):", "cw3"),
        ("Exam (0–100):", "exam")
    ]
    data = input_window("Add Student", fields)

    try:
        sid = data["id"]
        name = data["name"]
        cw1 = int(data["cw1"])
        cw2 = int(data["cw2"])
        cw3 = int(data["cw3"])
        exam = int(data["exam"])
    except:
        messagebox.showerror("Error", "Invalid input.")
        return

    if not (sid.isdigit() and 1000 <= int(sid) <= 9999):
        messagebox.showerror("Error", "Invalid ID.")
        return

    if not (0 <= cw1 <= 20 and 0 <= cw2 <= 20 and 0 <= cw3 <= 20 and 0 <= exam <= 100):
        messagebox.showerror("Error", "Marks out of range.")
        return

    students = load_students()

    if any(s["id"] == sid for s in students):
        messagebox.showerror("Error", "Student already exists.")
        return

    cw_total, overall, percent, grade = calculate_marks(cw1, cw2, cw3, exam)

    students.append({
        "id": sid, "name": name,
        "cw1": cw1, "cw2": cw2, "cw3": cw3, "exam": exam,
        "cw_total": cw_total, "overall": overall,
        "percentage": percent, "grade": grade
    })

    save_students(students)
    messagebox.showinfo("Success", "Student added.")


def delete_student():
    data = input_window("Delete Student", [("Enter Student Number:", "id")])
    sid = data.get("id", "")
    if not sid:
        return

    students = load_students()
    new_list = [s for s in students if s["id"] != sid]

    if len(new_list) == len(students):
        messagebox.showerror("Error", "Student does not exist.")
        return

    save_students(new_list)
    messagebox.showinfo("Deleted", "Student removed.")


def update_student():
    data = input_window("Update Student", [("Enter Student Number:", "id")])
    sid = data.get("id", "")
    if not sid:
        return

    students = load_students()
    for s in students:
        if s["id"] == sid:

            fields = [
                ("CW1 (0–20):", "cw1"),
                ("CW2 (0–20):", "cw2"),
                ("CW3 (0–20):", "cw3"),
                ("Exam (0–100):", "exam")
            ]
            new_marks = input_window("Update Marks", fields)

            try:
                s["cw1"] = int(new_marks["cw1"])
                s["cw2"] = int(new_marks["cw2"])
                s["cw3"] = int(new_marks["cw3"])
                s["exam"] = int(new_marks["exam"])
            except:
                messagebox.showerror("Error", "Invalid input.")
                return

            if not (0 <= s["cw1"] <= 20 and 0 <= s["cw2"] <= 20 and 0 <= s["cw3"] <= 20 and 0 <= s["exam"] <= 100):
                messagebox.showerror("Error", "Marks out of range.")
                return

            cw_total, overall, percent, grade = calculate_marks(
                s["cw1"], s["cw2"], s["cw3"], s["exam"]
            )
            s.update({
                "cw_total": cw_total,
                "overall": overall,
                "percentage": percent,
                "grade": grade
            })

            save_students(students)
            messagebox.showinfo("Updated", "Record updated.")
            return

    messagebox.showerror("Error", "Student not found.")

def show_statistics():
    students = load_students()
    if not students:
        return

    count = len(students)
    avg = round(sum(s["percentage"] for s in students) / count, 2)
    highest = max(students, key=lambda s: s["percentage"])
    lowest = min(students, key=lambda s: s["percentage"])

    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for s in students:
        grade_counts[s["grade"]] += 1

    max_count = max(grade_counts.values()) if grade_counts else 1

    chart = ""
    for g in ["A", "B", "C", "D", "F"]:
        bar_length = int((grade_counts[g] / max_count) * 20) if max_count > 0 else 0
        chart += f"{g}: ({grade_counts[g]})\n"
        
    text = (
        f"Total Students: {count}\n"
        f"Average Percentage: {avg}%\n"
        f"\nHighest Performer: {highest['name']} ({highest['percentage']}%)\n"
        f"Lowest Performer: {lowest['name']} ({lowest['percentage']}%)\n"
        f"\nGrade Distribution:\n{chart}"
    )

    show_scroll("Class Statistics", text)

root = tk.Tk()
root.title("Student Manager – Exercise 3")
root.geometry("480x550")
root.config(bg="#f2f2f2")

title = tk.Label(root, text="Student Manager", font=("Segoe UI", 20, "bold"), bg="#f2f2f2")
title.pack(pady=20)

def menu_btn(text, cmd):
    btn = tk.Button(
        root, text=text, font=("Segoe UI", 12),
        width=25, height=1, bg="white", bd=2, relief="raised",
        command=cmd
    )

    def on_enter(e):
        btn.config(bg="#e6f2ff")

    def on_leave(e):
        btn.config(bg="white")

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn

menu_btn("1. View All Records", view_all).pack(pady=5)
menu_btn("2. View Individual Record", view_individual).pack(pady=5)
menu_btn("3. Highest Mark", show_highest).pack(pady=5)
menu_btn("4. Lowest Mark", show_lowest).pack(pady=5)
menu_btn("5. Sort Records", sort_records).pack(pady=5)
menu_btn("6. Add Student", add_student).pack(pady=5)
menu_btn("7. Delete Student", delete_student).pack(pady=5)
menu_btn("8. Update Student", update_student).pack(pady=5)
menu_btn("9. Class Statistics", show_statistics).pack(pady=5)

root.mainloop()


