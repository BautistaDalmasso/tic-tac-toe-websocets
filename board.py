"""A tic-tac-toe board built with TKinter."""

import tkinter as tk
from tkinter import font

import game


class TicTacToeBoard(tk.Tk):
    def __init__(self, game: game.TicTacToeGame) -> None:
        super().__init__()
        self.title("Tic-Tac-Toe")
        self._cells = {}
        self._game = game
        self._create_board_display()
        self._create_board_grid()

    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text="Ready?",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack()

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=5,
                    height=2,
                    highlightbackground="lightblue",
                )
                self._cells[button] = (row, col)
                button.grid(
                    row=row,
                    column=col,
                    padx=5,
                    pady=5,
                    sticky="nsew",
                )

    def play(self, event):
        """Handle a player's move."""
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = game.Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._game.process_move(move)
            if self._game.is_tied():
                msg = "Tied game!"
                print(msg)
            elif self._game.has_winner():
                msg = f'Player "{self._game.current_player.label}" won!'
                print(msg)
            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.label}'s turn"
                print(msg)
