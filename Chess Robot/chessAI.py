import random
import chessCore

import cProfile
import pstats


class Random_Ai:
    @staticmethod
    def Move(BoardState, ToMove, ValidMoves):
        move = random.choice(ValidMoves)
        print(f"AI Move {move}")
        return move[0], move[1]


class Simple_AI:

    # Transposition Table: key -> (score, best_index, depth_searched)
    TT = {}

    @staticmethod
    def Eval(BoardState):
        """Evaluation from White's perspective (+ good for White, - good for Black)."""
        score = 0

        # Check bonuses first (only once each)
        if chessCore.InCheck(BoardState, "b"):
            score += 5
        if chessCore.InCheck(BoardState, "w"):
            score -= 5

        mat_values = chessCore.MaterialValue
        get_color = chessCore.GetPieceColor

        for row in BoardState:
            for piece in row:
                if piece:
                    val = mat_values[piece]
                    if get_color(piece) == "w":
                        score += val
                    else:
                        score -= val
        return score

    @staticmethod
    def quick_move_score(move, BoardState, ToMove):
        """Only capture scoring (no expensive InCheck calls here)."""
        (sx, sy), (ex, ey) = move
        attacker = BoardState[sx][sy]
        victim   = BoardState[ex][ey]

        if victim:
            return (chessCore.MaterialValue[victim] * 10) - chessCore.MaterialValue[attacker]
        return 0

    @staticmethod
    def Move(BoardState, ToMove, ValidMoves, depth=3):
        eval, BestEvalIndex = Simple_AI.Search(BoardState, ToMove, ValidMoves, depth, -999999, 999999)
        print(f"Best Eval {eval}")
        best_move = ValidMoves[BestEvalIndex]
        print(f"AI Move {best_move}")
        return best_move[0], best_move[1]

    @staticmethod
    def Search(BoardState, ToMove, ValidMoves, depth, alpha, beta):
        # --- Transposition Table lookup ---
        key = (tuple(map(tuple, BoardState)), ToMove, depth, alpha, beta)
        if key in Simple_AI.TT:
            return Simple_AI.TT[key]

        # Game over detection first
        if not ValidMoves:
            if chessCore.InCheck(BoardState, ToMove):
                if ToMove == "w":
                    return -99999 - depth, None  # Black wins
                else:
                    return 99999 + depth, None   # White wins
            else:
                return 0, None  # Stalemate

        if depth == 0:
            return Simple_AI.Eval(BoardState), None

        is_white = ToMove == "w"
        BestEval = -99999 if is_white else 99999
        BestEvalIndex = 0

        # Move ordering
        ValidMoves.sort(
            key=lambda m: Simple_AI.quick_move_score(m, BoardState, ToMove),
            reverse=True
        )

        next_color = "b" if is_white else "w"
        for index, Move in enumerate(ValidMoves):
            (sx, sy), (ex, ey) = Move
            attacker = BoardState[sx][sy]
            captured = BoardState[ex][ey]

            # Make move in-place
            BoardState[ex][ey] = attacker
            BoardState[sx][sy] = 0

            next_moves = chessCore.ValidMoves(BoardState, next_color)
            score, _ = Simple_AI.Search(BoardState, next_color, next_moves, depth - 1, alpha, beta)

            # Undo move
            BoardState[sx][sy] = attacker
            BoardState[ex][ey] = captured

            if is_white:  # maximizing
                if score > BestEval:
                    BestEval = score
                    BestEvalIndex = index
                alpha = max(alpha, BestEval)
                if alpha >= beta:
                    break
            else:  # minimizing
                if score < BestEval:
                    BestEval = score
                    BestEvalIndex = index
                beta = min(beta, BestEval)
                if alpha >= beta:
                    break

        result = (BestEval, BestEvalIndex)
        # --- Store in TT ---
        Simple_AI.TT[key] = result
        return result
if __name__ == "__main__":
    import cProfile, pstats
    import chessCore  # make sure your chessCore import works here
    chessCore.__init__()

    # --- setup a board position ---
    board ,to_move= chessCore.Readfen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    valid_moves = chessCore.ValidMoves(board, to_move)

    # --- run profiler ---
    def run_ai():
        Simple_AI.Move(board, to_move, valid_moves, depth=3)

    cProfile.run("run_ai()", "profile.out")
    p = pstats.Stats("profile.out")
    p.sort_stats("cumulative").print_stats(20)
