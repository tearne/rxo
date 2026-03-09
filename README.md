# XO

A terminal noughts and crosses game.

## Controls
- Press `Up`, `Down`, `Left`, `Right` to move the cursor.
- Press `Enter` to place your piece.
- Press `N` to start a new round (after a round ends).
- Press `Esc` to quit.
- Press `T` to toggle the theme.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — handles Python and dependencies automatically

## Linux

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and run
git clone <repo-url>
cd rxo
chmod +x xo.py
./xo.py
```

## Windows

**Install uv** — choose one:

- **winget** (built into Windows 10/11):
  ```
  winget install --id=astral-sh.uv -e
  ```
- **Manual**: download `uv-x86_64-pc-windows-msvc.zip` from the
  [uv releases page](https://github.com/astral-sh/uv/releases/latest),
  extract it, and add the folder to your PATH.

**Then run the game:**

```
git clone <repo-url>
cd rxo
uv run xo.py
```

`uv` will fetch Python 3.12+ and the `textual` library on first run.
