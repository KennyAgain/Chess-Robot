from heapq import heappush, heappop
from math import inf
from collections import deque
import serial
import serial.tools.list_ports
import json
import time

def __init__():
    global ser
    ser = find_esp32()
    time.sleep(1)
    ser.write("Engine Init\n".encode("utf-8"))


def find_esp32(baudrate=115200):
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "CH340" in p.description:  # looks for the CH340 USB-Serial chip
            print(f"Found ESP32 on port {p.device}")
            return serial.Serial(p.device, baudrate)
    raise Exception("ESP32 not found")

def Neighbors(board, pos):
    """8-way neighbors inside bounds. Does NOT filter by value."""
    rows, cols = len(board), len(board[0])
    x, y = pos
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue  # skip the current cell
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                yield nx, ny

def NearestFreeSquare(board, start,path):
    """
    Returns the nearest free square to `start`.
    If unavoidable, allows crossing non-zero cells.
    Returns (position, cost), where cost = # of crossed non-zero cells.
    """
    queue = deque([(start, 0)])  # (position, cost)
    visited = {start: 0}  # position -> minimal cost seen

    best = None
    best_cost = float('inf')

    while queue:
        (x, y), cost = queue.popleft()

        if board[x][y] == 0 and cost <= best_cost:
            best = (x, y)
            best_cost = cost

        for nx, ny in Neighbors(board, (x, y)):
            new_cost = cost + (1 if board[nx][ny] != 0 else 0)
            if ((nx, ny) not in visited or new_cost < visited[(nx, ny)] ) and not (nx,ny) in path:
                visited[(nx, ny)] = new_cost
                if board[nx][ny] == 0:
                    queue.appendleft(((nx, ny), new_cost))
                else:
                    queue.append(((nx, ny), new_cost))

    if best is None:
        return None, float('inf')
    return best, best_cost


def SearchShortestPath(board, start, target):
    """
    Returns (found, path, cost)
    cost = number of non-zero cells traversed (excluding start if start is nonzero you may adjust).
    Non-zero cells are allowed but cost +1. Cells with value -1 are treated as impassable here;
    change that check if your board uses a different impassable marker.
    Primary objective: minimize cost. Secondary: minimize steps.
    """
    if start == target:
        return [start], 0

    heap = []  # entries: (cost, steps, (x,y), path)
    heappush(heap, (0, 0, start, [start]))
    best = {start: (0, 0)}  # maps pos -> (best_cost, best_steps)

    while heap:
        cost, steps, pos, path = heappop(heap)

        # stale entry check
        if best.get(pos, (inf, inf)) < (cost, steps):
            continue

        if pos == target:
            return path, cost

        for nx, ny in Neighbors(board, pos):
            if board[nx][ny] == -1:     # treat -1 as impassable; change if needed
                continue

            add = 1 if board[nx][ny] != 0 else 0
            nc = cost + add
            ns = steps + 1
            npos = (nx, ny)

            if npos not in best or (nc, ns) < best[npos]:
                best[npos] = (nc, ns)
                heappush(heap, (nc, ns, npos, path + [npos]))

    return [], inf



def GenerateMovementPath(board,start,end):
    FinalPath = []

    Secondary_path = []

    #Checks if there is a direct path and returns it
    Primary_path, Primary_cost = SearchShortestPath(board,start,end) 
    print(f"path found: {Primary_path}")
    if Primary_path == 0: return Primary_path

    for (x,y) in Primary_path:
        if board[x][y] > 0 and (x,y) != start:
            best, best_cost = NearestFreeSquare(board,(x,y),Primary_path)
            print(best)
            print(f"Piece in the way at x: {x} and y: {y}")

            Secondary_path, Secondary_cost = SearchShortestPath(board,(x,y),best) #generate path for piece in the way

            print(f"Secondary Path found: {Secondary_path}")
    

    # If there is a secondary path, execute it first
    if Secondary_path:
        FinalPath = Secondary_path.copy()
        FinalPath.insert(1, (-2,-2))  # marker after first move
        FinalPath.append((-1,-1))  # end marker

    # Append primary path
    primary_start_index = len(FinalPath)
    FinalPath += Primary_path
    FinalPath.insert(primary_start_index + 1, (-2,-2))  # marker after first move
    FinalPath.append((-1,-1))  # end marker

    # If secondary path was executed, undo it
    if Secondary_path:
        rev_start_index = len(FinalPath)
        FinalPath += list(reversed(Secondary_path))
        FinalPath.insert(rev_start_index + 1, (-2,-2))  # marker after first move of reversed path
        FinalPath.append((-1,-1))

    return FinalPath

def GetMove():
    pass

def Move(board,start,target):
    global ser
    FinalPath = str(GenerateMovementPath(board, start, target)) + '\n'

    FinalPath = FinalPath.replace("(","[")
    FinalPath = FinalPath.replace(")","]")

    print(f"Final Path: {FinalPath.strip()}")
    ser.write(FinalPath.encode('utf-8'))

    time.sleep(0.1)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8')  # read all available bytes
        print(f"ESP Feedback: {response}")
    else:
        print("No response from ESP")
    


# ------------------ TEST ------------------
# board = [
#     [0, 0, 1],
#     [1, 1, 1],
#     [0, 0, 0]
# ]

# start = (0, 0)
# target = (2, 2)

# found, path, cost = 
#print(f"Final Path: {GenerateMovementPath(board, start, target)}")
# print("Found:", found)
# print("Path:", path)
# print("Cost:", cost)