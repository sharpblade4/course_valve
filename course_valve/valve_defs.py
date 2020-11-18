import os

with open(os.path.join(os.path.dirname(__file__), "obfs.txt"), "r") as f:
    target = f.read().strip()

FTP_USER = f"ron_u@{target}.co.il"
TARGET_FILE_NAME = "course.html"
TARGET_PAGE = f"https://{target}.co.il/" + TARGET_FILE_NAME
TARGET_FTP = f"{target}.co.il"
ENCRYPTED_PASSWORD = b"vFP\rU\x07R\x04Cp#6$`w\x02`"
IDENTIFIER = "course-terms-reveal"
NO_IDENTIFIER = "empty-view-title"
OPENED_TEMPLATE_NAME = f"{TARGET_FILE_NAME}.yes"
CLOSED_TEMPLATE_NAME = f"{TARGET_FILE_NAME}.no"
