import asyncio
import websockets
import json

import game


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
                print(event)
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
