"""Objects of the Tic-Tac-Toe game that are used in both server and
client sides."""

from typing import NamedTuple


class Player(NamedTuple):
    label: str
    color: str


class Move(NamedTuple):
    row: int
    col: int
    label: str = ""
