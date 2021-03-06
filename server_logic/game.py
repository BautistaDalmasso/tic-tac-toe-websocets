"""Controls the logic of a tic-tac-toe game."""

from itertools import cycle

from game_elements import Player, Move


BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="blue"),
    Player(label="O", color="green")
)


class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.all_players = players
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self.current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self._setup_board()
        self.running = False

    def _setup_board(self):
        self.current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [
            [(move.row, move.col) for move in row]
            for row in self.current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return (rows + columns + [first_diagonal, second_diagonal])

    def is_valid_move(self, move: Move) -> bool:
        row, col = move.row, move.col
        move_was_not_played = self.current_moves[row][col].label == ""
        return move_was_not_played and not self._has_winner

    def process_move(self, move: Move):
        """Process the current move and check if it's a win."""
        self.running = True
        row, col = move.row, move.col
        self.current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(
                self.current_moves[n][m].label
                for n, m in combo
            )
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break

    def has_winner(self) -> bool:
        return self._has_winner

    def is_tied(self) -> bool:
        played_moves = (
            move.label
            for row in self.current_moves
            for move in row
        )
        return all(played_moves) and not self._has_winner

    def toggle_player(self):
        self.current_player = next(self._players)

    def reset_game(self):
        self.running = False
        for row, row_content in enumerate(self.current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []
