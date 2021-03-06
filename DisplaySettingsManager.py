""" DisplaySettingsManager.py
    Last Modified: 5/25/2020
    Taha Arshad, Tennessee Bonner, Devin Mensah, Khalid Shaik, Collin Vaille

    This program manages the display settings, but more specifically it does the following:
        1. Managing the pop-up window (in DisplaySettingsWindow.py) for viewing and editing these settings.
        2. Managing the text file (Display Settings.txt) for saving these settings.
        3. Managing the program variables that hold the current state of these settings (ex: dsm.displayRate)
"""
from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog
from enum import Enum
import DisplaySettingsWindow as dsw
import TheGraph as tg
import InputManager as im
import TheSession as ts

#This class contains the Enumerator for what color attribute is being modified
class ColorAttribute(Enum):
    BACKGROUND = 0
    DATA = 1
    TEXT = 2
    STIMULUS = 3
    AXIS = 4
    ONSET = 5
    OFFSET = 6


#Called at the very beginning of the program to load in settings from file
def initialSetUp ():

    global displayRate, antiAliasing, shading, colors, renderOffset

    #Give default values to all settings first (in case loading settings from file fails)
    displayRate = 10    
    antiAliasing = False
    shading = False
    renderOffset = False

    #Default colors for each of the seven color categories
    colors = (QtGui.QColor(255, 255, 255), QtGui.QColor(0, 0, 255), QtGui.QColor(0, 0, 0), QtGui.QColor(75, 75, 75), QtGui.QColor(0, 0, 0), QtGui.QColor(10, 20, 30), QtGui.QColor(120, 120, 135))

    #Then try to read in settings from file...
    try:
        #Open the display settings file in read mode
        displaySettingsFile = open(file = "Display Settings.txt", mode = "r")
    
    #Error opening file
    except Exception as e:
        print("Error opening display settings file...\n")
        print(e) #Detailed error message
        print() #Extra line for spacing
    
    #Executed only if there is no error with opening the file
    else: 

        #Parse line by line for settings
        for line in displaySettingsFile:
            parseDisplaySettingsFileLine(line)

        #Close the file when done to avoid file descriptor memory leaks
        displaySettingsFile.close()


#This function is used to parse a line of the display settings file and load the data into the program
def parseDisplaySettingsFileLine (line):

    global displayRate, antiAliasing, shading, colors, renderOffset

    #Split the line into key/value pair
    keyValuePair = line.split(sep = "=", maxsplit = 2)

    #Not a key/value pair so skip line (probably whitespace or a comment)
    if len(keyValuePair) != 2:
        return

    #Extract key, remove any surrounding whitespace, and make it all lower case (for case insensitivity)
    key = keyValuePair[0].strip().lower()

    #Same for value
    value = keyValuePair[1].strip().lower()

    #Examine key and save corresponding value
    if key == "refresh rate":
        displayRate = int(value)
    elif key == "anti-aliasing":
        antiAliasing = value == "true"
    elif key == "shading":
        shading = value == "true"
    elif key == "background color":
        colors[ColorAttribute.BACKGROUND.value].setNamedColor(value)
    elif key == "data color":
        colors[ColorAttribute.DATA.value].setNamedColor(value)
    elif key == "text color":
        colors[ColorAttribute.TEXT.value].setNamedColor(value)
    elif key == "stimulus color":
        colors[ColorAttribute.STIMULUS.value].setNamedColor(value)
    elif key == "axis color":
        colors[ColorAttribute.AXIS.value].setNamedColor(value)
    elif key == "render offset arrows":
        renderOffset = value == "true"
    elif key == "onset color":
        colors[ColorAttribute.ONSET.value].setNamedColor(value)
    elif key == "offset color":
        colors[ColorAttribute.OFFSET.value].setNamedColor(value)


#Called when "Edit -> Display Settings..." is pressed to pop up the display settings menu
def openDisplaySettingsMenu():

    global displaySettingsWrapper, colorButtons

    #First, pause session so applying any changes don't have a chance of affecting performance
    if im.playMode == im.PlayMode.ACQUISITION and ts.currentSession:
        im.setPlaying(False)

    #Create the display settings menu (using the Qt Designer-generated Ui_displaySettings)
    displaySettingsWindow = QDialog()
    displaySettingsWrapper = dsw.Ui_displaySettingsWindow()
    displaySettingsWrapper.setupUi(displaySettingsWindow)

    #Detects when the "Restore Defaults" or "OK" buttons are pressed respectively (0x08000000 used instead of QtGui.QDialogButtonBox.Reset due to import issues[They are interchangable])
    displaySettingsWrapper.buttonBox.button(0x08000000).clicked.connect(restoreDisplayDefaults)
    displaySettingsWrapper.buttonBox.accepted.connect(saveDisplaySettings)

    #Keep track of the color buttons in tuple format for easier access
    colorButtons = (displaySettingsWrapper.backgroundColorButton, displaySettingsWrapper.dataColorButton, displaySettingsWrapper.textColorButton, displaySettingsWrapper.stimulusColorButton, displaySettingsWrapper.axisColorButton, displaySettingsWrapper.onsetArrowColorButton, displaySettingsWrapper.offsetArrowColorButton)

    #Detects when the color buttons are pressed
    colorButtons[0].clicked.connect(lambda: colorButtonPressed(ColorAttribute.BACKGROUND))
    colorButtons[1].clicked.connect(lambda: colorButtonPressed(ColorAttribute.DATA))
    colorButtons[2].clicked.connect(lambda: colorButtonPressed(ColorAttribute.TEXT))
    colorButtons[3].clicked.connect(lambda: colorButtonPressed(ColorAttribute.STIMULUS))
    colorButtons[4].clicked.connect(lambda: colorButtonPressed(ColorAttribute.AXIS))
    colorButtons[5].clicked.connect(lambda: colorButtonPressed(ColorAttribute.ONSET))
    colorButtons[6].clicked.connect(lambda: colorButtonPressed(ColorAttribute.OFFSET))

    #Make the menu not resizable
    displaySettingsWindow.setFixedSize(displaySettingsWindow.size())

    #Set the values of these settings to the currently selected values
    showDisplaySettings()

    #Display the menu
    displaySettingsWindow.exec()


#Called when "Restore defaults" buttons is pressed on graph display settings menu (restores the display setting defaults)
def restoreDisplayDefaults():

    #display rate box
    displaySettingsWrapper.displayRateSpinBox.setValue(10)

    #extra features
    displaySettingsWrapper.antiAliasingCheckBox.setChecked(False)
    displaySettingsWrapper.shadingCheckBox.setChecked(False)

    #offset arrow rendering
    displaySettingsWrapper.renderOffsetCheckBox.setChecked(False)

    #color buttons
    setButtonColor(displaySettingsWrapper.backgroundColorButton, QtGui.QColor(255, 255, 255)) #background = white
    setButtonColor(displaySettingsWrapper.dataColorButton, QtGui.QColor(0, 0, 255)) #data = blue
    setButtonColor(displaySettingsWrapper.textColorButton, QtGui.QColor(0, 0, 0)) #text = black
    setButtonColor(displaySettingsWrapper.stimulusColorButton, QtGui.QColor(75, 75, 75)) #stimulus = gray
    setButtonColor(displaySettingsWrapper.axisColorButton, QtGui.QColor(0, 0, 0)) #axis = black
    setButtonColor(displaySettingsWrapper.onsetArrowColorButton, QtGui.QColor(10, 20, 30)) #onset arrow = very dark gray
    setButtonColor(displaySettingsWrapper.offsetArrowColorButton, QtGui.QColor(120, 120, 135)) #offset arrow = slate gray


#Saves the display settings
def saveDisplaySettings():

    global displayRate, antiAliasing, shading, colors, renderOffset

    #First, extract display settings from the menu
    displayRate = displaySettingsWrapper.displayRateSpinBox.value()
    antiAliasing = displaySettingsWrapper.antiAliasingCheckBox.isChecked()
    shading = displaySettingsWrapper.shadingCheckBox.isChecked()
    renderOffset = displaySettingsWrapper.renderOffsetCheckBox.isChecked()
    colors = (colorButtons[0].palette().button().color(),
              colorButtons[1].palette().button().color(),
              colorButtons[2].palette().button().color(),
              colorButtons[3].palette().button().color(),
              colorButtons[4].palette().button().color(),
              colorButtons[5].palette().button().color(),
              colorButtons[6].palette().button().color())

    #Then, save settings to file...
    try:
    
        #Open the display settings file in write mode (overwrites anything already in it, no appending)
        displaySettingsFile = open(file = "Display Settings.txt", mode = "w")

    #Error opening the file
    except Exception as e:
        print("Error opening display settings file...\n")
        print(e) #Detailed error message
        print() #Extra empty line for spacing
    
    #Occurs if there are no problems opening the file
    else:
        displaySettingsFile.write("Note: Don't comment this file because it is regenerated on save.")
        displaySettingsFile.write("\n\nrefresh rate = " + str(displayRate))
        displaySettingsFile.write("\n\nanti-aliasing = " + str(antiAliasing))
        displaySettingsFile.write("\nshading = " + str(shading))
        displaySettingsFile.write("\n\nbackground color = " + colors[ColorAttribute.BACKGROUND.value].name())
        displaySettingsFile.write("\ndata color = " + colors[ColorAttribute.DATA.value].name())
        displaySettingsFile.write("\ntext color = " + colors[ColorAttribute.TEXT.value].name())
        displaySettingsFile.write("\nstimulus color = " + colors[ColorAttribute.STIMULUS.value].name())
        displaySettingsFile.write("\naxis color = " + colors[ColorAttribute.AXIS.value].name())
        displaySettingsFile.write("\nrender offset arrows = " + str(renderOffset))
        displaySettingsFile.write("\nonset color = " + colors[ColorAttribute.ONSET.value].name())
        displaySettingsFile.write("\noffset color = " + colors[ColorAttribute.OFFSET.value].name())

        #Close the file when done to avoid file descriptor memory leaks
        displaySettingsFile.close()

    #Finally, apply the settings to the graph
    tg.updateGraphSettings()

#This function fills in the options with the current settings
def showDisplaySettings():

    displaySettingsWrapper.displayRateSpinBox.setValue(displayRate)
    displaySettingsWrapper.antiAliasingCheckBox.setChecked(antiAliasing)
    displaySettingsWrapper.shadingCheckBox.setChecked(shading)
    displaySettingsWrapper.renderOffsetCheckBox.setChecked(renderOffset)

    #Set color to button in background
    for x in range(0, len(colorButtons)):
        setButtonColor(colorButtons[x], colors[x])


#Pulls up color picker for changing the color of the button This function is used by all color buttons, differentiating buttons via parameter
def colorButtonPressed(colorAttribute):

    #Retrieve current color (of type QColor)
    color = colorButtons[colorAttribute.value].palette().button().color()

    #Open color picker (use current color as initial color in color picker)
    color = QtGui.QColorDialog.getColor(initial = color, title = "Select " 
                                        + colorAttribute.name.capitalize() + " Color")
    
    #If the user didn't click cancel on color picker, set color to chosen color
    if color.isValid():
        setButtonColor(colorButtons[colorAttribute.value], color)


#Changes the background color of the button passed in (QPushButton) to the color passed in (QColor)
def setButtonColor(button, color):

    #Change the button color by accessing it's QPalette and changing it's color for the Button role
    palette = button.palette()
    palette.setColor(QtGui.QPalette.Button, color)
    button.setPalette(palette)

    #Required for it to display properly due to weird quirks within PyQt
    button.setAutoFillBackground(True)
    button.setFlat(True)
