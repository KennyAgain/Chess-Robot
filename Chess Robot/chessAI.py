import random
def Move(BoardState,ToMove,ValidMoves):

    if len(ValidMoves) > 0:
        Move = ValidMoves[random.randint(0,len(ValidMoves) - 1)]
    else:
        return (-1,-1),(-1,-1), True

    print(f"AI Move {Move}")

    Startsquare = Move[0]
    Endsquare = Move[1]

    return Startsquare, Endsquare, False