import json
import os

MEMORY_FILE ="data/memory.json"

def load_memory():

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except:
        return []

    def save_memory(memory):

        os.makedirs("data", exist_ok=True)

        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(memory, file, indent=2, ensure_ascii=False)