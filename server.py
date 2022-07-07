import asyncio
import websockets
import json

import game
from game_elements import Move


async def handler(websocket):
    async for message in websocket:
        # Parse events from the client.
        event = json.loads(message)
        response = {}
        match event["type"]:
            case "connect":
                # Sends the information required to initialize a board.
                response = {
                            "type": "start_game",
                            "board_data":
                                    {
                                        "current_player":
                                            ttt_game.current_player,
                                        "board_size":
                                            ttt_game.board_size
                                    }
                            }
            case "move":
                move = Move(*event["move"])
                if ttt_game.is_valid_move(move):
                    ttt_game.process_move(move)
                    if ttt_game.is_tied():
                        response = {"type": "is_valid_move",
                                    "valid": True,
                                    "current_player": ttt_game.current_player,
                                    "game_status": "tie"}
                    elif ttt_game.has_winner():
                        response = {"type": "is_valid_move",
                                    "valid": True,
                                    "current_player": ttt_game.current_player,
                                    "game_status": "win"}
                    else:
                        ttt_game.toggle_player()
                        response = {"type": "is_valid_move",
                                    "valid": True,
                                    "current_player": ttt_game.current_player,
                                    "game_status": "running"}
                else:
                    response = {"type": "is_valid_move", "valid": False}
            case "restart":
                if ttt_game.is_tied() or ttt_game.has_winner():
                    ttt_game.reset_game()
                    response = {"type": "is_valid_restart",
                                "valid": True}
                else:
                    response = {"type": "is_valid_restart",
                                "valid": False}
            case _:
                # TODO: send an error!
                pass
        await websocket.send(json.dumps(response))
        print(message)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    ttt_game = game.TicTacToeGame()
    asyncio.run(main())
