from barcode.writer import BaseWriter, FONT
from PIL import Image, ImageDraw, ImageFont

def mm2px(mm, dpi=300):
    return (mm * dpi) / 25.4


class ImageWithoutTextWriter(BaseWriter):
    def __init__(self, print_text=True):
        BaseWriter.__init__(self, self._init, self._paint_module,
                            self._paint_text, self._finish)
        self.format = 'PNG'
        self.dpi = 300
        self._image = None
        self._draw = None
        self.print_text = print_text

    def _init(self, code):
        size = self.calculate_size(len(code[0]), len(code), self.dpi)
        if not self.print_text:
            size = (size[0], int(size[1] * 0.7))
        self._image = Image.new('RGB', size, self.background)
        self._draw = ImageDraw.Draw(self._image)

    def _paint_module(self, xpos, ypos, width, color):
        size = [(mm2px(xpos, self.dpi), mm2px(ypos, self.dpi)),
                (mm2px(xpos + width, self.dpi),
                 mm2px(ypos + self.module_height, self.dpi))]
        self._draw.rectangle(size, outline=color, fill=color)

    def _paint_text(self, xpos, ypos):
        if self.print_text:
            font = ImageFont.truetype(FONT, self.font_size * 2)
            width, height = font.getsize(self.text)
            pos = (mm2px(xpos, self.dpi) - width // 2,
                   mm2px(ypos, self.dpi) - height // 4)
            self._draw.text(pos, self.text, font=font, fill=self.foreground)

    def _finish(self):
        return self._image
