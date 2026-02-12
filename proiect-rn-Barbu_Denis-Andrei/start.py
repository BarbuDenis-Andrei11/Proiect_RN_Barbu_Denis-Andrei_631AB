# Fisier: start.py (pune-l in radacina, langa requirements.txt)
import sys
import os

# Adauga folderul curent la calea Python
sys.path.append(os.getcwd())

# Porneste aplicatia
from src.app.main import TradingApp
import tkinter as tk

if __name__ == "__main__":
    print(">>> Se lanseaza aplicatia...")
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()