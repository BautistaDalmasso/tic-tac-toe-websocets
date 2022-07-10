# tic-tac-toe-websocets
A simple tic-tac-toe game that utilizes websockets. I followed this tutorial for the base game logic and board: https://realpython.com/tic-tac-toe-python. 
After having the base game I added websockets to it.

## Getting Started
### Dependencies
Requires having the websockets python module installed.
### Executing program
First run the server:
```
python server.py
```
Then you can run the client in another command prompt:
```
python client.py
```
You need at least 2 clients running to play the game. The clients alternate their turns after each move.
Extra clients can be opened but they'll only be able to watch the moves the first two clients make.
If a board is spectating a match and one of the players leaves, you can go into File -> Request player to be
assigned the role of the player that left.
Once a game is completed (either a tie or a win), you can go into File -> Play Again to reset the board.
