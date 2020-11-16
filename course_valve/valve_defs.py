import os

with open(os.path.join(os.path.dirname(__file__), "obfs.txt"), "r") as f:
    target = f.read().strip()

FTP_USER = f"ron_u@{target}.co.il"
TARGET_PAGE = f"https://{target}.co.il/course.html"
TARGET_FTP = f"ftp://{target}.co.il/"
ENCRYPTED_PASSWORD = b"vFP\rU\x07R\x04Cp#6$`w\x02`"
TARGET_FILE_NAME = "course.html"
IDENTIFIER = "course-terms-reveal"
OPEN_TEMPLATE_NAME = f"{TARGET_FILE_NAME}.yes"
CLOSED_TEMPLATE_NAME = f"{TARGET_FILE_NAME}.no"
