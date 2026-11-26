# flowit · made by md monirul islam
# how i use it:
#   ctrl + option + space  -> start talking
#   ctrl + option + space  -> stop, and it pastes wherever my cursor is

# don't change settings here, change them in settings.md
# tell the ai about yourself in memory.md

import re, ast, json, math, subprocess, threading, urllib.request
from pathlib import Path
import numpy as np, sounddevice as sd, mlx_whisper, tkinter as tk
from pynput import keyboard


# -- settings come from settings.md ---
# these are just backups in case settings.md is missing or a line is broken
SETTINGS = {
    "HOTKEY":   "<ctrl>+<alt>+<space>",
    "WHISPER":  "mlx-community/whisper-large-v3-mlx",
    "LLM":      "llama3.2",
    "MIC":      None,
    "TRIGGERS": ["write", "draft", "generate", "create", "compose", "give", "make",
                 "brainstorm", "suggest", "come up", "list", "tell me", "reply",
                 "summarise", "summarize", "idea", "ideas", "email"],
}


def load_settings():
    # read settings.md (next to this file) and pick up any line like  NAME = value
    path = Path(__file__).with_name("settings.md")
    if not path.exists():
        print("settings.md not found, using the default settings")
        return
    for line in path.read_text().splitlines():
        m = re.match(r"\s*(" + "|".join(SETTINGS) + r")\s*=\s*(.+?)\s*$", line)
        if m:
            try:
                SETTINGS[m[1]] = ast.literal_eval(m[2])  # safely turns "text", None, 2, [..] into real values
            except Exception:
                print(f"couldn't read {m[1]} in settings.md, keeping the default")


load_settings()
HOTKEY, WHISPER, LLM, MIC = SETTINGS["HOTKEY"], SETTINGS["WHISPER"], SETTINGS["LLM"], SETTINGS["MIC"]

# memory.md is a little note about me (name, how i sign emails, who people are).
# it goes to the ai every time, so emails come out sounding like me
memory_file = Path(__file__).with_name("memory.md")
MEMORY = memory_file.read_text() if memory_file.exists() else ""

# turn the trigger words into one search pattern.
# if one of them shows up in the first 6 words, it's a job for the ai, otherwise plain dictation
COMMAND = re.compile(r"\b(" + "|".join(re.escape(w) for w in SETTINGS["TRIGGERS"]) + r")\b", re.I)

# whisper loves to make up "thank you." when it hears nothing. classic.
# if that's all it heard, i just ignore it.
JUNK = {"thank you.", "thank you", "thanks for watching!", "thanks for watching.", "you", "bye.", ""}

# what the app is doing right now: "idle", "listening" or "thinking"
state, chunks, stream, front_app, level = "idle", [], None, "", 0.0


def is_command(text):
    # only check the start of the sentence, so a random "email" at the end doesn't trigger it
    return bool(COMMAND.search(" ".join(text.split()[:6])))


def osa(script):
    # small helper to run applescript. mac stuff like "which app is open" or "press cmd+v"
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()


def ask_llm(prompt):
    # sends what i said to ollama (running on my mac) and gets the written text back
    body = json.dumps({"model": LLM, "stream": False, "prompt": prompt, "system":
        "You write as the user, in their own voice, like a real person typing, not an AI. "
        "Keep it warm, relaxed and natural. Use short sentences, everyday words and contractions (I'm, it's, that's). "
        "Never use phrases like 'I hope this email finds you well', 'delve', 'I wanted to reach out' or 'feel free to'. "
        "No bullet points or headings unless asked. Keep it short and to the point. "
        "Reply with ONLY the finished text. No intro, no notes.\n"
        "Here is who the user is, use it when it helps:\n" + MEMORY}).encode()
    reply = urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/generate", body))
    return json.loads(reply.read())["response"].strip()


def paste(text):
    # copy to clipboard, jump back to the app i was in, then press cmd+v for me
    subprocess.run("pbcopy", input=text, text=True)
    osa(f'tell application "{front_app}" to activate')
    osa('tell application "System Events" to keystroke "v" using command down')


def on_audio(data, frames, t, status):
    # the mic calls this a lot of times a second while i'm talking
    global level
    chunks.append(data.copy())
    level = min(1.0, float(np.sqrt(np.mean(data ** 2))) * 25)  # how loud i am, for the bars


def process():
    # runs after i stop talking: voice -> text -> (maybe ai) -> paste
    global state
    try:
        audio = np.concatenate(chunks).flatten() if chunks else np.zeros(1, np.float32)

        # if the recording is basically silent, the mic probably isn't allowed
        peak = float(np.abs(audio).max())
        if peak < 0.01:
            print(f"silence (peak {peak:.4f}) - check microphone permission or MIC in settings.md")
            return

        text = mlx_whisper.transcribe(audio, path_or_hf_repo=WHISPER, language="en",
                                      condition_on_previous_text=False)["text"].strip()
        print(f"heard (peak {peak:.2f}):", text)
        if text.lower() in JUNK:
            return

        if is_command(text):
            print("mode: ai ->", LLM)
            paste(ask_llm(text))
        else:
            print("mode: dictation")
            paste(text)
    except Exception as e:
        print("error:", e)  # usually ollama isn't running
    finally:
        state = "idle"  # always go back to idle, even if something broke


def toggle():
    # the hotkey does both jobs: first press starts, second press stops
    global state, chunks, stream, front_app
    if state == "idle":
        # remember which app i'm in, so the text goes back there later
        front_app = osa('tell application "System Events" to get name of first process whose frontmost is true')
        chunks, state = [], "listening"
        stream = sd.InputStream(device=MIC, samplerate=16000, channels=1, dtype="float32", callback=on_audio)
        stream.start()
    elif state == "listening":
        stream.stop(); stream.close()  # mic off straight away, no orange dot hanging around
        state = "thinking"
        # do the heavy work in the background so the animation doesn't freeze
        threading.Thread(target=process, daemon=True).start()


# --- the little pill at the bottom middle of the screen ---
root = tk.Tk()
root.overrideredirect(True)            # no title bar, no buttons
root.attributes("-topmost", True)  # stay on top of everything
root.attributes("-transparent", True)  # see-through corners
root.config(bg="systemTransparent")

W, H = 140, 44
root.geometry(f"{W}x{H}+{(root.winfo_screenwidth() - W) // 2}+{root.winfo_screenheight() - H - 90}")
c = tk.Canvas(root, width=W, height=H, bg="systemTransparent", highlightthickness=0)
c.pack()

# a pill shape is just two circles and a rectangle in a trench coat
for shape in (c.create_oval(0, 0, H, H), c.create_oval(W - H, 0, W, H), c.create_rectangle(H / 2, 0, W - H / 2, H)):
    c.itemconfig(shape, fill="#111", outline="")
bars = [c.create_rectangle(0, 0, 0, 0, outline="") for _ in range(7)]
root.withdraw()  # hidden until i press the hotkey
tick = 0


def animate():
    # runs every 40ms. red bars = listening (they follow my voice), blue bars = thinking
    global tick
    tick += 1
    if state == "idle":
        root.withdraw()
    else:
        if root.state() == "withdrawn":
            root.deiconify()
        listening = state == "listening"
        for i, b in enumerate(bars):
            wave = abs(math.sin(tick * 0.25 + i * 0.7))
            h = 3 + 15 * wave * (level if listening else 0.6)
            x = 35 + i * 11
            c.coords(b, x, H / 2 - h, x + 5, H / 2 + h)
            c.itemconfig(b, fill="#ff4d4d" if listening else "#7aa2ff")
    root.after(40, animate)


# load whisper once at the start so the first real try isn't slow
threading.Thread(target=lambda: mlx_whisper.transcribe(np.zeros(16000, np.float32), path_or_hf_repo=WHISPER), daemon=True).start()

keyboard.GlobalHotKeys({HOTKEY: toggle}).start()
print(f"hotkey: {HOTKEY} | whisper: {WHISPER} | llm: {LLM}")
print("mic:", sd.query_devices(MIC, "input")["name"])
print("memory:", "loaded" if MEMORY else "no memory.md found")
print("flowit is ready. press your hotkey and talk.")
print("made by md monirul islam")
animate()
root.mainloop()