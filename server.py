import asyncio
import websockets
import json

from server_logic.game import TicTacToeGame
from game_elements import Move, Player


CONNECTIONS = {}


async def register(websocket):
    # Assigns a player to the connecting client.
    client_player = get_available_player()
    # Adds the connected websocket to connections.
    CONNECTIONS[websocket] = client_player
    try:
        handler_task = asyncio.create_task(handler(websocket))
        wait_closed_task = asyncio.create_task(websocket.wait_closed())
        await handler_task
        await wait_closed_task
    finally:
        # Releases the player used by the disconnecting client.
        if CONNECTIONS[websocket] != "SPECTATOR":
            available_players.append(CONNECTIONS[websocket])
        del CONNECTIONS[websocket]


async def handler(websocket):
    async for message in websocket:
        # Parse events from the client.
        event = json.loads(message)
        response = {}
        match event["type"]:
            case "connect":
                # Sends the information required to initialize a board.
                response = handle_connection_response(CONNECTIONS[websocket])
                await websocket.send(json.dumps(response))
            case "move":
                move = Move(*event["move"])
                if (ttt_game.is_valid_move(move)
                        and CONNECTIONS[websocket] == ttt_game.current_player):
                    ttt_game.process_move(move)
                    if ttt_game.is_tied():
                        response = {"type": "is_valid_move",
                                    "move": move,
                                    "current_player": ttt_game.current_player,
                                    "game_status": "tie"}
                    elif ttt_game.has_winner():
                        response = {"type": "is_valid_move",
                                    "move": move,
                                    "current_player": ttt_game.current_player,
                                    "game_status": "win"}
                    else:
                        # Only toggle the player when the game has to
                        # keep running.
                        ttt_game.toggle_player()
                        response = {"type": "is_valid_move",
                                    "move": move,
                                    "current_player": ttt_game.current_player,
                                    "game_status": "running"}
                    websockets.broadcast(CONNECTIONS, json.dumps(response))
            case "restart":
                # Only allow restarting the game when it's finished.
                if ttt_game.is_tied() or ttt_game.has_winner():
                    ttt_game.reset_game()
                    response = {"type": "is_valid_restart"}
                    websockets.broadcast(CONNECTIONS, json.dumps(response))
            case "request_disconnect":
                await websocket.send(json.dumps(
                                    {"type": "confirm_disconnect"}))


def handle_connection_response(assigned_player: Player):
    # Creates the response with all the information necessary to initialize
    # a board.
    response = {
            "type": "start_game",
            "already_started": ttt_game.running,
            "board_data":
                    {
                        "current_player":
                            ttt_game.current_player,
                        "board_size":
                            ttt_game.board_size,
                        "all_players":
                            ttt_game.all_players
                    },
            "assigned_player": assigned_player
            }
    # If the game already started then send information
    # about the entire board.
    if response["already_started"]:
        response["board_data"]["board_state"] = ttt_game.current_moves

    return response


def get_available_player():
    # Allows us to assign a specific player to the client.
    if len(available_players) > 0:
        client_player = available_players.pop(0)
    else:
        client_player = "SPECTATOR"

    return client_player


async def main():
    async with websockets.serve(register, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    ttt_game = TicTacToeGame()
    available_players = [*ttt_game.all_players]
    asyncio.run(main())
