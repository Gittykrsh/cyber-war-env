import os

def find_emojis_in_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            for ch in content:
                if ord(ch) > 10000:  # emoji range
                    print(f"Emoji found in {file_path}: {repr(ch)}")
    except:
        pass

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith((".py", ".md", ".yaml", ".toml")):
            find_emojis_in_file(os.path.join(root, file))