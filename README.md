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
You may run multiple clients and see the moves you make in one board be reflected in another board.
Once a game is completed (either a tie or a win), you can go into File -> Play Again to reset the board.
