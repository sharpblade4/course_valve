#!/usr/bin/env python3

from typing import Optional
import os
from enum import Enum, auto, unique
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import tkinter
from tkinter import ttk
import tkcalendar

from course_valve.valve_core import PageUpdater
from course_valve.valve_defs import TARGET_PAGE


@unique
class ValveFunc(Enum):
    RESTORE = auto()
    OPEN = auto()
    CLOSE = auto()


class PopupWindow:
    password_value: str
    top: tkinter.Toplevel

    def __init__(
        self, primary, text: str, is_information: bool, add_calendar: bool = False
    ) -> None:
        self.password_value = ""
        self.date_value = ""
        self.top = tkinter.Toplevel(primary)
        self.top.resizable(0, 0)
        if add_calendar:
            now = datetime.now()
            self._date_str_frame = tkinter.Frame(self.top)
            self._dynamic_value = tkinter.StringVar(
                self._date_str_frame,
                tkcalendar.Calendar.date.today().strftime("%d.%m.%Y"),
            )
            self._date_label = tkinter.Label(
                self._date_str_frame, textvariable=self._dynamic_value
            )
            self._date_label.pack(pady=10, padx=30)
            self._cal = tkcalendar.Calendar(
                self.top,
                selectmode="day",
                firstweekday="sunday",
                mindate=now,
                maxdate=now + timedelta(90),
                showweeknumbers=False,
                date_pattern="dd.mm.yyyy",
                selectbackground="blue",
                weekendbackground ="white",
                textvariable=self._dynamic_value,
                year=now.year,
                month=now.month,
                day=now.day,
            )
            self._cal.pack(pady=20, fill="both", expand=True, padx=10)
            self._dynamic_value.set(
                f"{self._cal.selection_get().strftime('%d.%m.%Y')}"
            )
            self._date_str_frame.pack()

        self._label = tkinter.Label(self.top, text=text)
        self._label.pack(pady=20, padx=30)
        if not is_information:
            self._entry = tkinter.Entry(self.top, show="*")
            self._entry.pack(pady=20, padx=40)
        self._button = tkinter.ttk.Button(self.top, text="OK", command=self._cleanup)
        self._button.pack(pady=20, padx=40)

    def _cleanup(self) -> None:
        if hasattr(self, "_entry"):
            self.password_value = self._entry.get()
        if hasattr(self, "_cal"):
            self.date_value = self._cal.selection_get().strftime("%d.%m.%Y")
        self.top.destroy()


class MainWindow:
    def __init__(self, primary, img) -> None:
        self._primary = primary
        self._pop_window = None
        self._image_panel = tkinter.Label(primary, image=img)
        self._image_panel.grid(row=0, column=0, columnspan=3, padx=60)

        self._pu = PageUpdater(TARGET_PAGE)
        if not self._pu.is_backup_exists():
            self._popup(
                "ERROR: cannot create backup. Contact Ron.",
                is_information=True,
                func=None,
            )

        self._label1 = tkinter.Label(primary, text="Course-Valve")
        self._label1.config(font=("Courier", 14))
        self._label1.grid(row=1, column=1, columnspan=1)

        self._button1 = tkinter.ttk.Button(
            primary,
            text="Restore",
            command=lambda: self._popup(
                "Restoring from backup.\nEnter password:",
                is_information=False,
                func=ValveFunc.RESTORE,
            ),
            width=20,
        )
        self._button1.grid(row=3, column=0)

        self._button2 = tkinter.ttk.Button(
            primary,
            text="Open Registration",
            command=lambda: self._popup(
                "Opening course registration.\nSelect date above and enter password:",
                is_information=False,
                func=ValveFunc.OPEN,
            ),
            width=20,
        )
        self._button2.grid(row=4, column=0)

        self._button3 = tkinter.ttk.Button(
            primary,
            text="Close Registration",
            command=lambda: self._popup(
                "Closing course registration.\nEnter password:",
                is_information=False,
                func=ValveFunc.CLOSE,
            ),
            width=20,
        )
        self._button3.grid(row=5, column=0)

    def _popup(
        self, text: str, is_information: bool, func: Optional[ValveFunc]
    ) -> None:
        should_pick_date = func is not None and func == ValveFunc.OPEN
        self._show_popup_aux(text, is_information, should_pick_date)
        status = False
        if func is not None and len(self._pop_window.password_value) > 0:
            if func == ValveFunc.RESTORE:
                status = self._pu.restore_from_backup(self._pop_window.password_value)
            elif func == ValveFunc.CLOSE:
                status = self._pu.close_course(self._pop_window.password_value)
            elif func == ValveFunc.OPEN and len(self._pop_window.date_value) > 0:
                status = self._pu.open_course(
                    self._pop_window.date_value, self._pop_window.password_value
                )
        else:
            status = True
        if not is_information:
            text = (
                "ʕ•ᴥ•ʔ   Success!"
                if status
                else "(⊙︿⊙)   Failed!!! please contact Ron for assistance."
            )
            self._show_popup_aux(text, is_information=True, add_calendar=False)

    def _show_popup_aux(
        self, text: str, is_information: bool, add_calendar: bool
    ) -> None:
        self._pop_window = PopupWindow(
            self._primary, text, is_information, add_calendar
        )
        self._button1["state"] = "disabled"
        self._button2["state"] = "disabled"
        self._button3["state"] = "disabled"
        self._primary.wait_window(self._pop_window.top)
        self._button1["state"] = "normal" # only restore allowed after performing an action.


def run_gui() -> None:
    window = tkinter.Tk()
    work_dir = os.path.abspath(os.path.dirname(__file__))
    img = ImageTk.PhotoImage(Image.open(os.path.join(work_dir, "icon.png")))
    window.geometry("320x380")
    window.title("Course Valve")
    window.resizable(0, 0)
    window.iconphoto(True, img)
    MainWindow(window, img)
    window.mainloop()


if __name__ == "__main__":
    run_gui()
