from copy import deepcopy

from typing import TypeAlias, Union, Literal, Optional


PlayerCharacter: TypeAlias = Literal['X', 'O']
TicTacToeBoard: TypeAlias = list[list[PlayerCharacter | Literal[' ']]]
UltimateTicTacToeBoard: TypeAlias = list[list[PlayerCharacter | Literal[' ', 'T']]]

NumericType: TypeAlias = Union[int, float]


EMPTY_CHAR: str = ' '
MAX_SCORE: int = 1000
TIE_SCORE: int = 0
def get_winner(board: TicTacToeBoard | UltimateTicTacToeBoard) -> Optional[PlayerCharacter]:
    """
    Get the winner of current state. Duh...

    ## Parameters:
    `board`: a Tic-Tac-Toe board or an Ultimate Tic-Tac-Toe board.
        A Tic-Tac-Toe board is a 3x3 grid with values `'X'`, `'O'` and `' '`.\
        The Ultimate Tic-Tac-Toe board extends this definition, having an additional\
        value `'T'`, representing a subboard that ended in a tie.

    ## Return
    `'X'` or `'O'` if either has won the game, else return `None` if\
    game has not ended or it is a tie
    """
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
    """
    Class representing a state in the Tic-Tac-Toe game

    ## Attributes (read-only):
    `previous_move` (`tuple[int, int]`): the move made before reaching the current state.
    `play_char` (`Literal['X', 'O']`): the character TO make the next move.\
        Note: this character has NOT made a move
    `game_over` (`bool`): determines if the game is over (if there is a winner or the game ties)

    ## Methods:
    `expand_state()`
    `calculate_score()`
    """
    # _board_state: the Tic-Tac-Toe board.\
    #     This is a 3x3 grid containing characters X, O and ' '.
    # _free_cells: (row, col) of the empty cells on the grid.
    # _max_player: the maximizing player, max player is the player char if this is a root state
    __slots__ = '_board_state', '_play_char', '_free_cells', '_previous_move', '_max_player'
    def __init__(self, board_state: TicTacToeBoard,
                 player_char: PlayerCharacter,
                 **kwargs):
        """
        Initialize the state.

        ## Parameters:
        `board_state`: a 3x3 grid of characters `'X'`, `'O'` and `' '`
        `player_char`: the player to make a move at the current state. Should be `'X'` or `'O'`
        """
        self._board_state = board_state
        self._play_char = player_char
        self._max_player = kwargs['max_player'] if 'max_player' in kwargs else player_char
        self._previous_move = kwargs['previous_move'] if 'previous_move' in kwargs else None

        free_cells = kwargs['free_cells'] if 'free_cells' in kwargs else None

        if free_cells is None:
            self._free_cells = set((i, j) for i, row in enumerate(self._board_state)
                                          for j, cell in enumerate(row)
                                          if cell == EMPTY_CHAR)
        else: self._free_cells = free_cells

    @property
    def previous_move(self) -> tuple[int, int]:
        """
        The move made before reaching the current state.
        For example: consider this state
            ```
            |X| |O|
            | | | |
            | | | |
            ```
        It is `X`'s turn, and `X` decides to play at (1, 0). Then, the next state should\
        have `previous_move = (1, 0)` and `play_char = O`.

        ## Return
        the row and column of the previous move
        """
        return self._previous_move
    @property
    def game_over(self) -> bool:
        """
        Determines if the game is over.

        ## Return
        True if the game has a winner, or ended in a tie.
        """
        return (not len(self._free_cells)) or bool(get_winner(self._board_state))
    @property
    def play_char(self) -> PlayerCharacter:
        """
        The character TO make the next move. Note: this character has NOT made a move yet!
        
        ## Return
        `'X'` or `'O'`
        """
        return self._play_char


    def expand_state(self) -> list['GameState']:
        """
        Expand into next states if possible. Expanding is basically making a move\
        with the current player character.

        ## Return
        list of the neighbouring `GameState`'s
        """
        new_states: list[GameState] = []
        for pos in self._free_cells:
            next_board = deepcopy(self._board_state)
            next_board[pos[0]][pos[1]] = self._play_char
            next_play_char = 'X' if self._play_char != 'X' else 'O'

            new_states.append(GameState(next_board, next_play_char,
                                        max_player=self._max_player,
                                        free_cells=self._free_cells - {pos},
                                        previous_move=pos))
        return new_states
    
    def calculate_score(self) -> Optional[NumericType]:
        """
        Calculate the score of current state.\\
        If the maximizing player has won, `MAX_SCORE` is returned.\
            Symmetrically, `-MAX_SCORE` is returned if maximizing player has lost.\
            If the game ends in a tie, `TIE_SCORE` is returned.

        ## Return
        A number if the game has ended, else `None`
        """
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
                 **kwargs):
        """
        Initialize the state.

        ## Parameters:
        `main_board_state`: a 3x3 grid of characters `'X'`, `'O'`, `'T'` and `' '`.\
            `'T'` stands for a subboard that ended in a draw.
        `subboard_state`: a 3x3 grid of `TicTacToeBoard`.\
            A `TicTacToeBoard` is a 3x3 grid of characters `'X'`, `'O'`, and `' '`
        `player_char`: the player to make a move at the current state. Should be `'X'` or `'O'`
        """
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

        max_player = kwargs['max_player'] if 'max_player' in kwargs else player_char
        super().__init__(main_board_state, player_char, max_player=max_player,
                         free_cells=free_cells, previous_move=previous_move)
        self._subboards = subboard_states

    @property
    def previous_move(self) -> tuple[int, int, int, int]:
        """
        The move made before reaching the current state. Similar to `GameState`,\
            this is a tuple of 4 values (row of subboard, col of subboard, row of cell, col of cell)

        ## Return
        (subboard row, subboard column, cell row, cell column)
        """
        return self._previous_move

    def expand_state(self) -> list['UltimateGameState']:
        """
        Expand into next states if possible. Expanding is basically making a move\
        with the current player character.

        ## Return
        list of the neighbouring `UltimateGameState`'s
        """
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
                                                next_play_char,
                                                max_player=self._max_player,
                                                board_to_play=next_b2p,
                                                previous_move=pos))
        return new_states
    
    def heuristic_score(self, depth: int) -> NumericType:
        """
        Heuristic score for the current state.

        ## Return
        A number
        """
        # 1. Small board wins add 5 points
        # 2. Winning the center board adds 10
        # 3. Winning a corner board adds 3
        # 4. Getting a center square in any small board is worth 3
        # 5. Getting a square in the center board is worth 3.
        # Two board wins which can be continued for a winning sequence
        #   (i.e. they are in a row, column or diagonal without an interfering win
        #   for the other player in the third board of the sequence) are worth 4 points
        # And a similar sequence inside a small board is worth 2 points.
        # A symmetric negative score is given if the other player has these features
        heurstic = self._board_state.count(self._play_char) * 5
        # heuristic 5
        heurstic += self._subboards[1][1].count(self._play_char) * 3
        if self.previous_move:
            if (self.previous_move[0] == 1) and (self.previous_move[1] == 1) and\
               (self._board_state[1][1] == self._play_char):
                heurstic += 10
            if ((self.previous_move[0] == 0) and (self.previous_move[1] == 0) or\
                (self.previous_move[0] == 0) and (self.previous_move[1] == 2) or\
                (self.previous_move[0] == 2) and (self.previous_move[1] == 0) or\
                (self.previous_move[0] == 2) and (self.previous_move[1] == 2)) and\
               (self._board_state[self.previous_move[0]][self.previous_move[1]] == self._play_char):
                heurstic += 3

        for i, row in enumerate(self._subboards):
            for j, board in enumerate(row):
                if board[1][1] == self._play_char: heurstic += 3
        return heurstic * (1 if self._play_char == self._max_player else -1)