# Flowit settings

This is the one file I wanted anyone to be able to open without fear. **It controls Flowit.** Change a value in the box below, save it, and restart Flowit (`python3 flowit.py`). The code never needs touching.

```python
HOTKEY   = "<ctrl>+<alt>+<space>"
WHISPER  = "mlx-community/whisper-large-v3-mlx"
LLM      = "llama3.2"
MIC      = None
TRIGGERS = ["write", "draft", "generate", "create", "compose", "give", "make", "brainstorm", "suggest", "come up", "list", "tell me", "reply", "summarise", "summarize", "idea", "ideas", "email"]
```

> Keep each setting on its own line, in the form `NAME = value`, with text in "quotes".

---

## What each one does

### HOTKEY
The keys you press to start and stop talking.
- Default: `"<ctrl>+<alt>+<space>"` (Ctrl + Option + Space)
- Other ideas: `"<cmd>+<shift>+d"`, `"<ctrl>+<alt>+v"`, `"<f5>"`
- `<alt>` is the Option key on a Mac.
- Don't pick a shortcut you already use, like Cmd+Space (that's Spotlight).

### WHISPER
The model that turns your voice into text.

| Value | Speed | Accuracy |
|---|---|---|
| `"mlx-community/whisper-large-v3-mlx"` | slower | best |
| `"mlx-community/whisper-large-v3-turbo"` | much faster | almost the same for English |

The model downloads the first time you use it, which is about 1.5 to 3 GB.

### LLM
The local AI that writes emails and ideas. It runs in [Ollama](https://ollama.com).
- Default: `"llama3.2"` (small and fast)
- Better writing: `"qwen2.5:7b"` or `"llama3.1:8b"`
- You have to download a model before you use it: `ollama pull qwen2.5:7b`
- `ollama list` shows the models you already have.

### MIC
Which microphone to use.
- `None` uses your Mac's default mic.
- To use another one, find its number with
  `python3 -c "import sounddevice as sd; print(sd.query_devices())"`
  and put that number in the box, for example `2`.
- When Flowit starts, it prints the mic it's using.

### TRIGGERS
The words that turn on AI mode. If any of them appears in your **first 6 words**, Flowit asks the AI. If none do, it just types what you said.
- Add a word: `"rewrite"`, `"explain"`, `"translate"`…
- Remove a word if it triggers too often. For example, take out `"email"` if you often dictate sentences like "I'll email her".