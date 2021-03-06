""" NoiseWizard.py
    Last Modified: 5/25/2020
    Taha Arshad, Tennessee Bonner, Devin Mensah, Khalid Shaik, Collin Vaille

    This file generates random data for the graph so the program can be run without the need for the pi

    Returns random noise to act as a substitute for getNextSample in Data Wizard.
    This is used on projects that run outside of the Pi that still need some kind of data...
    to be plot on the graph for debugging purposes.
"""
import numpy as np
import timeit

#Random initial "baseline" value
nextSample = np.random.uniform(1, 4)

#Used to emulate the timing functionality of DataWizard's getNextSample
timeOfLastSample = timeit.default_timer()

#Generates the next sample
def getNextSample():

    global timeOfLastSample, nextSample

    #Wait until data is ready
    while timeit.default_timer() - timeOfLastSample < 0.001:
        pass

    #Record when we got this sample
    timeOfLastSample = timeit.default_timer()

    #Generate new value
    nextSample += np.random.uniform(-0.2, 0.2)

    #Make sure value is within range
    nextSample = clamp(value = nextSample, minimum = 0, maximum = 5)

    return nextSample


def onTrialStart():
    pass


def setCSAmplitude(high):
    pass


def setUSAmplitude(high):
    pass


def clamp(value, minimum, maximum):
    return min(maximum, max(minimum, value))
