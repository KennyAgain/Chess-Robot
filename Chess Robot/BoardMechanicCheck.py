import tkinter as tk
import serial
import serial.tools.list_ports
import time

BOARD_SIZE = 8
SQUARE_SIZE = 60
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE


def find_esp32(baudrate=115200):
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "CH340" in p.description:
            print(f"Found ESP32 on port {p.device}")
            return serial.Serial(p.device, baudrate, timeout=1)
    raise Exception("ESP32 not found")


def on_square_clicked(x, y):
    global ser

    y = 7 - y

    message = f"[[{x},{y}]]\n"
    print(f"Sending: {message.strip()}")
    ser.write(message.encode("utf-8"))


def MagnetOn():
    global ser
    print("Magnet ON")
    ser.write("[[-2,-2]]\n".encode("utf-8"))


def MagnetOff():
    global ser
    print("Magnet OFF")
    ser.write("[[-1,-1]]\n".encode("utf-8"))


def CenterPieces():
    path = []
    for x in range(8):
        for y in range(8):
            path.append([x,y])
            path.append([-2,-2])
            path.append([-1,-1])
    
    ser.write((str(path) + "\n").encode("utf-8"))


def draw_board(canvas):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x1 = col * SQUARE_SIZE
            y1 = row * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE

            color = "white" if (row + col) % 2 == 0 else "gray"
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")


def canvas_click(event):
    col = event.x // SQUARE_SIZE
    row = event.y // SQUARE_SIZE

    if 0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE:
        x = col
        y = BOARD_SIZE - 1 - row  # single Y flip (correct)
        on_square_clicked(x, y)


# ---- SERIAL INIT ----
ser = find_esp32()
time.sleep(1)
ser.write("Engine Init\n".encode("utf-8"))

# ---- GUI ----
root = tk.Tk()
root.title("Chess Board Input")

canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE)
canvas.pack()

draw_board(canvas)
canvas.bind("<Button-1>", canvas_click)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn1 = tk.Button(button_frame, text="Magnet On", command=MagnetOn)
btn1.pack(side=tk.LEFT, padx=5)

btn2 = tk.Button(button_frame, text="Magnet Off", command=MagnetOff)
btn2.pack(side=tk.LEFT, padx=5)

btn3= tk.Button(button_frame, text="Center Pieces", command=CenterPieces)
btn3.pack(side=tk.LEFT, padx=5)

root.mainloop()
