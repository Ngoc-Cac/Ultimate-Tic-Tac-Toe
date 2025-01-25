# Ultimate Tic-Tac-Toe

Remember that fun little game with noughts and crosses?\
Yeah it gets boring pretty quickly. So why not try something that goes on a bit longer, and needs some more strategic planning?

#### Table of Contents
- [:scroll:**The Rules**](#rules)
- [:computer:**Running the program**](#program-run)

---
<a name="rules">

## :scroll:The Rules
Just like the normal Tic-Tac-Toe game, you win if you have a three in a row. However, here you are going to play on a 9x9 grid. This grid is subdivided into 3 smaller boards.
1. The first move can be made on any of the 81 squares in the grid. Following that, the next move has to be made in the small board with the corresponding position to the position made in the previous small board.
<details>
    <summary>
        <b>Illutstrative Example</b>
    </summary>
    <div align="center">
        <img src="./resource/tutorial/tutorial-1.png" width="600" height="250">
        <p>
            <b>
                X moved in the middle board at row 3, column 3. After that, O has to make a move in the small board at row 3, column 3
            </b>
        </p>
    </div>
</details>

2. If one player is able to make three in a row on a small board, a both player has filled the small board (a tie), the board is then no longer playable. When a player makes a move that send the next player to the aforementioned board, the next player can instead make a move in any other board.
<details>
    <summary>
        <b>Illutstrative Example</b>
    </summary>
    <div align="center">
        <img src="./resource/tutorial/tutorial-2.png" width="600" height="250">
        <p>
            <b>
                Here X is to play in the top middle board, X decides to play at the middle cell. In turn, O then has to play in the center small board. Since that board has been won, O can now play in any other board
            </b>
        </p>
    </div>
</details>

3. The players continue playing following the above rules until one has won three small boards in a row or they have filled out the entire grid.
<details>
    <summary>
        <b>Illutstrative Example</b>
    </summary>
    <div align="center">
        <img src="./resource/tutorial/tutorial-3.png" width="600" height="250">
        <p>
            <b>
                X has won three boards in a row (three boards in the middle column). X now wins the game
            </b>
        </p>
    </div>
</details>

---
<a name="pogram-run">

## :computer:How do I run the program?
1. Before running, be sure to have [Python](https://www.python.org/) installed.
2. Afterwards, install libraries in `/requirements.txt` using `pip install -r path/to/requirements.txt` or any other means. For more infomation, visit [pip install](https://pip.pypa.io/en/stable/cli/pip_install/#description).
2. If everything has been setup correctly, you can now run `main.py` as is.
