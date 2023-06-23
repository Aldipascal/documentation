import os
from pathlib import Path

from PIL import Image
import sphinxlint


MAX_IMAGE_SIZES = {  # in bytes
    '.png': 505000,
    '.gif': 2100000,
}

def log_error(file, line, msg, checker_name):
    """ Log an error in sphinx-lint's log format to ease the processing of linting errors on Runbot.
    """
    print(f"{file}:{line or 0}: {msg} ({checker_name})")

def local_run():
    return os.getenv('LOCAL') == '1'

def check_image_size(file):
    """ Check that images are not larger than the maximum file size allowed for their extension. """
    file_path = Path(file)
    file_size = file_path.stat().st_size
    max_size = MAX_IMAGE_SIZES.get(file_path.suffix)
    if max_size and file_size > max_size:
        log_error(
            file_path,
            0,
            f"the file has a size of {round(file_size / 10**6, 2)} MB, larger than the maximum"
            f" allowed size of {round(max_size / 10**6, 2)} MB; compress it with pngquant",
            'image-size',
        )

    if local_run():
        return

    if file_path.suffix == '.png':
        mode_to_bpp = {'1':1, 'L':8, 'P':8, 'RGB':24, 'RGBA':32, 'CMYK':32, 'YCbCr':24, 'I':32, 'F':32}

        data = Image.open(file)
        bpp = mode_to_bpp[data.mode]
        if bpp > 8:
            log_error(
                file_path,
                0,
                "File was not compressed through pngquant, bit depth is still too high.",
                'image-size'
            )

def check_media_name_format(file_path):
    split = file_path.split('/')
    if '_' in split[-1]:
        log_error(
            file_path,
            0,
            "Media name should use hyphens and not underscores",
            'media-name-format'
        )

additional_checkers = [
    check_image_size,
]
if not local_run():
    additional_checkers.append(check_media_name_format)

@sphinxlint.checker('')
def check_file_extensions(file, lines, options=None):
    """ Check that there is no file without extension. """
    yield 0, "the file does not have an extension"
