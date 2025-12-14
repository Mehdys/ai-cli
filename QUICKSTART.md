# Quick Start Guide

## Setup (One-time)

1. **Install dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Add alias to your shell** (already done!):
   The alias has been added to `~/.zshrc`. 
   To use it in your current terminal, run:
   ```bash
   source ~/.zshrc
   ```
   
   Or just open a new terminal window.

## Usage

### Basic Commands

**Open an existing project:**
```bash
ai "open completed"
ai "open not finished"
```

**Create a new project:**
```bash
ai "create a project called my-app"
ai "start new project web-app"
```

### How It Works

- **Opening projects**: Uses fuzzy matching to find projects in `~/Desktop/Projects`
- **Creating projects**: Creates folder, initializes git, creates README, opens in Cursor
- **Natural language**: Understands various phrasings like "create", "start", "make", "open"

### Examples

```bash
# Open existing
ai "open completed"
ai "open the project about local ai"

# Create new
ai "create a project called todo-app"
ai "start new project blog"
ai "make a project called api-server"

# If project exists, it just opens it
ai "create a project called existing-project"  # Opens instead of creating
```

## Troubleshooting

**If `ai` command not found:**
- Make sure you've run `source ~/.zshrc` or opened a new terminal
- Or use the full path: `python3 /Users/mehdigribaa/Desktop/Projects/NotFinishedYet/ai-cli/ai.py`

**If Cursor doesn't open:**
- Make sure Cursor is installed
- Check that `cursor` command works: `which cursor`

**Projects location:**
- All projects are created/opened from `~/Desktop/Projects`

