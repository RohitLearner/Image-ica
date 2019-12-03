"""
Apply filters to PIL.image
"""

import logging
import numpy as np
from PIL import Image
import sys

##
# @var logger
# Contains logging information.
# @hideinitializer
#

logger = logging.getLogger()

##
# @brief Choice of filters to use
#
# @details
# This class defines filters to set on images such as Sepia, Negative and Greyscale
#

class ColorFilters:

    ##
    # @var filters
    # Dictionary containing list of filters
    # @hideinitializer
    #

    filters = {"sepia": "Sepia", "negative": "Negative", "black_white": "Black & White", "gray": "Gray"}

    ##
    # @var SEPIA
    # Sepia filter
    # @hideinitializer
    #
    
    SEPIA = "sepia"
    
    ##
    # @var NEGATIVE
    # Negative filter
    # @hideinitializer
    #
    
    NEGATIVE = "negative"
    
    ##
    # @var BLACK_WHITE
    # Black and White filter
    # @hideinitializer
    #
    
    BLACK_WHITE = "black_white"
    
    ##
    # @var GRAY
    # Grayscale filter
    # @hideinitializer
    #
    
    GRAY = "gray"

##
# @brief Apply Sepia filter
#
# @details
# This function applies Sepia filter on the supplied image.
#
# @param[in] img Image file
# @return im2 Sepia applied image
#

def sepia(img):
    im = np.array(img)
    im2 = np.zeros(im.shape)
    im2[:, :, 0] = 0.393 * im[:, :, 0] + 0.769 * im[:, :, 1] + 0.189 * im[:, :, 2]
    im2[:, :, 1] = 0.349 * im[:, :, 0] + 0.686 * im[:, :, 1] + 0.168 * im[:, :, 2]
    im2[:, :, 2] = 0.272 * im[:, :, 0] + 0.534 * im[:, :, 1] + 0.131 * im[:, :, 2]
    im2 = np.where(im2 > 255, 255, im2).astype(np.uint8)
    if im.shape[2] > 3:
        im2[:,:,3:] = im[:,:,3:]
    im2 = Image.fromarray(im2)
    return im2

##
# @brief Apply Black and White filter
#
# @details
# This function applies Black and White filter on the supplied image.
#
# @param[in] img Image file
# @return im2 Black and White applied image
#

def black_white(img):
    im = np.array(img)
    im2 = np.zeros(im.shape)
    im2[:, :, 0] = 0.3 * im[:, :, 0] + 0.59 * im[:, :, 1] + 0.11 * im[:, :, 2]
    im2[:, :, 0] = np.where(im2[:, :, 0] <= 127, 0, 255)
    im2[:, :, 1] = im2[:, :, 2] = im2[:, :, 0]
    if im.shape[2] > 3:
        im2[:, :, 3:] = im[:, :, 3:]
    im2 = Image.fromarray(im2.astype(np.uint8))
    return im2

##
# @brief Apply Negative filter
#
# @details
# This function applies Negative filter on the supplied image.
#
# @param[in] img Image file
# @return im2 Negative applied image
#

def negative(img):
    im = np.array(img)
    im2 = 255 - im
    if im.shape[2] > 3:
        im2[:,:,3:] = im[:,:,3:]
    im2 = im2.astype(np.uint8)
    im2 = Image.fromarray(im2)
    return im2

##
# @brief Apply Greyscale filter
#
# @details
# This function applies Greyscale filter on the supplied image.
#
# @param[in] img Image file
# @return im2 Greyscale applied image
#

def gray(img):
    im = np.array(img)
    im2 = np.zeros(im.shape)
    im2[:, :, 0] = 0.3 * im[:, :, 0] + 0.59 * im[:, :, 1] + 0.11 * im[:, :, 2]
    im2[:, :, 1] = im2[:, :, 2] = im2[:, :, 0]
    if im.shape[2] > 3:
        im2[:, :, 3:] = im[:, :, 3:]
    im2 = im2.astype(np.uint8)
    im2 = Image.fromarray(im2)
    return im2

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
    img_copy = img.copy()
    if filter_name == ColorFilters.SEPIA:
        img_copy = sepia(img_copy)
    elif filter_name == ColorFilters.NEGATIVE:
        img_copy = negative(img_copy)
    elif filter_name == ColorFilters.BLACK_WHITE:
        img_copy = black_white(img_copy)
    elif filter_name == ColorFilters.GRAY:
        img_copy = gray(img_copy)
    else:
        logger.error(f"can't find filter {filter_name}")
        raise ValueError(f"can't find filter {filter_name}")

    return img_copy
