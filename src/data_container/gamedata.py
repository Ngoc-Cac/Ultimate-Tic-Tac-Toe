from dataclasses import (
    dataclass,
    field
)

from GUI.tictactoe_board import (
    TicTacToe,
    UltimateTicTacToe
)

from typing import (
    Literal,
    Optional
)


@dataclass
class GameData():
    game: UltimateTicTacToe

    x_turn: bool = True
    current_board: Optional[tuple[int, int]] = None
    # previous state contains: previous position played, the previous board
    # that was played on
    prev_states: list[tuple[tuple[int, int], 'TicTacToe']] = field(default_factory=lambda: [])

    bot_goes_first: bool = True
    game_ongoing: bool = False
    gametype: Literal['Normal', 'Ultimate'] = 'Ultimate'
    gamemode: Literal['Human', 'Bot'] = 'Human'

    bot_algo: Literal['minimax', 'monte_carlo'] = 'monte_carlo'