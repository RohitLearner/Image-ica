"""
Image operations
"""

##
# @brief Perform Image related operations calling.
#
# @details This program perform calling for different image related operation defined in other files. 
#


from PIL import Image, ImageEnhance
import logging

import img_modifier.color_filter as cf

##
# @brief Logger Function
#
# @details This function creates a new object with name logger.
#
# @note With the logging module imported, you can use something called a “logger” to log messages that you want to see. By default, there are 5 # standard levels indicating the severity of events. Each has a corresponding method that can be used to log events at that level of severity. 
#

logger = logging.getLogger()

##
# @var CONTRAST_FACTOR_MAX
# Maximum contrast factor
# @hideinitializer
#

CONTRAST_FACTOR_MAX = 1.5

##
# @var CONTRAST_FACTOR_MIN
# Minimun contrast factor
# @hideinitializer
#

CONTRAST_FACTOR_MIN = 0.5

##
# @var SHARPNESS_FACTOR_MAX
# Maximum sharpness factor
# @hideinitializer
#

SHARPNESS_FACTOR_MAX = 3

##
# @var SHARPNESS_FACTOR_MIN
# Minimum sharpness factor
# @hideinitializer
#

SHARPNESS_FACTOR_MIN = -1

##
# @var BRIGHTNESS_FACTOR_MAX
# Maximum brightness factor
# @hideinitializer
#

BRIGHTNESS_FACTOR_MAX = 1.5

##
# @var BRIGHTNESS_FACTOR_MIN
# Minimum brightness factor
# @hideinitializer
#

BRIGHTNESS_FACTOR_MIN = 0.5

##
# @var HIST_FACTOR_MAX
# Maximum histogram factor
# @hideinitializer
#

HIST_FACTOR_MAX = 2

##
# @var HIST_FACTOR_MIN
# Minimum histogram factor
# @hideinitializer
#

HIST_FACTOR_MIN = 0.01

##
# @brief Retreive image
#
# @details
# This function opens the image
#
# @param[in] path Image path
# @return Image Image
#

def get_img(path):

    if path == "":
        logger.error("path is empty of has bad format")
        raise ValueError("path is empty of has bad format")

    try:
        return Image.open(path)
    except Exception:
        logger.error(f"can't open the file {path}")
        raise ValueError(f"can't open the file {path}")

##
# @brief Resize image
#
# @details
# This function resizes the image
#
# @param[in] img Image file
# @param[in] width Image width
# @param[in] height Image height
# @return img Resized image
#

def resize(img, width, height):
    """Resize image"""
    return img.resize((width, height))

##
# @brief Rotate image
#
# @details
# This function rotates the image
#
# @param[in] img Image file
# @param[in] angle Angle of rotation
# @return img Rotated image
#

def rotate(img, angle):

    return img.rotate(angle, expand=True)

##
# @brief Apply a filter
#
# @details
# This function applies the chosen filter on the supplied image.
#
# @param[in] img Image file
# @param[in] filter_name Name of filter
# @return img_copy Copy of the image with the applied filter
#

def color_filter(img, filter_name):

    return cf.color_filter(img, filter_name)

##
# @brief Adjust brightness of image
#
# @details
# This function adjusts the brightness of the supplied image.
#
# @param[in] img Image file
# @param[in] factor Brightness factor
# @return img_copy Copy of the image with the adjusted brightness
#

def brightness(img, factor):

    if factor > BRIGHTNESS_FACTOR_MAX or factor < BRIGHTNESS_FACTOR_MIN:
        raise ValueError("factor should be [0-2]")

    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

##
# @brief Adjust contrast of image
#
# @details
# This function adjusts the contrast of the supplied image.
#
# @param[in] img Image file
# @param[in] factor Contrast factor
# @return img_copy Copy of the image with the adjusted contrast
#

def contrast(img, factor):

    if factor > CONTRAST_FACTOR_MAX or factor < CONTRAST_FACTOR_MIN:
        raise ValueError("factor should be [0.5-1.5]")

    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)

##
# @brief Adjust sharpness of image
#
# @details
# This function adjusts the sharpness of the supplied image.
#
# @param[in] img Image file
# @param[in] factor Sharpness factor
# @return img_copy Copy of the image with the adjusted sharpness
#

def sharpness(img, factor):
    if factor > SHARPNESS_FACTOR_MAX or factor < SHARPNESS_FACTOR_MIN:
        raise ValueError("factor should be [0.5-1.5]")

    enhancer = ImageEnhance.Sharpness(img)
    return enhancer.enhance(factor)

##
# @brief Flip image
#
# @details
# This function flips the image horizontally
#
# @param[in] img PIL image
# @return img2 Flipped image
#

def flip_left(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)

##
# @brief Flip image
#
# @details
# This function flips the image vertically
#
# @param[in] img PIL image
# @return img2 Flipped image
#

def flip_top(img):
    return img.transpose(Image.FLIP_TOP_BOTTOM)

##
# @brief Save image
#
# @details
# This function save the image
#
# @param[in] img Image
# @param[in] path Destination path
#

def save(img, path):
    img.save(path)

##
# @brief Retreive image
#
# @details
# This function opens the image
#
# @param[in] img PIL image
# @return img2 Pixel array
#

def open_img(img):
    img.open()

##
# @brief Adjust red histogram of image
#
# @details
# This function adjusts the redness of the supplied image.
#
# @param[in] img Image file
# @param[in] ratio Ratio factor
# @param[in] ratio_prev Previous ratio factor 
# @return img Image with the adjusted redness
#

def hist_red(img, ratio, ratio_prev):
    pix = img.load()
    temp = ratio/ratio_prev
    for i in range(img.width):
        for j in range(img.height):
            pix[i, j] = (int(pix[i, j][0] * temp), pix[i, j][1], pix[i, j][2])
    return img

##
# @brief Adjust green histogram of image
#
# @details
# This function adjusts the greenness of the supplied image.
#
# @param[in] img Image file
# @param[in] ratio Ratio factor
# @param[in] ratio_prev Previous ratio factor 
# @return img Image with the adjusted greenness
#

def hist_green(img, ratio, ratio_prev):
    pix = img.load()
    temp = ratio / ratio_prev
    for i in range(img.width):
        for j in range(img.height):
            pix[i, j] = (pix[i, j][0], int(pix[i, j][1] * temp), pix[i, j][2])
    return img

##
# @brief Adjust blue histogram of image
#
# @details
# This function adjusts the blueness of the supplied image.
#
# @param[in] img Image file
# @param[in] ratio Ratio factor
# @param[in] ratio_prev Previous ratio factor 
# @return img Image with the blueness greenness
#

def hist_blue(img, ratio, ratio_prev):
    pix = img.load()
    temp = ratio / ratio_prev
    for i in range(img.width):
        for j in range(img.height):
            pix[i, j] = (pix[i, j][0], pix[i, j][1], int(pix[i, j][2] * temp))
    return img
