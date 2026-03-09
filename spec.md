# XO
## Overview
`xo` is a Python CLI noughts and crosses game.
## Behaviours
### Game-play
`xo` uses normal noughts and crosses rules:
- There are 2 players, each represented by the symbol `x` or `o`.
- Players take turns placing one of their symbols on the board. A piece cant be placed on top of another.
- A player wins when there are 3 of their pieces in a straight or diagonal line.
### Interface
- The board is in the centre.
- A flashing orange dot indicates whoes turn it is. The dot is on the left with a `X` when it's `x`'s turn and on the right with an `O` when it's `o`'s turn.
- A selection highlight can be moved by the active player using the arrow keys from the very first turn.  They press enter to place their piece. The selected cell is indicated with ASCII-art square brackets (e.g. `[ X ]`).
- After a round is won, two buttons appear: **New Round** and **Quit**, with focus automatically on **New Round**.  The left/right arrow keys move focus between the two buttons.  Clicking **New Round** (or pressing `n`) starts the next round; clicking **Quit** (or pressing `esc`) exits the program.  Focused buttons are highlighted with ASCII-art square brackets.
- A button will toggle the theme between light and dark.  It can also be activated with the `t` key.

### Red Alert
The Red Alert function signls in two situations
- Player (A) has a winning move on (B)'s turn.
- Player (A) has a winning move on(A)'s turn. 

The game should scan for Red Alert situations after every turn, if it finds one the background turns red. It disappears at the start of the next round, or sooner if no Red Alerts are found.

## Constraints
- Written in Python
- Use `textual`
  - Use `tokyo-night` for dark theme.
  - Use `solarized-light` for light theme (default).
- Implement this as a single-file executable Python script using `uv` and a shebang along the lines of
  ```bash
  # /// script
  # requires-python = ">=3.12"
  # dependencies = []
  # ///
  ```
