import png
import uuid

import pyqrcode
from pyqrcode import QRCode


def generate_code():
    return uuid.uuid4().hex[:10].lower()
