# =====================================================
# Project: Bath Spa University BSc Cybersecurity - Student Manager
# Author: Farwa Batool
# Module: CodeLab II – Programming Skills Portfolio
# =====================================================
# References:
# - ChatGPT (Prompt: Create Python Tkinter Student Manager)
# - Python Docs: https://docs.python.org/3/library/tkinter.html
# =====================================================

import tkinter as tk
from tkinter import messagebox, simpledialog

FILE_NAME = "studentMarks.txt"

# ----------------------------
# Helper Functions
# ----------------------------

def get_grade(percentage):
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


def load_students():
    students = []
    try:
        with open(FILE_NAME, "r") as f:
            lines = f.readlines()
            for line in lines[1:]:  # skip first line (number of students)
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) < 8:
                    print(f"Skipping malformed line: {line}")
                    continue
                try:
                    student = {
                        "id": parts[0].strip(),
                        "name": parts[1].strip(),
                        "AI": int(parts[2]),
                        "CodeLab": int(parts[3]),
                        "CyberRes": int(parts[4]),
                        "Total": int(parts[5]),
                        "Percentage": float(parts[6]),
                        "Grade": parts[7].strip()
                    }
                    students.append(student)
                except ValueError:
                    print(f"Skipping line with invalid numbers: {line}")
                    continue
    except FileNotFoundError:
        messagebox.showerror("Error", f"{FILE_NAME} not found!")
    return students


def save_students(students):
    with open(FILE_NAME, "w") as f:
        f.write(f"{len(students)}\n")
        for s in students:
            line = f"{s['id']},{s['name']},{s['AI']},{s['CodeLab']},{s['CyberRes']},{s['Total']},{s['Percentage']},{s['Grade']}\n"
            f.write(line)


def display_students(students):
    output = ""
    for s in students:
        output += f"Student Name: {s['name']}\n"
        output += f"Student Number: {s['id']}\n"
        output += f"AI: {s['AI']}, Code Lab 2: {s['CodeLab']}, Cyber Resilience: {s['CyberRes']}\n"
        output += f"Total Marks: {s['Total']}, Percentage: {s['Percentage']}%, Grade: {s['Grade']}\n"
        output += "-"*40 + "\n"
    if students:
        avg_percentage = round(sum(s['Percentage'] for s in students)/len(students), 2)
        output += f"Number of Students: {len(students)}\nAverage Percentage: {avg_percentage}%\n"
    return output

# ----------------------------
# GUI Functions
# ----------------------------

def view_all():
    students = load_students()
    messagebox.showinfo("All Student Records", display_students(students))


def view_individual():
    students = load_students()
    student_id = simpledialog.askstring("Input", "Enter Student Number:")
    found = [s for s in students if s['id'] == student_id]
    if found:
        messagebox.showinfo("Student Record", display_students(found))
    else:
        messagebox.showerror("Error", "Student not found!")


def show_highest():
    students = load_students()
    if not students:
        messagebox.showinfo("Info", "No student data available.")
        return
    student = max(students, key=lambda x: x['Total'])
    messagebox.showinfo("Highest Total Marks", display_students([student]))


def show_lowest():
    students = load_students()
    if not students:
        messagebox.showinfo("Info", "No student data available.")
        return
    student = min(students, key=lambda x: x['Total'])
    messagebox.showinfo("Lowest Total Marks", display_students([student]))


def add_student():
    students = load_students()
    student_id = simpledialog.askstring("Input", "Enter Student Number:")
    student_name = simpledialog.askstring("Input", "Enter Student Name:")
    AI = int(simpledialog.askstring("Input", "Enter AI Marks:"))
    CodeLab = int(simpledialog.askstring("Input", "Enter Code Lab 2 Marks:"))
    CyberRes = int(simpledialog.askstring("Input", "Enter Cyber Resilience Marks:"))
    total = AI + CodeLab + CyberRes
    percentage = round(total / 300 * 100, 2)
    grade = get_grade(percentage)
    students.append({"id": student_id, "name": student_name, "AI": AI, "CodeLab": CodeLab, "CyberRes": CyberRes, "Total": total, "Percentage": percentage, "Grade": grade})
    save_students(students)
    messagebox.showinfo("Success", "Student added successfully!")


def delete_student():
    students = load_students()
    student_id = simpledialog.askstring("Input", "Enter Student Number to Delete:")
    new_students = [s for s in students if s['id'] != student_id]
    if len(new_students) == len(students):
        messagebox.showerror("Error", "Student not found!")
    else:
        save_students(new_students)
        messagebox.showinfo("Success", "Student deleted successfully!")


def update_student():
    students = load_students()
    student_id = simpledialog.askstring("Input", "Enter Student Number to Update:")
    for s in students:
        if s['id'] == student_id:
            AI = int(simpledialog.askstring("Input", f"Enter new AI Marks ({s['AI']}):"))
            CodeLab = int(simpledialog.askstring("Input", f"Enter new Code Lab 2 Marks ({s['CodeLab']}):"))
            CyberRes = int(simpledialog.askstring("Input", f"Enter new Cyber Resilience Marks ({s['CyberRes']}):"))
            total = AI + CodeLab + CyberRes
            percentage = round(total / 300 * 100, 2)
            grade = get_grade(percentage)
            s.update({"AI": AI, "CodeLab": CodeLab, "CyberRes": CyberRes, "Total": total, "Percentage": percentage, "Grade": grade})
            save_students(students)
            messagebox.showinfo("Success", "Student updated successfully!")
            return
    messagebox.showerror("Error", "Student not found!")


def sort_students():
    students = load_students()
    order = simpledialog.askstring("Input", "Enter 'asc' for ascending or 'desc' for descending sort by total marks:")
    if order.lower() == 'asc':
        students.sort(key=lambda x: x['Total'])
    elif order.lower() == 'desc':
        students.sort(key=lambda x: x['Total'], reverse=True)
    else:
        messagebox.showerror("Error", "Invalid input")
        return
    messagebox.showinfo("Sorted Students", display_students(students))

# ----------------------------
# GUI Setup
# ----------------------------

root = tk.Tk()
root.title("Bath Spa University - Student Manager")
root.geometry("500x300")

menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Menu", menu=file_menu)
file_menu.add_command(label="View All Students", command=view_all)
file_menu.add_command(label="View Individual Student", command=view_individual)
file_menu.add_command(label="Show Highest Total", command=show_highest)
file_menu.add_command(label="Show Lowest Total", command=show_lowest)
file_menu.add_separator()
file_menu.add_command(label="Add Student", command=add_student)
file_menu.add_command(label="Delete Student", command=delete_student)
file_menu.add_command(label="Update Student", command=update_student)
file_menu.add_command(label="Sort Students", command=sort_students)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)

root.mainloop()
