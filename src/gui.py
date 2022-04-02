import tkinter as tk
from tkinter import messagebox
from puzzle15 import State, BNBTree
import numpy as np

# Kelas Exception untuk mempermudah validasi input


class InvalidInputException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


# Inisialisasi app
app = tk.Tk()
app.title("15 puzzle")
app.resizable(False, False)

# Title dari app
app_title = tk.Label(app, text="15 puzzle", font=("Helvetica", 20))
app_title.grid(row=0, column=0, columnspan=4)

# Frame puzzle
puzzlegrid = tk.Frame(app, width=300, height=300)
puzzlegrid.grid(row=1, column=0, padx=10, pady=10, columnspan=4, rowspan=3)
puzzlegrid.configure(background='#FFFFFF')

number = 1


def set_number(button_number):
  # Fungsi untuk memasukkan angka ke dalam puzzle
    global number, buttons
    if (buttons[button_number].cget('text') == '-' and number <= 16):
        buttons[button_number].configure(
            text=number if number < 16 else "-", bg="#FFFFFF", fg="#FFFFFF", state="disabled")
        number += 1


def reset_number():
  # Fungsi untuk menghapus angka dari puzzle
    global number, buttons
    number = 1
    app.after_cancel(cur_timer)
    for button in buttons:
        if button.cget('text') != '-':
            button.configure(text='-', bg="#FFFFFF",
                             fg="#000000", state="normal")


def import_number():
  # Fungsi untuk memasukkan angka dari text input ke puzzle
    global number, buttons, text_input, kurang_label_res
    try:
        res = []
        lines = text_input.get("1.0", "end-1c").strip().split("\n")
        if len(lines) != 4:
            raise InvalidInputException("Row must be 4")
        for line in lines:
            try:
                inp = [int(x) if x != "-" else 16 for x in line.split(" ")]
            except ValueError:
                raise InvalidInputException("Input must be number")
            if len(inp) != 4:
                raise InvalidInputException("Column must be 4")
            for i in inp:
                if i < 1 or i > 16:
                    raise InvalidInputException(
                        "Input must be between 1 and 16")
            res.append(inp)

        # Ubah input ke puzzle
        state = State(np.array(res))

        # Mendapatkan nilai Kurang(i)
        kurang = state.get_kurang()
        kurang_label_res.configure(
            text=str(sum(kurang.values()) + (sum(state.blank_index) % 2)[0]))
        kurangi_label_res.configure(
            text="\n".join(["{}\t=\t{}".format(k, v) for k, v in sorted(kurang.items(), key=lambda x: x[0])]))

        # Visualisasi State
        visualize_state(state)
        number = 17
    except InvalidInputException as e:
        messagebox.showerror("Invalid input", str(e))
        return


# Type casting state untuk visualisasi
tree = BNBTree
state = State
state_list = list
cur_timer = str
delay = int


def start_visualize():
  # Fungsi untuk memulai visualisasi
    global tree, state, buttons, state_list, cur_timer, number, delay, delay_input, time_label_res, expand_label_res, steps_label_res

    # Validasi Input
    delay = delay_input.get()
    if not delay.isdigit():
        messagebox.showerror("Invalid input", "Delay must be number")
        return
    delay = int(delay)
    if number < 17:
        messagebox.showerror("Invalid input", "Input must be full")
        return

    # Mendapatkan input dari puzzle
    board = [[], [], [], []]
    for (i, button) in enumerate(buttons):
        txt = button.cget('text')
        board[i//4].append(int(txt if txt.isdigit() else '16'))

    # Memasukkan input ke dalam state dan tree
    state = State(np.array(board))
    tree = BNBTree(state)

    # Mengecek apakah state dapat diselesaikan
    if tree.is_solvable():
        app.after_cancel(cur_timer)
        # Melakukan Search
        tree.search()
        time_label_res.configure(text="{:.3f}".format(tree.search_time))
        expand_label_res.configure(text=str(tree.expanded_nodes_count))
        state_list = tree.route
        steps_label_res.configure(text=str(len(state_list) - 2))
        next()
    else:
        messagebox.showerror("Invalid", "The puzzle is not solvable")
        return


def next():
  # Fungsi untuk mengubah state ke state berikutnya
    global cur_timer, state, state_list, delay
    if (state.is_goal or len(state_list) == 0):
        return
    state = state_list.pop()
    visualize_state(state)
    cur_timer = app.after(delay, lambda: next())


def visualize_state(state: State):
  # Fungsi untuk menampilkan state ke dalam puzzle
    global buttons
    for i in range(len(buttons)):
        num = state.board[i//4][i % 4]
        buttons[i].configure(text=num if num < 16 else "-",
                             bg="#FFFFFF", fg="#000000", state="disabled")


# Puzzle Buttons
buttons = []
for i in range(16):
    buttons.append(tk.Button(puzzlegrid, text='-', command=lambda x=i: set_number(x),
                   width=5, height=2, bg="#FFFFFF", fg="#000000"))
for i, button in enumerate(buttons):
    button.grid(row=int(i/4), column=i % 4)

# Reset Button
reset_button = tk.Button(app, text="Reset", width=5,
                         height=2, command=reset_number)
reset_button.grid(row=4, column=0, pady=10)

# Delay Input
delay_input = tk.Entry(app, width=5, )
delay_input.grid(row=4, column=2, pady=10)
delay_input.insert(-1, "100")

# Delay Label
delay_label = tk.Label(app, text="Delay (ms)")
delay_label.grid(row=4, column=3, pady=10)

# State Input Label
input_label = tk.Label(
    app, text="Input state:\n(Insert numbers separated by space)")
input_label.grid(row=0, column=4, pady=(5, 0))

# State Input
text_input = tk.Text(app, width=18, height=6)
text_input.configure(font=("Helvetica", 10))
text_input.grid(row=1, column=4, rowspan=1, pady=(5, 0), padx=(0, 10))

# Result Frame
result_frame = tk.Frame(app)
result_frame.grid(row=2, column=4, rowspan=1, pady=(5, 0), padx=(0, 10))

# Time Label
time_label = tk.Label(result_frame, text="Time (s)\t\t\t:")
time_label.grid(row=0, column=0)

# Time Result
time_label_res = tk.Label(result_frame, text="-")
time_label_res.grid(row=0, column=1)

# Kurang Label
kurang_label = tk.Label(result_frame, text="SUM(KURANG(i)) + X\t:")
kurang_label.grid(row=1, column=0)

# Kurang Result
kurang_label_res = tk.Label(result_frame, text="-")
kurang_label_res.grid(row=1, column=1)

# Expanded Label
expand_label = tk.Label(result_frame, text="Expanded nodes\t\t:")
expand_label.grid(row=2, column=0)

# Expanded Result
expand_label_res = tk.Label(result_frame, text="-")
expand_label_res.grid(row=2, column=1)

# Steps Label
steps_label = tk.Label(result_frame, text="Steps\t\t\t:")
steps_label.grid(row=3, column=0)

# Steps Result
steps_label_res = tk.Label(result_frame, text="-")
steps_label_res.grid(row=3, column=1)

# Button Frame
button_frame = tk.Frame(app)
button_frame.grid(row=4, column=4)

# Visualize Button
visualize_button = tk.Button(
    button_frame, text="Visualize", width=10, height=2, command=start_visualize)
visualize_button.grid(row=4, column=4, pady=10, padx=4)

# Import Button
import_button = tk.Button(button_frame, text="Import", width=10,
                          height=2, command=import_number)
import_button.grid(row=4, column=5, pady=10, padx=4)

# Kurang(i) Label
kurangi_label = tk.Label(app, text="Nilai Dari KURANG(i)", width=20)
kurangi_label.grid(row=0, column=5)

# Kurang(i) Result
kurangi_label_res = tk.Label(app, text="-")
kurangi_label_res.grid(row=1, column=5, rowspan=5)

app.mainloop()
