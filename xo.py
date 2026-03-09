#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["textual>=0.50"]
# ///

from __future__ import annotations

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.geometry import Size
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.containers import Horizontal, Vertical

from rich.text import Text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_winner(grid: list[list[str | None]]) -> str | None:
    lines = [grid[r] for r in range(3)]
    lines += [[grid[r][c] for r in range(3)] for c in range(3)]
    lines += [[grid[i][i] for i in range(3)], [grid[i][2 - i] for i in range(3)]]
    for line in lines:
        if line[0] and all(c == line[0] for c in line):
            return line[0]
    return None


def has_winning_move(grid: list[list[str | None]], player: str) -> bool:
    """Return True if player has at least one winning move available."""
    for r in range(3):
        for c in range(3):
            if grid[r][c] is None:
                grid[r][c] = player
                if check_winner(grid):
                    grid[r][c] = None
                    return True
                grid[r][c] = None
    return False


BOARD_COLS = 3
BOARD_ROWS = 3

# Each cell is rendered as 5 chars wide × 3 lines tall
CELL_W = 5
CELL_H = 3


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------

class Board(Widget):
    """Interactive 3×3 noughts-and-crosses board."""

    BINDINGS: ClassVar = [
        ("up",    "move(-1, 0)", "Up"),
        ("down",  "move(1, 0)",  "Down"),
        ("left",  "move(0, -1)", "Left"),
        ("right", "move(0, 1)",  "Right"),
        ("enter", "place",       "Place"),
    ]

    can_focus = True

    cursor: reactive[tuple[int, int]] = reactive((1, 1))
    active: reactive[str] = reactive("x")
    locked: reactive[bool] = reactive(False)

    class MoveMade(Message):
        def __init__(self, row: int, col: int) -> None:
            super().__init__()
            self.row = row
            self.col = col

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.grid: list[list[str | None]] = [[None] * 3 for _ in range(3)]

    def reset(self) -> None:
        self.grid = [[None] * 3 for _ in range(3)]
        self.cursor = (1, 1)
        self.locked = False
        self.refresh()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return CELL_W * BOARD_COLS + (BOARD_COLS + 1)

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return CELL_H * BOARD_ROWS + (BOARD_ROWS + 1)

    def render(self) -> Text:
        cr, cc = self.cursor
        t = Text()

        # horizontal separator
        h_sep = "─" * CELL_W
        top    = "┌" + ("┬".join([h_sep] * BOARD_COLS)) + "┐"
        mid    = "├" + ("┼".join([h_sep] * BOARD_COLS)) + "┤"
        bottom = "└" + ("┴".join([h_sep] * BOARD_COLS)) + "┘"

        for r in range(BOARD_ROWS):
            t.append(top if r == 0 else mid)
            t.append("\n")
            # cell content row (vertically centred in CELL_H lines)
            for sub in range(CELL_H):
                t.append("│")
                for c in range(BOARD_COLS):
                    piece = self.grid[r][c]
                    is_cursor = (r == cr and c == cc)
                    if sub == CELL_H // 2:
                        symbol = piece.upper() if piece else " "
                        if is_cursor and not self.locked:
                            cell_text = f"[ {symbol} ]"
                        else:
                            cell_text = f"  {symbol}  "
                        if piece == "x":
                            style = "bold cyan"
                        elif piece == "o":
                            style = "bold magenta"
                        else:
                            style = ""
                        t.append(cell_text, style=style)
                    else:
                        t.append(" " * CELL_W)
                    t.append("│")
                t.append("\n")
        t.append(bottom)
        return t

    def action_move(self, dr: int, dc: int) -> None:
        if self.locked:
            return
        r, c = self.cursor
        self.cursor = ((r + dr) % 3, (c + dc) % 3)

    def action_place(self) -> None:
        if self.locked:
            return
        r, c = self.cursor
        if self.grid[r][c] is None:
            self.grid[r][c] = self.active
            self.refresh()
            self.post_message(self.MoveMade(r, c))


# ---------------------------------------------------------------------------
# BracketButton
# ---------------------------------------------------------------------------

class BracketButton(Widget):
    """A focusable button that shows ASCII-art square brackets when focused."""

    BINDINGS: ClassVar = [("enter", "press", "Press")]

    can_focus = True

    class Pressed(Message):
        def __init__(self, button_id: str) -> None:
            super().__init__()
            self.button_id = button_id

    def __init__(self, label: str, id: str, **kwargs) -> None:
        super().__init__(id=id, **kwargs)
        self._label = label

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return len(self._label) + 4

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return 1

    def render(self) -> Text:
        if self.has_focus:
            return Text(f"[ {self._label} ]", style="bold")
        return Text(f"  {self._label}  ")

    def on_focus(self) -> None:
        self.refresh()

    def on_blur(self) -> None:
        self.refresh()

    def action_press(self) -> None:
        self.post_message(self.Pressed(self.id or ""))

    def on_click(self) -> None:
        self.post_message(self.Pressed(self.id or ""))


# ---------------------------------------------------------------------------
# RoundEndOverlay
# ---------------------------------------------------------------------------

class RoundEndOverlay(Widget):
    """Shown after a round ends — two clickable buttons plus key shortcuts."""

    BINDINGS: ClassVar = [
        ("left",  "shift(-1)", ""),
        ("right", "shift(1)",  ""),
    ]

    def action_shift(self, direction: int) -> None:
        buttons = list(self.query(BracketButton))
        focused = next((b for b in buttons if b.has_focus), None)
        if focused:
            idx = buttons.index(focused)
            buttons[(idx + direction) % len(buttons)].focus()

    DEFAULT_CSS = """
    RoundEndOverlay {
        layer: overlay;
        dock: bottom;
        width: 100%;
        height: 5;
        align: center middle;
        background: $panel;
    }
    RoundEndOverlay Horizontal {
        align: center middle;
        height: 100%;
    }
    RoundEndOverlay BracketButton {
        margin: 0 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield BracketButton("New Round  [N]", id="new-round-btn")
            yield BracketButton("Quit  [ESC]", id="quit-btn")


# ---------------------------------------------------------------------------
# TurnDot
# ---------------------------------------------------------------------------

class TurnDot(Widget):
    """Turn indicator dot — shown on the active player's side."""

    active: reactive[bool] = reactive(False)
    _blink: reactive[bool] = reactive(True)

    def __init__(self, player: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._player = player.upper()

    def on_mount(self) -> None:
        self.set_interval(0.5, self._tick)

    def _tick(self) -> None:
        self._blink = not self._blink

    def render(self) -> Text:
        t = Text(justify="center")
        t.append(f" {self._player} \n", style="bold")
        if self.active and self._blink:
            t.append(" ● ", style="bold orange1")
        else:
            t.append("   ")
        return t


# ---------------------------------------------------------------------------
# XOApp
# ---------------------------------------------------------------------------

class XOApp(App):

    BINDINGS: ClassVar = [
        Binding("t",      "toggle_theme", "Toggle Theme"),
        Binding("n",      "new_round",    "New Round",  priority=True),
        Binding("escape", "quit",         "Quit",       priority=True),
    ]

    CSS = """
    Screen {
        layers: default overlay;
    }

    Screen.doom {
        background: $error 30%;
    }

    #main {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    TurnDot {
        width: 7;
        height: 100%;
        content-align: center middle;
        padding: 1;
    }

    #center {
        width: auto;
        height: auto;
        align: center middle;
    }

    Board {
        width: auto;
        height: auto;
        margin: 1;
    }

    BracketButton {
        width: auto;
        height: 1;
        margin: 1 2;
    }

    """

    TITLE = "XO"
    THEME = "solarized-light"

    def __init__(self) -> None:
        super().__init__()
        self.current_player: str = "x"
        self._round_over: bool = False
        self._doom: bool = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="main"):
            yield TurnDot("x", id="dot-x")
            with Vertical(id="center"):
                yield Board(id="board")
                yield BracketButton("Toggle Theme", id="theme-btn")
            yield TurnDot("o", id="dot-o")

    def on_mount(self) -> None:
        self.theme = "solarized-light"
        self.query_one("#dot-x", TurnDot).active = True
        self.call_after_refresh(self.query_one(Board).focus)

    # ------------------------------------------------------------------
    # Game logic
    # ------------------------------------------------------------------

    def on_board_move_made(self, event: Board.MoveMade) -> None:
        board = self.query_one(Board)
        grid = board.grid
        winner = check_winner(grid)

        if winner:
            board.locked = True
            self._round_over = True
            overlay = RoundEndOverlay()
            self.mount(overlay)
            self.call_after_refresh(lambda: overlay.query_one("#new-round-btn", BracketButton).focus())
            return

        # Draw?
        if all(grid[r][c] is not None for r in range(3) for c in range(3)):
            board.locked = True
            self.set_timer(1.5, self._reset_round)
            return

        # Red Alert — re-evaluate after every move
        other = "o" if self.current_player == "x" else "x"
        should_doom = has_winning_move(grid, self.current_player) or has_winning_move(grid, other)
        if should_doom != self._doom:
            self._doom = should_doom
            if should_doom:
                self.screen.add_class("doom")
            else:
                self.screen.remove_class("doom")

        # Next player
        self.current_player = "o" if self.current_player == "x" else "x"
        board.active = self.current_player
        self.query_one("#dot-x", TurnDot).active = (self.current_player == "x")
        self.query_one("#dot-o", TurnDot).active = (self.current_player == "o")

    def _reset_round(self) -> None:
        if self._doom:
            self._doom = False
            self.screen.remove_class("doom")
        board = self.query_one(Board)
        self.current_player = "x"
        board.active = "x"
        self.query_one("#dot-x", TurnDot).active = True
        self.query_one("#dot-o", TurnDot).active = False
        board.reset()
        board.focus()

    def action_new_round(self) -> None:
        if not self._round_over:
            return
        self._round_over = False
        try:
            self.query_one(RoundEndOverlay).remove()
        except NoMatches:
            pass
        self._reset_round()

    # ------------------------------------------------------------------
    # Theme toggle
    # ------------------------------------------------------------------

    def action_toggle_theme(self) -> None:
        self.theme = "tokyo-night" if self.theme == "solarized-light" else "solarized-light"

    def on_bracket_button_pressed(self, event: BracketButton.Pressed) -> None:
        if event.button_id == "theme-btn":
            self.action_toggle_theme()
        elif event.button_id == "new-round-btn":
            self.action_new_round()
        elif event.button_id == "quit-btn":
            self.exit()


if __name__ == "__main__":
    XOApp().run()
