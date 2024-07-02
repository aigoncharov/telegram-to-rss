import qrcode
from io import BytesIO
from base64 import b64encode


def get_qr_code_image(qr_code: str):
    buffer = BytesIO()
    img = qrcode.make(qr_code)
    img.save(buffer)
    encoded_img = b64encode(buffer.getvalue()).decode()

    data_uri = "data:image/png;base64,{}".format(encoded_img)
    return data_uri
