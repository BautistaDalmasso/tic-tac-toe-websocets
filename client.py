import json
import asyncio
import websockets
from tkinter import TclError

from game_elements import Player, Move
from client_logic.board import TicTacToeBoard, GameState


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


def handle_all_players(response):
    all_players = []
    for player in response["board_data"]["all_players"]:
        all_players.append(Player(*player))
    return all_players


def handle_assigned_player(response):
    if response["assigned_player"] == "SPECTATOR":
        return Player("SPECTATOR", "black")
    return Player(*response["assigned_player"])


async def run_board(root):
    try:
        while True:
            root.update()
            await asyncio.sleep(.01)
    except TclError as e:
        if "application has been destroyed" not in e.args[0]:
            raise


async def send_disconnect_request(websocket):
    await websocket.send(json.dumps({"type": "request_disconnect"}))


async def receive_message(websocket, board: TicTacToeBoard,
                          g_state: GameState):
    """Receives and handle messages from the server."""
    while True:
        message = json.loads(await websocket.recv())
        match message["type"]:
            case "is_valid_move":
                board.receive_move(message)
            case "is_valid_restart":
                board.receive_reset_order()
            case "player_request":
                g_state.assigned_player = message["assigned_player"]
            case "confirm_disconnect":
                break


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
        # Initializes a GameState according to the server's data.
        board_size = response["board_data"]["board_size"]
        # Player that has the current turn.
        current_player = Player(*response["board_data"]["current_player"])
        # Player that is assigned to the client.
        assigned_player = handle_assigned_player(response)
        all_players = handle_all_players(response)
        current_moves = handle_current_moves(response)
        game_state = GameState(board_size=board_size,
                               current_player=current_player,
                               assigned_player=assigned_player,
                               all_players=all_players,
                               current_moves=current_moves
                               )

        board = TicTacToeBoard(websocket, game_state)

        # Here we start running the game board.
        board_task = asyncio.create_task(
            run_board(board)
        )
        message_receiver_task = asyncio.create_task(
            receive_message(websocket, board, game_state)
        )
        board_task.add_done_callback(
            lambda _: asyncio.ensure_future(send_disconnect_request(websocket))
        )
        await board_task
        await message_receiver_task


if __name__ == "__main__":
    asyncio.run(main())
