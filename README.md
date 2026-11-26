# Flowit

> I talk. My Mac writes.

Most of my best ideas show up at the worst time: halfway through an email, in the middle of a chat, or when my hands are already busy. Typing is slower than thinking. So I built Flowit, a local voice assistant that lives entirely on my Mac. It's still an early prototype, a little rough around the edges and far from finished, but it already saves me time every day.

I press one key and speak, and the words appear right where my cursor is blinking. When I say *"write an email to Katie saying thank you to her for the opportunity"*, it doesn't just type my sentence; it writes the email. When I say *"give me some ideas about NASA"*, it gives me ideas. And when I'm only talking, it simply listens and types what I said.

Everything runs on my own MacBook. No cloud, no account, nothing leaving the machine.

## Setting it up

You'll need a Mac with Apple Silicon (M1 or newer). I built and tested it on an M4 Pro.
Automatic recognition for Windows and Linux will be added, so you won't need to configure anything manually.

```bash
brew install python-tk@3.14 ollama   # use the python-tk version that matches your Python
brew services start ollama
ollama pull llama3.2 # for better text generation use qwen2.5:7b if you machine can handle it and change it on the settings.md as 
                     # (I'm using qwen3.5:9b)

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 flowit.py
```

The first run downloads the speech model, about 3 GB, so it's a good moment for a cup of tea.

**Want better writing?** A bigger model makes a real difference. I use `qwen3.5:9b`, and `qwen2.5:7b` is a great step up too. Pull the one you want (for example `ollama pull qwen2.5:7b`), then set `LLM` to that name in [settings.md](settings.md).

macOS will want to know it can trust Flowit. In **System Settings → Privacy & Security**, allow your Terminal (or VS Code) under **Microphone**, **Accessibility** and **Input Monitoring**, then restart Terminal.

## Using it

1. Click wherever the words should go: an email, Notes, a chat.
2. Press **Ctrl + Option + Space**. A small pill with red bars appears at the bottom of the screen, rising and falling with your voice.
3. Say what's on your mind.
4. Press **Ctrl + Option + Space** again. The bars turn blue while it thinks, and then the text arrives.

Everything you might want to change (the hotkey, the models, the mic, the words that wake up the AI) lives in **[settings.md](settings.md)**. Edit it, save it, restart Flowit, and that's it.

## Teaching it who you are

An email that ends with *"Best regards, [Your Name]"* isn't much help. So Flowit has a small note called **`memory.md`**, where you tell it about yourself: your name, how you sign off, the tone you like, and who the people you often write to are.

```markdown
# About me
- Name: Md Monirul Islam (Mahim)
- Sign my emails as: Md Monirul Islam
- My tone: friendly, casual and warm. Simple words, no corporate language.
```

Flowit reads this note every time it starts and quietly passes it to the AI, so the emails come out sounding like you and signed with your name. Keep it short, since it's sent with every request. If the file isn't there, Flowit still works; it just doesn't know who you are yet.

Your memory is personal, so you may want to add `memory.md` to `.gitignore` before pushing to GitHub.

## When it doesn't listen

- **It only types "Thank you."** The mic isn't allowed, and Whisper is filling the silence with good manners. Check the Microphone permission.
- **AI mode stays quiet.** Ollama isn't awake. Run `brew services start ollama`.
- **Nothing pastes.** Turn on the Accessibility permission.

## How it works

I like to picture Flowit as three helpers passing a note down a line.

**The ear** listens. It's OpenAI's Whisper Large-v3, running on the Mac's own chip through Apple's MLX, and it turns my voice into text.

**The decider** reads the first few words. If they sound like a request, such as *write*, *give me*, *ideas* or *email*, it hands the note to the writer. If not, the note goes straight to my cursor.

**The writer** is a language model running locally in Ollama. It reads the request, checks `memory.md` to remember who I am, and writes the email or the ideas.

Then Flowit does the one thing I always forget I'm doing a hundred times a day: it copies the text and presses Cmd+V for me, in the app I was using. The pill is a tiny window drawn with Python's built-in Tkinter, and the hotkey comes from `pynput`. All of it fits in one Python file.

It's a small tool. But it closes a gap I used to feel every single day: the gap between thinking something and seeing it written down.

---

Made by **Md Monirul Islam**
