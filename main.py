import chatlas as ctl
import argparse
import json
import re
import keyring
import os
from chatlas._turn import UserTurn, AssistantTurn, SystemTurn

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = keyring.get_password("OPENAI_API_KEY", "default")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in env or macOS Keychain")

parser = argparse.ArgumentParser(description="Running Coach Chatbot")
parser.add_argument("name", help="your name")
parser.add_argument("-s", "--systemPrompt", type=str, 
                    default="You are an experienced and well-trained running coach but you are terse.", help="system prompt")
parser.add_argument("-f", "--filename", type=str, default="runConv.json", help="conversation filename")
parser.add_argument("-t", "--statfile", type=str, default="stats.txt", help="file to store statistics")
parser.add_argument("prompt", type=str)
args = parser.parse_args()

system_prompt = args.systemPrompt
fileName = args.filename
statfile = args.statfile
def turn_from_dict(d):
    role = d["role"]
    contents = d["contents"]
    if role == "user":
        return UserTurn(contents=contents)
    elif role == "assistant":
        return AssistantTurn(contents=contents)
    elif role == "system":
        return SystemTurn(contents=contents)
    else:
        raise ValueError(f"Unknown role: {role}")

chat = ctl.ChatOpenAI(system_prompt=system_prompt, api_key = api_key)
try:
    with open(fileName, 'r', encoding='utf-8') as f:
        data = json.load(f)
    turns = [turn_from_dict(d) for d in data]
    chat.set_turns(turns)
except FileNotFoundError:
    print(f"{fileName} not found. Starting a new conversation.")

newPrompt = args.prompt
chat.chat(newPrompt)

turns = chat.get_turns()
turns_json = [x.model_dump() for x in turns]
with open(fileName, 'w') as f:
    json.dump(turns_json, f, ensure_ascii=False, indent=2)
chat.export("index.html" , overwrite = True)
