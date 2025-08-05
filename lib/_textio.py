# lib/_texio.py
import json, pathlib

def read_text(path):
    return pathlib.Path(path).read_text(encoding="utf-8")

def write_text(path, s):
    pathlib.Path(path).write_text(s, encoding="utf-8")

def emit_human(header, items):
    lines=[header]
    lines+=items
    return "\n".join(lines)

def emit_json(**kwargs):
    return kwargs