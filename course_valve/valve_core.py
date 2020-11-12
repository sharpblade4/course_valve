from typing import Tuple
from urllib.request import urlopen
import os
from ftplib import FTP
from tempfile import TemporaryDirectory
from hashlib import sha256
from tkinter import ttk
import tkinter

TARGET_PAGE: str = "https://ASD.co.il/course.html"
TARGET_FTP: str = "ftp://ASD.co.il/"
ENCRYPTED_PASSWORD: bytes = b'C]]GS_\x04\n_@\\_@\\_'


#
#  Core
#


def get_backup_path() -> str:
    return os.path.join(os.path.dirname(__file__), "course.html.bkp")


def save_backup(page_content: str) -> None:
    with open(get_backup_path(), "w") as f:
        f.write(page_content)


def read_html(page_address: str) -> str:
    with urlopen(page_address) as f:
        return f.read().decode("utf-8")


def get_begin_end_for_edit_text(page_content: str) -> Tuple[int, int]:
    div_id_idx = page_content.index("course-terms-reveal")
    orig_text_begin_idx = div_id_idx + page_content[div_id_idx:].index(">")
    orig_text_end_idx = orig_text_begin_idx + page_content[orig_text_begin_idx:].index("</")
    return orig_text_begin_idx, orig_text_end_idx


def insert_new_course_text(page_content: str, text: str) -> str:
    orig_text_begin_idx, orig_text_end_idx = get_begin_end_for_edit_text(page_content)
    return f"{page_content[:orig_text_begin_idx + 1]}{text}{page_content[orig_text_end_idx:]}"


def upload_content(page_content: str, user: str, password: str) -> bool:
    file_name = "course.html"
    with FTP(TARGET_FTP, user, password) as ftp, TemporaryDirectory() as dirpath:
        content_path = os.path.join(dirpath, file_name)
        with open(content_path, "w") as f:
            f.write(page_content)
        temp_orig_file_name = file_name + ".orig.bkp"
        ftp.rename(file_name, temp_orig_file_name)
        try:
            with open(content_path, "rb") as f:
                ftp.storbinary(f"STOR {file_name}", f)
            ftp.delete(temp_orig_file_name)
        except Exception as e:
            print(f"Error during FTP upload: {e}")
            ftp.rename(temp_orig_file_name, file_name)
            return False
    return True


def decrypt_password(key_pass: str, encrypted_pass: bytes) -> str:
    # gen hardocded pass by `bytes(x ^ y for x, y in zip('SAMELEN1'.encode('utf-8'), 'SAMELEN2'.encode('utf-8'))`)
    key_pass_bytes = sha256(key_pass.encode('utf-8')).hexdigest()[:len(encrypted_pass)].encode('utf-8')
    return bytes(x ^ y for x, y in zip(key_pass_bytes, encrypted_pass)).decode('utf-8')


#
#  GUI
#

def assemble_new_date_message(page_content: str, new_date: str) -> bool:
    orig_text_begin_idx, orig_text_end_idx = get_begin_end_for_edit_text() # TODO cnt


def execute_new_date_open_course(new_date: str) -> bool:
    page_content = read_html(TARGET_PAGE)
    save_backup(page_content)
    new_page_content = insert_new_course_text() # TODO cnt


def run_gui() -> None:
    window = tkinter.Tk()
    window.title("Course Valve")
    tkinter.Label(window, text="Username").grid(row=0)  # 'username' is placed on position 00 (row - 0 and column - 0)

    # 'Entry' class is used to display the input-field for 'username' text label
    tkinter.Entry(window).grid(row=0, column=1)  # first input-field is placed on position 01 (row - 0 and column - 1)

    tkinter.Label(window, text="Password").grid(row=1)  # 'password' is placed on position 10 (row - 1 and column - 0)

    tkinter.Entry(window).grid(row=1, column=1)  # second input-field is placed on position 11 (row - 1 and column - 1)

    # 'Checkbutton' class is for creating a checkbutton which will take a 'columnspan' of width two (covers two columns)
    tkinter.Checkbutton(window, text="Keep Me Logged In").grid(columnspan=2)

    # def test():
    #     tkinter.Label(window, text="GUI with Tkinter!").pack()
    tkinter.ttk.Button(window, text="Click Me!", command=None).grid(row=3, column=1)
    # TODO cnt
    window.mainloop()


if __name__ == '__main__':
    run_gui()
