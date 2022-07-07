"""A tic-tac-toe board built with TKinter."""

import tkinter as tk
from tkinter import font
import asyncio
import websockets
import json
from typing import List

from game_elements import Player, Move


class GameState:
    """Keeps track of the game state at the client side."""
    def __init__(self, board_size: int, current_player: Player,
                 current_moves: List[List[Move]]):
        self.board_size = board_size
        self.current_player = current_player
        self.current_moves = current_moves


class TicTacToeBoard(tk.Tk):
    def __init__(self, websocket, game_state: GameState) -> None:
        super().__init__()
        self.title("Tic-Tac-Toe")
        self._cells = {}
        self._ws = websocket
        self._game_state = game_state
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()

    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text=f"Ready {self._game_state.current_player.label}?",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack()

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        for row in range(self._game_state.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._game_state.board_size):
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
                button.bind("<ButtonPress-1>",
                            lambda event:
                            asyncio.ensure_future(self.play(event)))
                button.grid(
                    row=row,
                    column=col,
                    padx=5,
                    pady=5,
                    sticky="nsew",
                )
        self._set_buttons()

    def _set_buttons(self):
        for button, coordinates in self._cells.items():
            row, col = coordinates
            button.config(text=self._game_state.current_moves[row][col].label)

    async def play(self, event):
        """Handle a player's move."""
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        message = {"type": "move",
                   "move": Move(row, col,
                                self._game_state.current_player.label)}
        await self._ws.send(json.dumps(message))
        # Makes sure the move is valid:
        response = json.loads(await self._ws.recv())
        assert response["type"] == "is_valid_move"
        if response["valid"]:
            self._update_button(clicked_btn)
            self._game_state.current_player = Player(
                                                *response["current_player"])
            match response["game_status"]:
                case "tie":
                    self._update_display(msg="Tied game!", color="red")
                case "win":
                    msg = f'Player "{self._game_state.current_player.label}" won!'
                    color = self._game_state.current_player.color
                    self._update_display(msg, color)
                case "running":
                    msg = f"{self._game_state.current_player.label}'s turn"
                    self._update_display(msg)

    def _update_button(self, clicked_btn: tk.Button):
        clicked_btn.config(text=self._game_state.current_player.label)
        clicked_btn.config(foreground=self._game_state.current_player.color)

    def _update_display(self, msg: str, color: str = "black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(
            label="Play again",
            command=lambda: asyncio.ensure_future(self.reset_board())
        )
        menu_bar.add_cascade(label="File", menu=file_menu)

    async def reset_board(self):
        message = {"type": "restart"}
        await self._ws.send(json.dumps(message))

        # Checks if the game can be restarted.
        response = json.loads(await self._ws.recv())
        assert response["type"] == "is_valid_restart"

        if response["valid"]:
            msg = f"Ready {self._game_state.current_player.label}?"
            self._update_display(msg=msg)
            for button in self._cells.keys():
                button.config(highlightbackground="lightblue")
                button.config(text="")
                button.config(fg="black")


def handle_current_moves(response):
    board_size = response["board_data"]["board_size"]
    if response["already_started"]:
        board_state = response["board_data"]["board_state"]
        current_moves = [
            [Move(*board_state[row][col]) for col in range(board_size)]
            for row in range(board_size)
        ]
    else:
        current_moves = [
            [Move(row, col) for col in range(board_size)]
            for row in range(board_size)
        ]
    return current_moves


async def run_board(root):
    try:
        while True:
            root.update()
            await asyncio.sleep(.01)
    except tk.TclError as e:
        if "application has been destroyed" not in e.args[0]:
            raise


async def main():
    """Create the game's board and run its main loop."""
    async with websockets.connect("ws://localhost:8001") as websocket:
        # Tells the server that we want to start a new game.
        message = {"type": "connect"}
        await websocket.send(json.dumps(message))

        response = json.loads(await websocket.recv())
        # Makes sure the server's response corresponds to a
        # game starting request.
        assert response["type"] == "start_game"
        print(response)
        board_size = response["board_data"]["board_size"]
        current_player = Player(*response["board_data"]["current_player"])
        current_moves = handle_current_moves(response)
        game_state = GameState(board_size, current_player, current_moves)

        board = TicTacToeBoard(websocket, game_state)
        await run_board(board)


if __name__ == "__main__":
    asyncio.run(main())
