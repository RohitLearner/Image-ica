'''
Base program
'''
import sys

from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import QFileInfo

from functools import partial

from img_modifier import img_helper
from img_modifier import color_filter

from PIL import ImageQt
from PIL import Image

from logging.config import fileConfig
import logging
import numpy as np
import os, os.path

logger = logging.getLogger()

# original img, can't be modified
_img_original = None
_img_preview = None
_img_path = None

# constants
THUMB_BORDER_COLOR_ACTIVE = "#3893F4"
THUMB_BORDER_COLOR = "#ccc"
BTN_MIN_WIDTH = 120
ROTATION_BTN_SIZE = (70, 30)
THUMB_SIZE = 120

SLIDER_MIN_VAL = -99
SLIDER_MAX_VAL = 100
SLIDER_DEF_VAL = 0

##
# @brief Class for image ooperations
#
# @details
# This class defines operations on images
#
class Operations:

##
# @brief Initalization of Class Operations.
#
# @details
# This function applies initialises default values to Class Operations.
#
# @param[in] class of _main_.(ClassName)
# @return Void
    def __init__(self):
        self.color_filter = None

        self.flip_left = False
        self.flip_top = False
        self.rotation_angle = 0

        self.size = None

        self.brightness = 0
        self.sharpness = 0
        self.contrast = 0

        self.red = 1
        self.green = 1
        self.blue = 1

        self.red_prev = 1
        self.green_prev = 1
        self.blue_prev = 1

##
# @brief Resetting of Class Operations.
#
# @details
# This function initialise back default values to Class Operations.
#
# @param[in] class of _main_.(ClassName)
# @return Void
    def reset(self):
        self.color_filter = None

        self.brightness = 0
        self.sharpness = 0
        self.contrast = 0

        self.size = None

        self.flip_left = False
        self.flip_top = False
        self.rotation_angle = 0

        self.red = 1
        self.green = 1
        self.blue = 1

        self.red_prev = 1
        self.green_prev = 1
        self.blue_prev = 1

##
# @brief Check changes in Image.
#
# @details
# This function check if there is any change made in the image
#
# @param[in] class of _main_.(ClassName)
# @return Any int value if there is change in image otherwise default value.
    def has_changes(self):
        return self.color_filter or self.flip_left \
               or self.flip_top or self.rotation_angle \
               or self.contrast or self.brightness \
               or self.sharpness or self.size


operations = Operations()

##
# @brief Give int vaule of height ratio.
#
# @details
# This function evaluate the value of the height ratio.
#
# @param[in] class of _main_.(ClassName)
# @return Int value of ratio of height.
def _get_ratio_height(width, height, r_width):
    return int(r_width / width * height)

##
# @brief Give int vaule of width ratio.
#
# @details
# This function evaluate the value of the width ratio.
#
# @param[in] class of _main_.(ClassName)
# @return Int value of ratio of width.
def _get_ratio_width(width, height, r_height):
    return int(r_height / height * width)

##
# @brief Give int vaule of height ratio.
#
# @details
# This function evaluate the value of the height ratio.
#
# @note  convert user ui slider selected value (x) to PIL value user ui slider scale is -100 to 100, PIL scale is -1 to 2
# @param[in] class of _main_.(ClassName)
# @return Int value of ratio of height.
# @example      - user selected 50
#               - PIL value is 1.25   


##
# @brief Give value of factor based on slider dragged by user.
#
# @details
# This function evaluate the new value of factor based on length to which cursor is dragged by user to perform intensity of operation.
#        
# @param[in] SLIDER_MIN_VAL p1
# @param[in] SLIDER_MAX_VA p2
# @param[in] Operation factor MIN p1
# @param[in] Operation factor MAX p2
# @param[in] SLIDER CURRENT VALUE
# @return Int value of factor.
def _get_converted_point(user_p1, user_p2, p1, p2, x):

    r = (x - user_p1) / (user_p2 - user_p1)
    return p1 + r * (p2 - p1)

##
# @brief Performing operation on image.
#
# @details
# This function perform operations like brightness, contrast and sharpness.
#        
# @return New Image.
def _get_img_with_all_operations():
    b = operations.brightness
    c = operations.contrast
    s = operations.sharpness

    img = _img_preview
    if b != 0:
        img = img_helper.brightness(img, b)

    if c != 0:
        img = img_helper.contrast(img, c)

    if s != 0:
        img = img_helper.sharpness(img, s)

    if operations.rotation_angle:
        img = img_helper.rotate(img, operations.rotation_angle)

    if operations.flip_left:
        img = img_helper.flip_left(img)

    if operations.flip_top:
        img = img_helper.flip_top(img)

    if operations.size:
        img = img_helper.resize(img, *operations.size)

    if operations.red != operations.red_prev:
        img = img_helper.hist_red(img, operations.red, operations.red_prev)
        operations.red_prev = operations.red

    if operations.green != operations.green_prev:
        img = img_helper.hist_green(img, operations.green, operations.green_prev)
        operations.green_prev = operations.green

    if operations.blue != operations.blue_prev:
        img = img_helper.hist_blue(img, operations.blue, operations.blue_prev)
        operations.blue_prev = operations.blue

    return img

##
# @brief Create various buttons needed for GUI. 
#
# @details Create different buttons that are used in the GUI for user to allow to perform different operation.
# 
#        
# @param[in] name of button
# @param[in] minimum width of button
# @param[in] function to which button is connected.
# @param[in] status of button
# @param[in] style needed for button 
# @example self.encryption_btn = create_button("One Click Encryption", BTN_MIN_WIDTH + 10, self.encrypt, True,
#                                            "font-weight:bold;")    
#
# @return Object of type QToolButton.
def create_button(name, minWidth, connectFunction, enablestatus, stylesheet):
    btnLoad = QtWidgets.QToolButton()
    btnLoad.setText(name)
    btnLoad.clicked.connect(connectFunction)
    btnLoad.setEnabled(enablestatus)
    btnLoad.setMinimumWidth(minWidth)
    btnLoad.setStyleSheet("background-color:#BCB281; color: #202927;")
    return btnLoad

##
# @brief Create slider needed for GUI. 
#
# @details Create slider that are used in the GUI for user to navigate.
# 
# @param[in] Object of type QWidget
# @param[in] function to which slider is connected.
# @example self.contrast_slider = create_slider(self, self.on_contrast_slider_released)
#
# @return Object of type QSlider
def create_slider(obj, connectFunction):
    obj.slider = QSlider(Qt.Horizontal, obj)
    obj.slider.setMinimum(SLIDER_MIN_VAL)
    obj.slider.setMaximum(SLIDER_MAX_VAL)
    obj.slider.sliderReleased.connect(connectFunction)
    obj.slider.setToolTip(str(SLIDER_MAX_VAL))
    return obj.slider

##
# @brief Class for layout
#
# @details
# This class defines layout features of respective feaatures
#

class ActionTabs(QTabWidget):
    """Action tabs widget"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.filters_tab = FiltersTab(self)
        self.adjustment_tab = AdjustingTab(self)
        self.modification_tab = ModificationTab(self)
        self.rotation_tab = RotationTab(self)
        self.histogram_tab = HistogramTab(self)
        self.security_tab = SecurityTab(self)
        self.miscellaneous_tab = MiscellaneousTab(self)

        self.addTab(self.filters_tab, "Filters")
        self.addTab(self.adjustment_tab, "Adjust")
        self.addTab(self.modification_tab, "Resize")
        self.addTab(self.rotation_tab, "Rotation")
        self.addTab(self.histogram_tab, "Histogram")
        self.addTab(self.security_tab, "Security")
        self.addTab(self.miscellaneous_tab, "Miscellaneous")

        self.setMaximumHeight(160)

##
# @brief Class for adjustment features
#
# @details
# This class defines adjustment features like contrast
#

class RotationTab(QWidget):
    """Rotation tab widget"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        rotate_left_btn = QPushButton("↺ 90°")
        rotate_left_btn.setMinimumSize(*ROTATION_BTN_SIZE)
        rotate_left_btn.clicked.connect(self.on_rotate_left)

        rotate_right_btn = QPushButton("↻ 90°")
        rotate_right_btn.setMinimumSize(*ROTATION_BTN_SIZE)
        rotate_right_btn.clicked.connect(self.on_rotate_right)

        flip_left_btn = QPushButton("⇆")
        flip_left_btn.setMinimumSize(*ROTATION_BTN_SIZE)
        flip_left_btn.clicked.connect(self.on_flip_left)

        flip_top_btn = QPushButton("↑↓")
        flip_top_btn.setMinimumSize(*ROTATION_BTN_SIZE)
        flip_top_btn.clicked.connect(self.on_flip_top)

        rotate_lbl = QLabel("Rotate")
        rotate_lbl.setAlignment(Qt.AlignCenter)
        rotate_lbl.setFixedWidth(140)

        flip_lbl = QLabel("Flip")
        flip_lbl.setAlignment(Qt.AlignCenter)
        flip_lbl.setFixedWidth(140)

        lbl_layout = QHBoxLayout()
        lbl_layout.setAlignment(Qt.AlignCenter)
        lbl_layout.addWidget(rotate_lbl)
        lbl_layout.addWidget(flip_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(rotate_left_btn)
        btn_layout.addWidget(rotate_right_btn)
        btn_layout.addWidget(QVLine())
        btn_layout.addWidget(flip_left_btn)
        btn_layout.addWidget(flip_top_btn)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(lbl_layout)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def on_rotate_left(self):
        logger.debug("rotate left")

        operations.rotation_angle = 0 if operations.rotation_angle == 270 else operations.rotation_angle + 90
        self.parent.parent.place_preview_img()

    def on_rotate_right(self):
        logger.debug("rotate left")

        operations.rotation_angle = 0 if operations.rotation_angle == -270 else operations.rotation_angle - 90
        self.parent.parent.place_preview_img()

    def on_flip_left(self):
        logger.debug("flip left-right")

        operations.flip_left = not operations.flip_left
        self.parent.parent.place_preview_img()

    def on_flip_top(self):
        logger.debug("flip top-bottom")

        operations.flip_top = not operations.flip_top
        self.parent.parent.place_preview_img()

##
# @brief Class for modifying images
#
# @details
# This class defines modification features like changng dimensions of images
#

class ModificationTab(QWidget):
    """Modification tab widget"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.width_lbl = QLabel('width:', self)
        self.width_lbl.setFixedWidth(100)

        self.height_lbl = QLabel('height:', self)
        self.height_lbl.setFixedWidth(100)

        self.width_box = QLineEdit(self)
        self.width_box.textEdited.connect(self.on_width_change)
        self.width_box.setMaximumWidth(100)

        self.height_box = QLineEdit(self)
        self.height_box.textEdited.connect(self.on_height_change)
        self.height_box.setMaximumWidth(100)

        self.unit_lbl = QLabel("px")
        self.unit_lbl.setMaximumWidth(50)

        self.ratio_check = QCheckBox('aspect ratio', self)
        self.ratio_check.stateChanged.connect(self.on_ratio_change)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setFixedWidth(90)
        self.apply_btn.clicked.connect(self.on_apply)

        width_layout = QHBoxLayout()
        width_layout.addWidget(self.width_box)
        width_layout.addWidget(self.height_box)
        width_layout.addWidget(self.unit_lbl)

        apply_layout = QHBoxLayout()
        apply_layout.addWidget(self.apply_btn)
        apply_layout.setAlignment(Qt.AlignRight)

        lbl_layout = QHBoxLayout()
        lbl_layout.setAlignment(Qt.AlignLeft)
        lbl_layout.addWidget(self.width_lbl)
        lbl_layout.addWidget(self.height_lbl)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        main_layout.addLayout(lbl_layout)
        main_layout.addLayout(width_layout)
        main_layout.addWidget(self.ratio_check)
        main_layout.addLayout(apply_layout)

        self.setLayout(main_layout)

    def set_boxes(self):
        self.width_box.setText(str(_img_original.width))
        self.height_box.setText(str(_img_original.height))

    def on_width_change(self, e):
        logger.debug(f"type width {self.width_box.text()}")

        if self.ratio_check.isChecked():
            r_height = _get_ratio_height(_img_original.width, _img_original.height, int(self.width_box.text()))
            self.height_box.setText(str(r_height))

    def on_height_change(self, e):
        logger.debug(f"type height {self.height_box.text()}")

        if self.ratio_check.isChecked():
            r_width = _get_ratio_width(_img_original.width, _img_original.height, int(self.height_box.text()))
            self.width_box.setText(str(r_width))

    def on_ratio_change(self, e):
        logger.debug("ratio change")

    def on_apply(self, e):
        logger.debug("apply")

        operations.size = int(self.width_box.text()), int(self.height_box.text())

        self.parent.parent.place_preview_img()

##
# @brief Class for adjustment features
#
# @details
# This class defines adjustment features like contrast
#

class AdjustingTab(QWidget):
    """Adjusting tab widget"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        contrast_lbl = QLabel("Contrast")
        contrast_lbl.setAlignment(Qt.AlignCenter)

        brightness_lbl = QLabel("Brightness")
        brightness_lbl.setAlignment(Qt.AlignCenter)

        sharpness_lbl = QLabel("Sharpness")
        sharpness_lbl.setAlignment(Qt.AlignCenter)

        self.contrast_slider = create_slider(self, self.on_contrast_slider_released)
        self.brightness_slider = create_slider(self, self.on_brightness_slider_released)
        self.sharpness_slider = create_slider(self, self.on_sharpness_slider_released)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(contrast_lbl)
        main_layout.addWidget(self.contrast_slider)

        main_layout.addWidget(brightness_lbl)
        main_layout.addWidget(self.brightness_slider)

        main_layout.addWidget(sharpness_lbl)
        main_layout.addWidget(self.sharpness_slider)

        self.reset_sliders()
        self.setLayout(main_layout)

    def reset_sliders(self):
        self.brightness_slider.setValue(SLIDER_DEF_VAL)
        self.sharpness_slider.setValue(SLIDER_DEF_VAL)
        self.contrast_slider.setValue(SLIDER_DEF_VAL)

    def on_contrast_slider_released(self):
        logger.debug(self.contrast_slider.value())
        self.contrast_slider.setToolTip(str(self.contrast_slider.value()))
        factor = _get_converted_point(SLIDER_MIN_VAL, SLIDER_MAX_VAL, img_helper.CONTRAST_FACTOR_MIN,
                                      img_helper.CONTRAST_FACTOR_MAX, self.contrast_slider.value())
        logger.debug(f"contrast factor: {factor}")
        operations.contrast = factor
        self.parent.parent.place_preview_img()

    def on_brightness_slider_released(self):
        logger.debug(f"brightness selected value: {self.brightness_slider.value()}")
        self.brightness_slider.setToolTip(str(self.brightness_slider.value()))
        factor = _get_converted_point(SLIDER_MIN_VAL, SLIDER_MAX_VAL, img_helper.BRIGHTNESS_FACTOR_MIN,
                                      img_helper.BRIGHTNESS_FACTOR_MAX, self.brightness_slider.value())
        logger.debug(f"brightness factor: {factor}")
        operations.brightness = factor
        self.parent.parent.place_preview_img()

    def on_sharpness_slider_released(self):
        logger.debug(self.sharpness_slider.value())
        self.sharpness_slider.setToolTip(str(self.sharpness_slider.value()))
        factor = _get_converted_point(SLIDER_MIN_VAL, SLIDER_MAX_VAL, img_helper.SHARPNESS_FACTOR_MIN,
                                      img_helper.SHARPNESS_FACTOR_MAX, self.sharpness_slider.value())
        logger.debug(f"sharpness factor: {factor}")
        operations.sharpness = factor
        self.parent.parent.place_preview_img()

##
# @brief Class for histogram adjustment
#
# @details
# This class defines histogram adjustments like redness
#

class HistogramTab(QWidget):
    """Histogram tab widget"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        red_lbl = QLabel("Red")
        red_lbl.setAlignment(Qt.AlignCenter)

        green_lbl = QLabel("Green")
        green_lbl.setAlignment(Qt.AlignCenter)

        blue_lbl = QLabel("Blue")
        blue_lbl.setAlignment(Qt.AlignCenter)

        self.red_slider = create_slider(self, self.on_red_slider_released)
        self.green_slider = create_slider(self, self.on_green_slider_released)
        self.blue_slider = create_slider(self, self.on_blue_slider_released)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(red_lbl)
        main_layout.addWidget(self.red_slider)

        main_layout.addWidget(green_lbl)
        main_layout.addWidget(self.green_slider)

        main_layout.addWidget(blue_lbl)
        main_layout.addWidget(self.blue_slider)

        self.reset_sliders()
        self.setLayout(main_layout)

    def reset_sliders(self):
        self.red_slider.setValue(SLIDER_DEF_VAL)
        self.green_slider.setValue(SLIDER_DEF_VAL)
        self.blue_slider.setValue(SLIDER_DEF_VAL)

    def on_red_slider_released(self):
        logger.debug(f"red selected value: {self.red_slider.value()}")
        self.red_slider.setToolTip(str(self.red_slider.value()))
        factor = (self.red_slider.value() + SLIDER_MAX_VAL) / SLIDER_MAX_VAL
        logger.debug(f"red factor: {factor}")
        operations.red = factor
        self.parent.parent.place_preview_img()

    def on_green_slider_released(self):
        logger.debug(f"green selected value: {self.green_slider.value()}")
        self.green_slider.setToolTip(str(self.green_slider.value()))
        factor = (self.green_slider.value() + SLIDER_MAX_VAL) / SLIDER_MAX_VAL
        logger.debug(f"green factor: {factor}")
        operations.green = factor
        self.parent.parent.place_preview_img()

    def on_blue_slider_released(self):
        logger.debug(f"blue selected value: {self.blue_slider.value()}")
        self.blue_slider.setToolTip(str(self.blue_slider.value()))
        factor = (self.blue_slider.value() + SLIDER_MAX_VAL) / SLIDER_MAX_VAL
        logger.debug(f"blue factor: {factor}")
        operations.blue = factor
        self.parent.parent.place_preview_img()


class FiltersTab(QWidget):
    """Color filters widget"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.main_layout = QHBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.add_filter_thumb("none")
        for key, val in color_filter.ColorFilters.filters.items():
            self.add_filter_thumb(key, val)

        self.setLayout(self.main_layout)

    def add_filter_thumb(self, name, title=""):
        logger.debug(f"create lbl thumb for: {name}")

        thumb_lbl = QLabel()
        thumb_lbl.name = name
        thumb_lbl.setStyleSheet("border:2px solid #ccc;")

        if name != "none":
            thumb_lbl.setToolTip(f"Apply <b>{title}</b> filter")
        else:
            thumb_lbl.setToolTip('No filter')

        thumb_lbl.setCursor(Qt.PointingHandCursor)
        thumb_lbl.setFixedSize(THUMB_SIZE, THUMB_SIZE)
        thumb_lbl.mousePressEvent = partial(self.on_filter_select, name)

        self.main_layout.addWidget(thumb_lbl)

    def on_filter_select(self, filter_name, e):
        logger.debug(f"apply color filter: {filter_name}")

        global _img_preview
        if filter_name != "none":
            _img_preview = img_helper.color_filter(_img_original, filter_name)
        else:
            _img_preview = _img_original.copy()
        operations.color_filter = filter_name
        self.toggle_thumbs()

        self.parent.parent.place_preview_img()

    def toggle_thumbs(self):
        for thumb in self.findChildren(QLabel):
            color = THUMB_BORDER_COLOR_ACTIVE if thumb.name == operations.color_filter else THUMB_BORDER_COLOR
            thumb.setStyleSheet(f"border:2px solid {color};")

##
# @brief Class for security features
#
# @details
# This class defines security features like encryption and decryption
#

class SecurityTab(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.encryption_btn = create_button("One Click Encryption", BTN_MIN_WIDTH + 10, self.encrypt, True,
                                            "font-weight:bold;")
        self.decryption_btn = create_button("One Click Decryption", BTN_MIN_WIDTH + 10, self.decrypt, True,
                                            "font-weight:bold;")

        # Create textbox
        self.textbox1 = QLineEdit(self)
        self.textbox1.move(250, 100)
        self.textbox1.resize(280, 20)
        self.textbox1.setPlaceholderText("Password Here")

        # Create textbox
        self.textbox2 = QLineEdit(self)
        self.textbox2.move(540, 100)
        self.textbox2.resize(280, 20)
        self.textbox2.setPlaceholderText("New File Name (without any extension)")

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(self.encryption_btn)
        btn_layout.addWidget(self.decryption_btn)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def encrypt(self):
        textboxValue1 = self.textbox1.text()
        textboxValue2 = self.textbox2.text()
        h = SHA256.new()
        password = textboxValue1.encode()
        h.update(password)
        hash = h.digest()
        key = hash[:16]
        iv = hash[16:]
        logger.debug(_img_path)
        ext = _img_path.split(os.path.sep)[-1].split('.')[-1]
        padding = 8 - len(ext)
        message = ext.encode() + (chr(padding) * padding).encode()
        with open(_img_path, "rb") as f:
            message += f.read()
        aes = AES.new(key, AES.MODE_CBC, iv)
        cipher = aes.encrypt(pad(message, AES.block_size))
        with open((os.path.sep).join(_img_path.split(os.path.sep)[:-1]) + os.path.sep + textboxValue2 + ".ima",
                  "wb") as f:
            f.write(cipher)

    def decrypt(self):
        textboxValue1 = self.textbox1.text()
        textboxValue2 = self.textbox2.text()
        h = SHA256.new()
        password = textboxValue1.encode()
        h.update(password)
        hash = h.digest()
        key = hash[:16]
        iv = hash[16:]
        logger.debug(_img_path)
        with open(_img_path, "rb") as f:
            cipher = f.read()
        aes = AES.new(key, AES.MODE_CBC, iv)
        message = aes.decrypt(cipher)
        message = unpad(message, AES.block_size)
        ext = message[:8 - message[7]]
        message = message[8:]
        with open(
                os.path.sep.join(_img_path.split(os.path.sep)[:-1]) + os.path.sep + textboxValue2 + "." + ext.decode(),
                "wb") as f:
            f.write(message)

##
# @brief Class for miscellaneous purposes
#
# @details
# This class defines miscellaeneous features like color pop
#

class MiscellaneousTab(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.colorpop_btn = create_button("Color Pop", BTN_MIN_WIDTH, self.on_colorpop, True, "font-weight:bold;")

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(self.colorpop_btn)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def on_colorpop(self):
        self.parent.parent.captureMouseClick = True
        pass

##
# @brief Photo display class
#
# @details
# This class defines the environment for the dosplay of the image
#

class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        self.parent = parent

        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(222, 214, 181)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse() and self.parent.captureMouseClick:
            print(self.mapToScene(event.pos()).toPoint())
            x = self.mapToScene(event.pos()).toPoint().x()
            y = self.mapToScene(event.pos()).toPoint().y()

            global _img_preview
            im = np.array(_img_preview)
            im2 = im[:, :, :]
            arr = im[y, x, :]

            _img_preview = img_helper.color_filter(_img_preview, "gray")
            im = np.array(_img_preview)
            im[:, :] = np.where(im2[:, :] == arr, arr, im[:, :])
            _img_preview = Image.fromarray(im)
            preview_pix = ImageQt.toqpixmap(_img_preview)
            self.setPhoto(preview_pix)

            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
            self.parent.captureMouseClick = False
        super(PhotoViewer, self).mousePressEvent(event)

##
# @brief Base class
#
# @details
# This class defines the basic UI structure for other components.
#

class ImageicaUI(QtWidgets.QWidget):
    """Main widget"""

    def __init__(self):
        super(ImageicaUI, self).__init__()
        self.captureMouseClick = False
        self._empty = False
        self.image_list = []
        self.name = None

        self.viewer = PhotoViewer(self)
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)

        self.action_tabs = ActionTabs(self)
        VBlayout.addWidget(self.action_tabs)
        self.action_tabs.setVisible(False)

        self.file_name = None
        self.path = os.getcwd()

        self.load_btn = create_button("Load", BTN_MIN_WIDTH, self.on_load, True, "font-weight:bold;")
        self.Next_btn = create_button("Next", BTN_MIN_WIDTH, self.next_image, False, "font-weight:bold;")
        self.Previous_btn = create_button("Previous", BTN_MIN_WIDTH, self.previous_image, False, "font-weight:bold;")
        self.reset_btn = create_button("Reset", BTN_MIN_WIDTH, self.on_reset, False, "font-weight:bold;")
        self.save_btn = create_button("Save", BTN_MIN_WIDTH, self.on_save, False, "font-weight:bold;")

        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.addWidget(self.load_btn)
        HBlayout.addWidget(self.reset_btn)
        HBlayout.addWidget(self.Previous_btn)
        HBlayout.addWidget(self.Next_btn)
        HBlayout.addWidget(self.save_btn)
        VBlayout.addLayout(HBlayout)

        self.setMinimumSize(600, 500)
        self.setMaximumSize(1300, 1600)
        self.setGeometry(1000, 1000, 1100, 650)
        self.setWindowTitle('Image-ica : The Photo Viewer & Editor')
        self.center()
        self.setStyleSheet("background-color:#DED6B5;")
        self.setWindowIcon(QIcon('icon.png'))
        self.show()

    def center(self):
        """align window center"""

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        logger.debug("close")

        if operations.has_changes():
            reply = QMessageBox.question(self, "",
                                         "You have unsaved changes<br>Are you sure you want to Exit?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def resizeEvent(self, e):
        pass

    def place_preview_img(self):
        img = _get_img_with_all_operations()

        preview_pix = ImageQt.toqpixmap(img)
        self.viewer.setPhoto(preview_pix)

    def on_save(self):
        logger.debug("open save dialog")
        new_img_path, _ = QtWidgets.QFileDialog.getSaveFileName(None,
                                                                "QFileDialog.getSaveFileName()",
                                                                f"ez_pz_{self.name}",
                                                                "Images (*.png *.jpg *.ima)")

        if new_img_path:
            logger.debug(f"save output image to {new_img_path}")
            img = _get_img_with_all_operations()
            img.save(new_img_path)

    def on_nothing(self):
        pass

    def next_image(self):
        logger.debug("Next")
        ind = self.image_list.index(self.name)
        if ind + 1 != len(self.image_list):
            if operations.has_changes():
                reply = QMessageBox.question(win, "",
                                             "You have unsaved changes<br>Do you want to save?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    self.on_save()
            operations.reset()
            self.path = self.image_list[ind + 1]
            self.load_image(self.path)
        else:
            self.Next_btn.setEnabled(False)
        self.Previous_btn.setEnabled(True)

    def previous_image(self):
        logger.debug("Previous")
        ind = self.image_list.index(self.name)
        if ind - 1 >= 0:
            if operations.has_changes():
                reply = QMessageBox.question(win, "",
                                             "You have unsaved changes<br>Do you want to save?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    self.on_save()
            operations.reset()
            self.path = self.image_list[ind - 1]
            self.load_image(self.path)
        else:
            self.Previous_btn.setEnabled(False)
        self.Next_btn.setEnabled(True)

    def on_load(self):
        logger.debug("load")
        img_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Open image",
                                                            self.path, "Images (*.png *.jpg *.ima)")

        if img_path:
            logger.debug(f"open file {img_path}")
            self.path = QFileInfo(img_path).path()
            logger.debug(self.path)

            valid_images = [".jpg", ".png", ".ima"]
            for f in os.listdir(self.path):
                ext = os.path.splitext(f)[1]
                if ext.lower() not in valid_images:
                    continue
                self.image_list.append(os.path.join(self.path, f).replace("\\", "/"))

            self.reset_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.Next_btn.setEnabled(True)
            self.Previous_btn.setEnabled(True)

            self.load_image(img_path)

    def load_image(self, img_path):
        self.viewer.setPhoto(QtGui.QPixmap(img_path))
        self._empty = False
        logger.debug(f"open file {img_path}")
        self.name = img_path

        print(self.name)
        global _img_path
        _img_path = self.name
        pix = QPixmap(img_path)
        self.action_tabs.setVisible(True)
        self.action_tabs.adjustment_tab.reset_sliders()
        self.action_tabs.histogram_tab.reset_sliders()

        global _img_original
        _img_original = ImageQt.fromqpixmap(pix)

        if _img_original.width < _img_original.height:
            w = THUMB_SIZE
            h = _get_ratio_height(_img_original.width, _img_original.height, w)
        else:
            h = THUMB_SIZE
            w = _get_ratio_width(_img_original.width, _img_original.height, h)

        img_filter_thumb = img_helper.resize(_img_original, w, h)

        global _img_preview
        _img_preview = _img_original.copy()

        for thumb in self.action_tabs.filters_tab.findChildren(QLabel):
            if thumb.name != "none":
                img_filter_preview = img_helper.color_filter(img_filter_thumb, thumb.name)
            else:
                img_filter_preview = img_filter_thumb

            preview_pix = ImageQt.toqpixmap(img_filter_preview)
            thumb.setPixmap(preview_pix)

        self.action_tabs.modification_tab.set_boxes()

    def on_reset(self):
        logger.debug("reset all")

        global _img_preview
        _img_preview = _img_original.copy()

        operations.reset()

        self.action_tabs.filters_tab.toggle_thumbs()
        self.place_preview_img()
        self.action_tabs.adjustment_tab.reset_sliders()
        self.action_tabs.histogram_tab.reset_sliders()
        self.action_tabs.modification_tab.set_boxes()

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode() == QtWidgets.QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))

##
# @brief Add vertical line to UI
#

class QVLine(QFrame):
    """Vertical line"""

    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


if __name__ == '__main__':
    fileConfig('logging_config.ini')

    app = QApplication(sys.argv)
    win = ImageicaUI()
    win.showMaximized()
    sys.exit(app.exec_())
