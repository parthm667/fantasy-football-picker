#!/usr/bin/env python3
import json, pathlib
w = pathlib.Path(".")
shell = (w / "app_shell.html").read_text()
players = json.dumps(json.loads((w / "players.json").read_text()), separators=(",", ":"))
engine = (w / "engine.js").read_text()
app = (w / "app.js").read_text()
assert "</script" not in players and "</script" not in engine.lower() and "</script" not in app.lower()
out = shell.replace("/*__PLAYERS__*/", "const PLAYERS = " + players + ";")
out = out.replace("/*__ENGINE__*/", engine)
out = out.replace("/*__APP__*/", app)
dest = w / "draft-command-2026.html"
dest.write_text(out)
print("wrote", dest, len(out), "bytes")
