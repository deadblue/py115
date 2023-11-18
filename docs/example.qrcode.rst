============
QRcode Login
============

.. code:: python

    import io
    import typing

    from PIL import Image

    import py115
    from py115.types import LoginTarget, QrcodeStatus


    class QRcode:

        _char_dict = ['\u2588', '\u2584', '\u2580', ' ']
        
        _matrix: typing.List[int]
        _width: int
        _height: int

        @staticmethod
        def _is_black(c: int) -> bool:
            return c < 128

        def __init__(self, img_io: typing.BinaryIO) -> None:
            with Image.open(img_io).convert('L') as img:
                self._parse(img)

        def _parse(self, img: Image.Image):
            width, height = img.size
            # Locate QRcode area
            left, right, upper, lower = -1, -1, -1, -1
            for y in range(height):
                for x in range(width):
                    if QRcode._is_black(img.getpixel((x, y))):
                        left, upper = x, y
                        break
                if left > 0: break
            for x in range(width - 1, left, -1):
                if QRcode._is_black(img.getpixel((x, upper))):
                    right = x
                    break
            for y in range(height - 1, upper, -1):
                if QRcode._is_black(img.getpixel((left, y))):
                    lower = y
                    break
            # Measure dot size
            dot_size = 0
            for step in range(0, right - left + 1):
                pt = img.getpixel((left + step, upper + step))
                if not QRcode._is_black(pt):
                    dot_size = step
                    break
            # Parse QRcode as matrix
            self._matrix = []
            self._width = int((right - left + 1) / dot_size)
            self._height = int((lower - upper + 1) / dot_size)
            for y in range(self._height):
                for x in range(self._width):
                    pt = img.getpixel((
                        left + x * dot_size,
                        upper + y * dot_size
                    ))
                    self._matrix.append(
                        1 if QRcode._is_black(pt) else 0
                    )
        
        def _get_point(self, x: int, y: int) -> int:
            if x < 0 or x >= self._width or y < 0 or y >= self._height:
                return 0
            return self._matrix[y * self._width + x]

        def to_ascii(self, margin: int = 3) -> str:
            buf = []
            for y in range(0, self._height + margin * 2, 2):
                for x in range(0, self._width + margin * 2):
                    dot_1 = self._get_point(x - margin, y - margin)
                    dot_2 = self._get_point(x - margin, y + 1 - margin)
                    code = dot_2 * 2 + dot_1
                    buf.append(QRcode._char_dict[code])
                buf.append('\n')
            return ''.join(buf)


    if __name__ == '__main__':
        cloud = py115.connect()
        
        print('Start QRcode login ...')
        session = cloud.qrcode_login(LoginTarget.Linux)
        qr = QRcode(io.BytesIO(session.image_data))
        print(f'Please scan QRcode: \n{qr.to_ascii()}')
        while True:
            status = cloud.qrcode_poll(session)
            if status == QrcodeStatus.Done:
                print('Login succeeded!')
            elif status == QrcodeStatus.Expired or status == QrcodeStatus.Failed:
                print('Login failed!')
                break
