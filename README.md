# stashpull

> Interactive terminal utility to browse, preview, and selectively restore git stash entries across a repo.

---

## Installation

```bash
pip install stashpull
```

Or install from source:

```bash
git clone https://github.com/yourname/stashpull.git && cd stashpull && pip install .
```

---

## Usage

Run `stashpull` from anywhere inside a git repository:

```bash
stashpull
```

An interactive TUI will launch, listing all stash entries. Use the arrow keys to navigate, press `p` to preview a stash diff, and `Enter` to selectively restore it.

### Key Bindings

| Key        | Action                        |
|------------|-------------------------------|
| `↑ / ↓`   | Navigate stash entries        |
| `p`        | Preview diff for selected entry |
| `Enter`    | Restore selected stash        |
| `d`        | Drop selected stash entry     |
| `q / Esc`  | Quit                          |

### Example

```
$ stashpull

  stash@{0}  WIP on main: fix login bug          2 hours ago
  stash@{1}  WIP on feature/auth: add OAuth flow  yesterday
  stash@{2}  WIP on main: refactor user model     3 days ago

[p] Preview  [Enter] Restore  [d] Drop  [q] Quit
```

---

## Requirements

- Python 3.8+
- Git 2.0+

---

## License

[MIT](LICENSE) © 2024 yourname