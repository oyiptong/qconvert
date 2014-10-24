import logging
import operator
from PIL import Image


logger = logging.getLogger("command")

class ConversionError(Exception): pass


def resize(infilename, scale_factor, width, height, *args, **kwargs):

    dimensions_provided = not (width is None and height is None)
    if not dimensions_provided and scale_factor is None:
        raise ConversionError("Either width and height or scale factor need to be supplied")

    img = Image.open(infilename)
    img_x, img_y = img.size
    logger.info("input: {0} width: {1}px height: {2}px".format(infilename, img_x, img_y))

    if scale_factor:
        new_x, new_y = map(lambda x: operator.mul(x, scale_factor), img.size)
    else:
        new_x = width
        new_y = height

    logger.info("output width:{0}px height: {1}px".format(new_x, new_y))

    img.thumbnail((new_x, new_y))

    return img
