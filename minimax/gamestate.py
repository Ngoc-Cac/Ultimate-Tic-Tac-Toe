from copy import deepcopy

from typing import TypeAlias, Union, Literal, Optional


PlayerCharacter: TypeAlias = Literal['X', 'O']
TicTacToeBoard: TypeAlias = list[list[PlayerCharacter | Literal[' ']]]
UltimateTicTacToeBoard: TypeAlias = list[list[PlayerCharacter | Literal[' ', 'T']]]

NumericType: TypeAlias = Union[int, float]


EMPTY_CHAR: str = ' '
MAX_SCORE: int = 1000
TIE_SCORE: int = 1000
def get_winner(board: TicTacToeBoard | UltimateTicTacToeBoard) -> Optional[PlayerCharacter]:
    main_diag = []
    sub_diag = []
    for i, row in enumerate(board):
        # rows
        row_alias = set(row)
        if (len(row_alias) == 1) and\
           (not EMPTY_CHAR in row_alias) and\
           (not 'T' in row_alias):
            return row_alias.pop()
        # cols
        col = set(cell[i] for cell in board)
        if (len(col) == 1) and\
           (not EMPTY_CHAR in col) and\
           (not 'T' in col):
            return col.pop()

        main_diag.append(row[i])
        sub_diag.append(board[2 - i][i])

    main_diag = set(main_diag)
    sub_diag = set(sub_diag)
    if (len(main_diag) == 1) and\
       (not EMPTY_CHAR in main_diag) and\
       (not 'T' in main_diag):
        return main_diag.pop()
    if (len(sub_diag) == 1) and\
       (not EMPTY_CHAR in sub_diag) and\
       (not 'T' in sub_diag):
        return sub_diag.pop()
    # tie or game has not ended
    return None

class GameState():
    __slots__ = '_board_state', '_play_char', '_free_cells', '_previous_move', '_max_player'
    def __init__(self, board_state: TicTacToeBoard,
                 player_char: PlayerCharacter,
                 max_player: PlayerCharacter,
                 # previous_move: Optional[tuple[int, int]]
                 # free_cells: Optional[set[tuple[int, int]]]
                 **kwargs):
        # Type check stuff please

        self._board_state = board_state
        self._play_char = player_char
        self._max_player = max_player
        self._previous_move = kwargs['previous_move'] if 'previous_move' in kwargs else None

        free_cells = kwargs['free_cells'] if 'free_cells' in kwargs else None

        if free_cells is None:
            self._free_cells = set((i, j) for i, row in enumerate(self._board_state)
                                          for j, cell in enumerate(row)
                                          if cell == EMPTY_CHAR)
        else: self._free_cells = free_cells

    @property
    def previous_move(self) -> tuple[int, int]:
        return self._previous_move


    def expand_state(self) -> list['GameState']:
        new_states: list[GameState] = []
        for pos in self._free_cells:
            next_board = deepcopy(self._board_state)
            next_board[pos[0]][pos[1]] = self._play_char
            next_play_char = 'X' if self._play_char != 'X' else 'O'

            new_states.append(GameState(next_board, next_play_char,
                                        self._max_player,
                                        free_cells=self._free_cells - {pos},
                                        previous_move=pos))
        return new_states
    
    def calculate_score(self) -> Optional[NumericType]:
        if (winner := get_winner(self._board_state)):
            return (1 if winner == self._max_player else -1) * MAX_SCORE
        else:
            return TIE_SCORE if len(self._free_cells) == 0 else None
        
    def heuristic_score(self, depth: int) -> NumericType:
        """Placeholder method for compatibility with minimax algorithm"""
        return -depth + 0 if (h_score := self.calculate_score()) is None else h_score
        

    def __str__(self) -> str:
        return '\n'.join('|'.join(row) for row in self._board_state)
    

class UltimateGameState(GameState):
    __slots__ = '_subboards'
    def __init__(self, main_board_state: UltimateTicTacToeBoard,
                 subboard_states: list[list[TicTacToeBoard]],
                 player_char: PlayerCharacter,
                 max_player: PlayerCharacter,
                 # board_to_play: Optional[tuple[int, int]] = None
                 # previous_move: Optional[tuple[int, int, int, int]]
                 # free_cells: Optional[set[tuple[int, int, int, int]]]
                 **kwargs):
        free_cells = kwargs['free_cells'] if 'free_cells' in kwargs else None
        board_to_play = kwargs['board_to_play'] if 'board_to_play' in kwargs else None
        previous_move = kwargs['previous_move'] if 'previous_move' in kwargs else None

        free_cells = set()
        if board_to_play is None:
            for i, row in enumerate(subboard_states):
                for j, board in enumerate(row):
                    if main_board_state[i][j] != EMPTY_CHAR: continue
                    free_cells.update((i, j , k, l)
                                      for k, subrow in enumerate(board)
                                      for l, cell in enumerate(subrow)
                                      if cell == EMPTY_CHAR)
        else:
            b2p = subboard_states[board_to_play[0]][board_to_play[1]]
            free_cells.update((*board_to_play, k, l)
                              for k, subrow in enumerate(b2p)
                              for l, cell in enumerate(subrow)
                              if cell == EMPTY_CHAR)

        super().__init__(main_board_state, player_char, max_player,
                         free_cells=free_cells, previous_move=previous_move)
        self._subboards = subboard_states

    def expand_state(self) -> list['UltimateGameState']:
        new_states: list[UltimateGameState] = []
        for pos in self._free_cells:
            next_board = deepcopy(self._board_state)
            next_subboards = deepcopy(self._subboards)
            next_play_char = 'X' if self._play_char != 'X' else 'O'

            next_subboards[pos[0]][pos[1]][pos[2]][pos[3]] = self._play_char
            if (winner := get_winner(next_subboards[pos[0]][pos[1]])):
                next_board[pos[0]][pos[1]] = winner
            elif winner is None:
                if not sum(row.count(EMPTY_CHAR) for row in next_subboards[pos[0]][pos[1]]):
                    next_board[pos[0]][pos[1]] = 'T'

            next_b2p = (pos[2], pos[3]) if next_board[pos[2]][pos[3]] == EMPTY_CHAR else None


            new_states.append(UltimateGameState(next_board, next_subboards,
                                                next_play_char, self._max_player,
                                                board_to_play=next_b2p,
                                                previous_move=pos))
        return new_states
    
    def heuristic_score(self, depth: int) -> NumericType:
        return 0