# 🤖 AI CLI - Because I'm Too Lazy to Navigate Folders

<div align="center">

**I got fed up with manually opening my projects or creating new ones, so I built this command for myself. You're welcome to use it too! 🎉**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with: Rage](https://img.shields.io/badge/made%20with-rage-red.svg)](https://github.com/yourusername/ai-cli)

*"Why click through folders when you can just... talk to your computer?"* 🤷‍♂️

</div>

---

## 😤 The Problem (My Rant)

Look, I'm a developer. I have like 50+ projects scattered across my `~/Desktop/Projects` directory. Every time I want to work on something, I have to:

1. Open Finder (or whatever file manager)
2. Navigate to `~/Desktop/Projects`
3. Remember which category folder it's in (`NotFinishedYet`, `completed`, `DuringWorkHours`, etc.)
4. Click through folders
5. Finally find the project
6. Open it in Cursor
7. Realize I'm in the wrong project
8. Repeat steps 1-7 😭

**OR** when I want to create a new project:
1. Navigate to the right folder
2. Create a new directory
3. `cd` into it
4. `git init`
5. Create a README
6. Open Cursor
7. Realize I forgot to initialize git
8. Go back and do it manually
9. Question my life choices 🤦‍♂️

**ENOUGH!** I said to myself. "There has to be a better way!"

So I built this. Now I just type:
```bash
ai "open ai cli"
```

And boom! ✨ It just works. No thinking. No clicking. No existential crisis.

## 🚀 What This Thing Does

It's basically a CLI that understands natural language and does the boring stuff for you:

- **Open projects** - Just tell it what you want, it'll find it (even if you misspell it)
- **Create projects** - Say "create a project called X" and it does EVERYTHING
- **No AI needed** - It's just smart pattern matching (because I'm too cheap for API calls)
- **Works offline** - No internet? No problem! (Unlike my other projects 😅)

## 📦 Installation (It's Easy, I Promise)

### Step 1: Get the Code

```bash
git clone https://github.com/yourusername/ai-cli.git
cd ai-cli
```

### Step 2: Install Stuff

```bash
pip install -r requirements.txt
```

That's it. Two commands. If you can't do this, maybe programming isn't for you. 😏

### Step 3: Make It Work Everywhere (Optional but Recommended)

Add this to your `~/.zshrc` or `~/.bashrc`:

```bash
alias ai="python3 /path/to/ai-cli/ai.py"
```

Then reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

Now you can use `ai` from anywhere. Like a boss. 💪

## 🎮 How to Use (It's Not Rocket Science)

### Opening Projects (The Fun Part)

Just... tell it what you want:

```bash
ai "open ai cli"
ai "open local ai"
ai "open that project about voice stuff"
```

![Opening a project example](images/Screenshot%202025-12-14%20at%2022.13.04.png)

It uses fuzzy matching, so even if you're half-asleep and type `"opne ai cli"`, it'll probably still work. I've tested it at 3 AM. It works. ☕

**What it does:**
- Searches in `~/Desktop/Projects/*/` (one level deep, because I organize my chaos)
- Finds the best match using some math magic
- Opens it in Cursor
- If it's not sure, it shows you the top 5 matches (so you can pick)

### Creating Projects (Even Easier)

Want a new project? Just say it:

```bash
ai "create a project called my-awesome-app"
ai "start new project todo-list"
ai "make a project called blog"
```

![Creating a project example](images/Screenshot%202025-12-14%20at%2022.14.00.png)

**What it does automatically:**
- Creates the folder (in the right place)
- Initializes git (because you always forget)
- Creates a README (with the project name, because you're lazy)
- Opens it in Cursor (so you can start coding immediately)

If the project already exists? It just opens it. Smart, right? 😎

## 🧠 How It Works (The Technical Stuff I'm Proud Of)

### The Magic Behind the Curtain

1. **You type something** like `"open ai cli"`
2. **It extracts keywords** - removes useless words like "the", "open", "project" (stopwords, if you're fancy)
3. **It searches** - looks in all subdirectories of `~/Desktop/Projects`
4. **It matches** - uses fuzzy matching (thanks, `rapidfuzz`!) to find the best match
5. **It opens** - launches Cursor with the project path
6. **You code** - because that's what you wanted to do anyway

### The Search Strategy

I organize my projects like this:
```
~/Desktop/Projects/
├── NotFinishedYet/     ← Projects I'll finish "soon"
│   ├── ai-cli/         ← This one!
│   └── ...
├── completed/          ← Projects I actually finished (rare)
│   └── ...
└── DuringWorkHours/    ← Projects I work on when I should be working
    └── ...
```

The CLI searches one level deep, so it finds projects regardless of which category folder they're in. Because I can never remember where I put things. 🤷‍♂️

## 🎯 Real-World Examples (From My Actual Usage)

```bash
# Morning routine: Open the project I was working on yesterday
ai "open ai cli"                    # ✅ Opens ai-cli

# Afternoon: Start a new side project
ai "create a project called meme-generator"  # ✅ Creates everything

# Late night: Can't remember the exact name
ai "open local ai"                  # ✅ Finds "localai-engine" anyway

# 3 AM: Typo? No problem
ai "opne ai cli"                    # ✅ Still works (probably)
```

### Screenshots in Action

Here's what it actually looks like when you use it:

**Opening an existing project:**
![Terminal screenshot - Opening project](images/Screenshot%202025-12-14%20at%2022.13.04.png)

**Creating a new project:**
![Terminal screenshot - Creating project](images/Screenshot%202025-12-14%20at%2022.14.00.png)

> 💡 **Tip:** You can add more screenshots to the `images/` folder and reference them here. Just make sure to use URL-encoded filenames (spaces become `%20`) or rename them without spaces for easier linking.

## ⚙️ Configuration (If You're Fancy)

Want to change where projects are stored? Edit `ai.py`:

```python
PROJECTS_DIR = Path.home() / "Desktop" / "Projects"  # Change this line
```

Want it to be less/more picky about matches? Change this:

```python
CONFIDENCE_THRESHOLD = 55  # Lower = more matches, Higher = pickier
```

That's about it. I kept it simple because I'm lazy. 😴

## 🧪 Testing (Because I'm a Professional... Sometimes)

I wrote tests. 41 of them. They all pass. Run them if you want:

```bash
pytest test_ai.py -v
```

If they don't pass, you probably broke something. Or I did. Either way, open an issue. 🤝

## 🤔 Why "AI CLI" If There's No AI?

Good question! I called it "AI CLI" because:
1. It sounds cool
2. It uses "artificial intelligence" (pattern matching, but shhh 🤫)
3. I'm bad at naming things
4. It's short and easy to type

If you have a better name, feel free to suggest it. I probably won't change it, but I'll appreciate the effort. 😊

## 🐛 Known Issues (Because Nothing's Perfect)

- Sometimes it opens the wrong project if you have similar names (my fault, not the tool's)
- If Cursor isn't installed, it'll tell you (politely, I hope)
- It only searches one level deep (by design, because I'm organized... ish)

## 🤝 Contributing (Please Help Me)

Found a bug? Have an idea? Want to make it better?

1. Fork it
2. Make changes
3. Test it (please)
4. Submit a PR
5. I'll probably merge it if it doesn't break anything

I'm not picky. Just don't make it slower. Speed is important when you're lazy. ⚡

## 📝 License

MIT License. Do whatever you want with it. Just don't blame me if it breaks your computer. 😅

## 🙏 Acknowledgments

- **Typer** - For making CLI development not suck
- **RapidFuzz** - For the fuzzy matching magic
- **Cursor** - For being an awesome IDE
- **Coffee** - For keeping me awake while building this
- **My Future Self** - For using this tool and thanking past me

## 💬 Final Thoughts

I built this because I was tired of manually managing projects. If you're in the same boat, give it a try. If not, that's cool too. I'm not your boss. 🤷‍♂️

**TL;DR:** Type `ai "open project-name"` or `ai "create project called name"`. It works. That's it. You're welcome.

---

<div align="center">

**Built with ❤️ (and a lot of frustration)**

⭐ Star this if you're also too lazy to navigate folders manually

**"Work smarter, not harder... or just be lazy like me"** 😎

</div>
