"""A tic-tac-toe board built with TKinter."""

import tkinter as tk
from tkinter import font
import asyncio
import websockets
import json


class TicTacToeBoard(tk.Tk):
    def __init__(self, websocket) -> None:
        super().__init__()
        self.title("Tic-Tac-Toe")
        self._cells = {}
        self._ws = websocket
        self._create_menu()
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
        for row in range(3):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(3):
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

    async def play(self, event):
        """Handle a player's move."""
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        message = {"type": "move", "move": [row, col]}
        await self._ws.send(json.dumps(message))
        # TODO: handle state of the game.
        if False:
            self._update_button(clicked_btn)
            if self._game.is_tied():
                self._update_display(msg="Tied game!", color="red")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f'Player "{self._game.current_player.label}" won!'
                color = self._game.current_player.color
                self._update_display(msg, color)
            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.label}'s turn"
                self._update_display(msg)

    def _update_button(self, clicked_btn: tk.Button):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(foreground=self._game.current_player.color)

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
            command=self.reset_board
        )
        menu_bar.add_cascade(label="File", menu=file_menu)

    def reset_board(self):
        # TODO: allow reseting the game.
        self._update_display(msg="Ready?")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")


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
        board = TicTacToeBoard(websocket)
        await run_board(board)


if __name__ == "__main__":
    asyncio.run(main())
