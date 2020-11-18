from typing import Tuple
from urllib.request import urlopen
import os
from ftplib import FTP
from tempfile import TemporaryDirectory
from hashlib import sha256
import re

from course_valve.valve_defs import (
    TARGET_FTP,
    ENCRYPTED_PASSWORD,
    TARGET_FILE_NAME,
    IDENTIFIER,
    NO_IDENTIFIER,
    FTP_USER,
    OPENED_TEMPLATE_NAME,
    CLOSED_TEMPLATE_NAME,
)


class PageUpdater:
    def __init__(self, page_address: str) -> None:
        self._work_dir = os.path.abspath(os.path.dirname(__file__))
        if not all(
            [
                os.path.exists(os.path.join(self._work_dir, e))
                for e in [OPENED_TEMPLATE_NAME, CLOSED_TEMPLATE_NAME]
            ]
        ):
            pass  # raise EnvironmentError(
            #    "ERROR: PageUpdater::__init__ : Missing essential template files"
            # )
        self._backup_path = os.path.join(self._work_dir, f"{TARGET_FILE_NAME}.bkp")
        if os.path.exists(self._backup_path):
            os.remove(self._backup_path)
        self._page_content = self._read_html(page_address)
        self._is_closed = NO_IDENTIFIER in self._page_content
        self._save_backup(self._page_content)
        self._date_pattern = re.compile(r"(\d+\.\d+\.\d+)")

    def restore_from_backup(self, password: str) -> bool:
        if self.is_backup_exists():
            with open(self._backup_path, "r", encoding="utf-8") as f:
                backup_content = f.read()
                return self._upload_content_aux(backup_content, FTP_USER, password)
        return False

    def is_backup_exists(self) -> bool:
        return os.path.exists(self._backup_path)

    def open_course(self, new_date: str, password: str) -> bool:
        if self._is_closed:
            with open(
                os.path.join(self._work_dir, OPENED_TEMPLATE_NAME), "r", encoding="utf-8"
            ) as f:
                page_content = f.read()
        else:
            page_content = self._page_content
        orig_text_begin_idx, orig_text_end_idx = self._get_begin_end_for_edit_text(page_content)
        new_sentence = self._replace_date(
            page_content[orig_text_begin_idx:orig_text_end_idx], new_date
        )
        new_page_content = self._insert_new_course_text(new_sentence, page_content)
        return self._upload_content_aux(new_page_content, FTP_USER, password)

    def close_course(self, password: str) -> bool:
        if self._is_closed:
            return False
        with open(
            os.path.join(self._work_dir, CLOSED_TEMPLATE_NAME), "r", encoding="utf-8"
        ) as f:
            closed_content = f.read()
        return self._upload_content_aux(closed_content, FTP_USER, password)

    def _save_backup(self, page_content: str) -> None:
        with open(self._backup_path, "w", encoding="utf-8") as f:
            f.write(page_content)

    def _read_html(self, page_address: str) -> str:
        with urlopen(page_address) as webpage:
            return webpage.read().decode("utf-8")

    def _replace_date(self, orig_sentence: str, new_date: str) -> str:
        if re.match(self._date_pattern, new_date) is None:
            raise ValueError(
                "ERROR: PageUpdate::_replace_date : new_date is not in the right format"
            )
        print('#@#@#', orig_sentence)
        orig_date = re.search(self._date_pattern, orig_sentence).group(1)
        return orig_sentence.replace(orig_date, new_date)

    def _get_begin_end_for_edit_text(self, page_content: str) -> Tuple[int, int]:
        div_id_idx = page_content.index(IDENTIFIER)
        orig_text_begin_idx = div_id_idx + page_content[div_id_idx:].index(">") + 1
        orig_text_end_idx = orig_text_begin_idx + page_content[
            orig_text_begin_idx:
        ].index("</")
        return orig_text_begin_idx, orig_text_end_idx

    def _insert_new_course_text(self, text: str, page_content: str) -> str:
        orig_text_begin_idx, orig_text_end_idx = self._get_begin_end_for_edit_text(page_content)
        return f"{page_content[:orig_text_begin_idx + 1]}{text}{page_content[orig_text_end_idx:]}"

    @staticmethod
    def _upload_content_aux(page_content: str, user: str, password: str) -> bool:
        file_name = TARGET_FILE_NAME
        ftp_password = PageUpdater._decrypt_password(password, ENCRYPTED_PASSWORD)
        with FTP(
            TARGET_FTP, user, ftp_password
        ) as ftp, TemporaryDirectory() as dirpath:
            content_path = os.path.join(dirpath, file_name)
            with open(content_path, "w", encoding="utf-8") as f:
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

    @staticmethod
    def _decrypt_password(key_pass: str, encrypted_pass: bytes) -> str:
        key_pass_bytes = (
            sha256(key_pass.encode("utf-8"))
            .hexdigest()[: len(encrypted_pass)]
            .encode("utf-8")
        )
        return bytes(x ^ y for x, y in zip(key_pass_bytes, encrypted_pass)).decode(
            "utf-8"
        )
