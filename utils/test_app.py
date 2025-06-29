import tkinter as tk
import tkinterdnd2 as tkdnd
from main import PDFDuplicateApp, t

def test_app():
    root = tkdnd.Tk()
    app = PDFDuplicateApp(root)
    print("Application started successfully!")
    root.mainloop()

if __name__ == "__main__":
    test_app()
