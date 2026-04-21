# MacroAutoCraft

A desktop tool that automates crafting macro sequences (e.g. for FFXIV). Define macro sets with keybinds and durations, then let the app press the keys for you with randomized human-like timing.

## Features

- **Macro set management** — Create, select, and delete macro sets. Each set is identified by a difficulty name and contains up to 3 macros.
- **Automatic duration extraction** — Paste your in-game macro text and the app parses `/ac` lines with `<wait.N>` tags to calculate the total duration automatically.
- **Crafting automation** — Select a macro set, choose the number of iterations (1–999), and start crafting. A progress bar tracks completion in real time.
- **Pause / Resume / Stop** — Pause gracefully (finishes the current iteration before pausing), resume, or hard-stop at any time.
- **Input validation** — Duplicate keybinds within a set are rejected, iterations are capped at 3 digits, and keybinds are limited to a single character.
- **Persistent storage** — Macro sets are saved to a `macros.json` file so they survive between sessions.

## Installation

### From source

1. Make sure you have **Python 3.10+** installed.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   python ui.py
   ```

### From executable

A standalone `.exe` can be built with PyInstaller:

```
pip install pyinstaller
pyinstaller --onefile --windowed --name MacroAutoCraft --add-data "macros.json;." ui.py
```

The executable will be generated in the `dist/` folder.

> **⚠️ Important:** Place `MacroAutoCraft.exe` in its own dedicated folder. The application creates and manages a `macros.json` file in the same directory as the executable to store your macro sets. Keeping it in a separate folder avoids clutter and makes it easy to find your data.

## Usage

1. **Add a macro set** — Fill in a difficulty name, enter a keybind (single character) and paste the macro content for each macro (up to 3). Click **Save**.
2. **Select a macro set** — Click on a set in the list. The **Start Crafting** button becomes available.
3. **Start crafting** — Enter the number of iterations and click **Start Crafting**. A short countdown begins, then the app starts pressing keys automatically.
4. **Pause / Stop** — Use the **Pause** button to finish the current iteration and pause, or **Stop** to halt immediately.

## Project Structure

| File                  | Description                                              |
|-----------------------|----------------------------------------------------------|
| `ui.py`               | Tkinter GUI — pure display layer, delegates to backend  |
| `autocraft.py`        | Crafting automation logic (key presses, timing, events) |
| `jsonHandler.py`      | Data persistence — load/save/delete macro sets from JSON |
| `macroExctractor.py`  | Parses macro text to extract keybind and total duration  |
| `models.py`           | Pydantic data models (`MacroSet`, `AutomatedMacro`, etc.) |
| `exceptions.py`       | Custom exception classes                                |
| `macros.json`         | Stored macro sets (created automatically on first save) |

## License

This project is provided as-is for personal use.
