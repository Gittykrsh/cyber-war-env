# clean_text.py
import os

for root, _, files in os.walk("."):
    for f in files:
        if f.endswith((".py", ".md", ".yaml", ".toml")):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()

                # remove all non-ascii
                clean = content.encode("ascii", "ignore").decode()

                with open(path, "w", encoding="utf-8") as file:
                    file.write(clean)

                print("Cleaned:", path)
            except:
                pass