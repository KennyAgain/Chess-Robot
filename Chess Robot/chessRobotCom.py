from heapq import heappush, heappop
from math import inf
from collections import deque
import serial
import serial.tools.list_ports
import json
import time
import heapq

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
    """4-way neighbors inside bounds. Does NOT filter by value."""
    rows, cols = len(board), len(board[0])
    x, y = pos
    for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                yield nx, ny




def FindNearestFreeSquare(board, start,path):
    board_size = len(board)
    queue = deque([start])
    visited = {start}

    while queue:
        x, y = queue.popleft()

        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            nx, ny = x + dx, y + dy

            if 0 <= nx < board_size and 0 <= ny < board_size:
                if (nx, ny) in visited:
                    continue

                visited.add((nx, ny))

                if board[nx][ny] == 0:
                    queue.append((nx, ny))
                    if not (nx,ny) in path:
                        return (nx, ny)

    return None


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

    Secondary_paths = []

    #Checks if there is a direct path and returns it
    Primary_path, _ = SearchShortestPath(board,start,end) 
    print(f"path found: {Primary_path}")
    if Primary_path == 0: return Primary_path

    for (x,y) in Primary_path:
        if board[x][y] > 0 and (x,y) != start:
            best = FindNearestFreeSquare(board,(x,y),Primary_path + Secondary_paths)
            print(best)
            print(f"Piece in the way at x: {x} and y: {y} for Secondary_path")

            path, _ = SearchShortestPath(board,(x,y),best) #generate path for piece in the way
            Secondary_paths.append(path)

            print(f"Avodiance Path found: {path}")


    # If there is a secondary path, execute it first
    for sec_path in Secondary_paths:

        markerd_sec_path = sec_path.copy() #copy the path array
        markerd_sec_path.insert(1, (-2,-2))# marker after first move
        markerd_sec_path.append((-1,-1))  # end marker

        FinalPath += markerd_sec_path

    # Append primary path
    primary_start_index = len(FinalPath)
    FinalPath += Primary_path
    FinalPath.insert(primary_start_index + 1, (-2,-2))  # marker after first move
    FinalPath.append((-1,-1))  # end marker

    # If secondary path was executed, undo it
    for sec_path in Secondary_paths:

        markerd_sec_path = sec_path.copy() #copy the path array
        markerd_sec_path = list(reversed(markerd_sec_path)) #reverse the moves
        markerd_sec_path.insert(1, (-2,-2))# marker at the start of the array
        markerd_sec_path.append((-1,-1)) #pickup marker at the end of the array
    
        FinalPath += markerd_sec_path
        
    return FinalPath

def GetMove():
    pass

#TODO 
#Also give the robot the info if the move is a travel or not
#

def Move(board,start,target):
    #global ser
    FinalPath = str(GenerateMovementPath(board, start, target)) + '\n'

    FinalPath = FinalPath.replace("(","[")
    FinalPath = FinalPath.replace(")","]")

    print(f"Final Path: {FinalPath.strip()}")
    ser.write(FinalPath.encode('utf-8'))

    time.sleep(0.1)

    ser.write("Parsed\n".encode('utf-8'))

    time.sleep(0.1)

    ser.write("KeepAlive\n".encode('utf-8'))




def CheckResponse():
    while ser.in_waiting > 0:
        try:
            response = ser.read(ser.in_waiting).decode('utf-8')  # read all available bytes
            print(f"ESP Feedback: {response}")
        except:
            print("An error occured while reading the esps response")
    


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