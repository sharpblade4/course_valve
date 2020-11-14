#!/usr/bin/env python3

from tkinter import ttk
import tkinter
from PIL import Image, ImageTk
import os

from course_valve.valve_core import PageUpdater
from course_valve.valve_defs import TARGET_PAGE

class PopupWindow:
    value: str
    top: tkinter.Toplevel

    def __init__(self, primary, text: str, is_information: bool) -> None:
        self.value = ""
        self.top = tkinter.Toplevel(primary)
        self.top.resizable(0, 0)
        self.top.geometry("260x150")
        self._label = tkinter.Label(self.top, text=text)
        self._label.grid(row=0, column=0, padx=30)
        if not is_information:
            self._entry = tkinter.Entry(self.top)
            self._entry.grid(row=1, column=0, padx=40)
        self._button = tkinter.ttk.Button(self.top, text='OK', command=self._cleanup)
        self._button.grid(row=2, column=0)

    def _cleanup(self) -> None:
        if hasattr(self, '_entry'):
            self.value = self._entry.get()
        self.top.destroy()


class MainWindow:
    def __init__(self, primary, img) -> None:
        self._primary = primary
        self._pop_window = None
        self._image_panel = tkinter.Label(primary, image=img)
        self._image_panel.grid(row=0, column=0, columnspan=3, padx=60)
        
        self._pu = PageUpdater(TARGET_PAGE)
        if not self._pu.is_backup_exists():
            self._popup('ERROR: cannot create backup. Contact Ron.', is_information=True)
        
        self._label1 = tkinter.Label(primary, text="Course-Valve")
        self._label1.config(font=("Courier", 14))
        self._label1.grid(row=1, column=1, columnspan=1)
        self._button1 = tkinter.ttk.Button(primary, text="Click Me!",
                                           command=lambda: self._popup("Enter password:", 
                                                                       is_information=False),
                                           width=20)
        self._button1.grid(row=3, column=0)


    def _popup(self, text: str, is_information: bool) -> None:
        self._pop_window = PopupWindow(self._primary, text, is_information)
        self._button1["state"] = "disabled"
        self._primary.wait_window(self._pop_window.top)
        self._button1["state"] = "normal"

    def _get_pop_value(self) -> str:
        return self._pop_window.value


def run_gui() -> None:
    window = tkinter.Tk()
    work_dir = os.path.abspath(os.path.dirname(__file__))
    img = ImageTk.PhotoImage(Image.open(os.path.join(work_dir, "icon.png")))
    window.geometry("320x380")
    window.title("Course Valve")
    window.resizable(0,0)
    window.iconphoto(True, img)
    MainWindow(window, img)
    window.mainloop()


if __name__ == '__main__':
    run_gui()
