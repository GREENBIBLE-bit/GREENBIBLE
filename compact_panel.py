from pathlib import Path

p = Path("interface.py")
s = p.read_text(encoding="utf-8")

s = s.replace('font=("Arial", 11, "bold"),\n                padx=20,\n                pady=13,',
              'font=("Arial", 10, "bold"),\n                padx=16,\n                pady=8,')

p.write_text(s, encoding="utf-8")

print("CONTROL PANEL COMPACTED")