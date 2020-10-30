import base64
import io
import zipfile

def unzip_string(buf):
    buf = base64.b64decode(buf)
    in_ = io.BytesIO()
    in_.write(buf)
    in_.seek(0)
    with zipfile.ZipFile(file=in_) as zf:
        filename = zf.namelist()[0]
        result = zf.read(filename)
    return result