#######################
# SikuliX Speedrun AutoSplitter by klayveR (reddit.com/u/klayveR) - klayver.de
# Version 1.1.6
# 07/20/2016
#
# Thanks to Titandrake for inspiration: https://www.youtube.com/watch?v=W4sn4yjSosA
# Visit https://www.klayver.de/autosplitter for setup instructions

#######################
### SCRIPT SETTINGS ###
#######################

# gameRegion: The region that the script should scan for pattern matches. Use the GUI Region feature to select your game window
# Usage: Region(x, y, width, height) or simply use GUI feature, replace the whole Region(...) if you do that (Should look like this: https://i.imgur.com/xJ9NpWt.png)
gameRegion = Region(0, 0, 1920, 1080)

# splitPatterns: Patterns (pictures) that the script will look for to make a split, must be in correct order of splits, seperated by comma
# Use Take Screenshot/Insert Image GUI features to add pictures (Should look like this: https://i.imgur.com/tLTOYq5.png)
# Examples: ["split1.png", "split2.png"]
splitPatterns = []

# splitNames (optional): If you want to show split names in the console, add names to splitNames, seperate by comma. Leave empty if you don't need this
# Important: The splitNames array must have the same amount of elements as the splitPatterns array
# Examples: ["Segment 1", "Segment 2"]
splitNames = []

# splitScanRate: How often per second the script should scan the game region, is used for every split
#                Higher scanrate equals more checks per second, but more checks will eat a lot of cpu power
#                Anything higher than 100 will result in continuous checking in most cases
splitScanRate = 25

# minSimilarity: If the pattern matches the region by this value or higher, the split key will be pressed
#                Reduce value if splits aren't firing, increase if you get false matches
minSimilarity = 0.7

# USING THIS OVERRIDES THE splitScanRate VALUE - LEAVE EMPTY IF YOU DON'T NEED THIS
# scanRates (optional): In case you need different scan rates for multiple splits, add a scan rate for each split you have, seperate by comma
#                       This is sometimes necessary in case there is a harder to recognize pattern for certain splits or maybe you want a more accurate detection on the last split
# Important: The scanRates array must have the same amount of elements as the splitPatterns array
# Examples: [15, 50]
scanRates = []

# USING THIS OVERRIDES THE minSimilarity VALUE - LEAVE EMPTY IF YOU DON'T NEED THIS
# minSimilarities (optional): In case you need different minimal similarity values for multiple splits, add a decimal percentage for each split you have, seperate by comma
#                             This can be used to get more reliable results based on the type of pattern
# Important: The minSimilarities array must have the same amount of elements as the splitPatterns array
# Examples: [0.8, 0.5]
minSimilarities = []

# scanAccuracy: A lower value means that the scans are faster, but more inaccurate. Try what works best for you, this changes based on the power of your computer
# Low value for faster processing, increase value if you get false matches
scanAccuracy = 6

# Key configuration: Keys that you are using to make a split/start, reset, unsplit and skip in LiveSplit, SikuliX Key Constants: http://doc.sikuli.org/keys.html
# Examples: Key.NUM0, "5", Key.F5
splitKey = Key.NUM0
resetKey = Key.NUM1
unsplitKey = Key.NUM2
skipKey = Key.NUM3

# startTimerAt: If you use the "Start Timer at" feature in LiveSplit, edit this value accordingly
startTimerAt = 0

# splitDelay: The time in seconds the script should wait before searching for the next pattern after it successfully found the previous split pattern
# skipDelay: The time in seconds the script should wait before searching for the next pattern after skipping a split
# finishDelay: The time in seconds the script should wait after you finished a run
# Important: During the skip and split delay the script is not able to recognize if you press the reset/skip/unsplit keys!
splitDelay = 3
skipDelay = 1
finishDelay = 5

# logRuns: If you want to log your runs, set this to True
logRuns = True
logRunsFile = "runs.log"

# timeNormalisation: If you notice a consistent delay (which is often caused by huge gameRegions, consider changing that first)
#                    in your splits, you can change this to a value, which will then be subtracted from the recorded time
# Notice: This does NOT affect LiveSplits time, only the log and console times of this script!
timeNormalisation = 0.00

###########################
### SCRIPT SETTINGS END ###
###########################

#################################################################
### DONT TOUCH CODE BELOW UNLESS YOU KNOW WHAT YOU'RE DOING   ###
#################################################################

import os
import os.path
import sys
import time
from org.sikuli.natives import Vision

# Sikuli settings
Vision.setParameter("MinTargetSize", scanAccuracy)
Settings.TypeDelay = 0
Settings.ActionLogs = False
Settings.InfoLogs = False
Settings.DebugLogs = False

# Variables
fileName = os.path.basename(sys.argv[0])
fileNameNoExt = fileName.replace(".sikuli", "")
splitCount = len(splitPatterns)
splitNameCount = len(splitNames)
scanRateCount = len(scanRates)
minSimilaritiesCount = len(minSimilarities)
showSplitNames = False
variableScanRates = False
variableMinSimilarities = False
currentlyDelaying = False

allStrings = ""
lastRunTime = 0.0
lastRunTimeMilli = ".00"
startTime = 0.0
longestName = 0

canRun = True
runCount = 0
splitsFound = []
currentSplit = 0
currentSplitRegion = gameRegion

###############
### CONSOLE ###
###############

# Clear windows terminal
# If this causes errors, please remove this line below as well as all clear() function calls in this script
clear = lambda: os.system('cls')

def printStrings(allStrings):
    clear()
    print allStrings
    return

def printString(str, allStrings, br = True, refresh = True):
    if allStrings == "":
        allStrings = str
    else:
        if br == True:
            allStrings = allStrings + "\n" + str
        else:
            allStrings = allStrings + str
    if refresh == True: printStrings(allStrings)
    return allStrings

def printRemainingSplits(split):
    for i in range(split + 1, splitCount):
        if showSplitNames == False:
            print "Split " + str(i + 1)
        else:
            print splitNames[i]

def logRun(str):
    tempStr = str.split("---------------------------")
    str = "---------------------------" + tempStr[1]

    file = open(logRunsFile, "a+")
    if os.stat(logRunsFile).st_size == 0:
        file.write(str + "\n")
    else:
        file.write("\n\n" + str + "\n")
    file.close()
    return

#########################
### CMD FILE CREATION ###
#########################

if not os.path.isfile(fileNameNoExt + "_start.cmd"):
    file = open(fileNameNoExt + "_start.cmd", "w")
    file.write("@ECHO OFF\nstart /i /b /wait runsikulix.cmd -r " + fileName)
    file.close()

    popup("It looks like this is the first time you are starting this script. " + fileNameNoExt + "_start.cmd has been created in your SikuliX directory,\nI recommend to use that to start the Speedrun Autosplitter script in the future in order to see the console and to easily close the script.\n\nThe script will now exit.\nPlease restart it by double-clicking " + fileNameNoExt + "_start.cmd.", "First launch")
    exit()

######################
### SETTINGS CHECK ###
######################

# Check if it's possible to even start a run, there must be at least one split
if splitCount == 0:
    popup("You need to add at least one split pattern, modify splitPatterns in the script\n\nThe script will now exit.", "Error")
    exit()

# Check if split name count match split count, catch errors
if splitNameCount > 0:
    if splitNameCount == splitCount:
        showSplitNames = True
        longestName = 0
        for name in splitNames:
            if len(name) > longestName: longestName = len(name)
    else:
        popup("Count of split names does not match count of splits.\n\nSplit names have been disabled, default names will be used.", "Warning")
        longestName = 7
        if splitCount > 9: longestName = 8

# Check if scan rates count match split count, catch errors
if scanRateCount > 0:
    if scanRateCount == splitCount:
        variableScanRates = True
    else:
        popup("Count of scan rates does not match count of splits.\n\nDisabled variable scan rates. splitScanRate will be used for every split.", "Warning")

# Check if minimum similarity values count match split count, catch errors
if minSimilaritiesCount > 0:
    if minSimilaritiesCount == splitCount:
        variableMinSimilarities = True
    else:
        popup("Count of minimum similarity values does not match count of splits.\n\nDisabled variable minimum similarity values. minSimilarity will be used for every split.", "Warning")

#####################
### RUN FUNCTIONS ###
#####################

# Initialize run
def initRun():
    global allStrings
    global runCount
    global canRun

    canRun = True
    runCount += 1
    allStrings = ""

    # Scan rates
    if variableScanRates == False:
        allStrings = printString("[CONFIG] Constant scan rate: " + str(splitScanRate) + " scans/s", allStrings, True, False)
    else:
        allStrings = printString("[CONFIG] Variable scan rates: " + str(variableScanRates), allStrings, True, False)

    # Min. similarities
    if variableMinSimilarities == False:
        allStrings = printString("[CONFIG] Constant min. similarity: " + str(minSimilarity * 100) + "%", allStrings, True, False)
    else:
        allStrings = printString("[CONFIG] Variable min. similarities: " + str(variableMinSimilarities), allStrings, True, False)

    # Split count
    allStrings = printString("[CONFIG] Split count: " + str(splitCount), allStrings, True, False)
    allStrings = printString("[CONFIG] Split names: " + str(showSplitNames), allStrings, True, False)

    # Write everything to console
    allStrings = printString("", allStrings, False)

    # If ahkSupprt enabled, delete leftover textfiles from previous runs and wait for the user to press the start key
    # If not enabled, run starts immediately
    allStrings = printString("\nRUN #" + str(runCount) + " (Last run: " + time.strftime('%H:%M:%S', time.gmtime(lastRunTime)) + lastRunTimeMilli + ")\n---------------------------", allStrings)
    print "Press your split key to start the run"
    return

# Start run
def startRun(event):
    # New run
    global allStrings
    global canRun
    global startTime
    global currentSplit
    global splitsFound
    global lastRunTime
    global lastRunTimeMilli

    if canRun == True:
        if startTimerAt < 0:
            startTime = time.time() - startTimerAt
        else:
            startTime = time.time() - startTimerAt

        currentSplit = 0
        splitsFound = []
        canRun = False
        lastRunTime = startTime
        lastRunTimeMilli = ".00"

        allStrings = printString("Segment", allStrings)
        for i in range(0, longestName - 7 + 3): allStrings = printString(" ", allStrings, False, False)
        allStrings = printString("Time          Segment Time", allStrings, False, False)

        allStrings = printString("-------", allStrings)
        for i in range(0, longestName - 7 + 2): allStrings = printString("-", allStrings, False, False)
        allStrings = printString(" ------------- ------------", allStrings, False, True)

        nextSplit(currentSplit)

# End run
def finishRun():
    # New run
    global allStrings

    if len(splitsFound) == splitCount:
        printStrings(allStrings)

        allStrings = printString("\nRun finished in " + time.strftime('%H:%M:%S', time.gmtime(lastRunTime)) + lastRunTimeMilli + "!", allStrings)

        # Log run
        if logRuns == True: logRun(allStrings)

    time.sleep(finishDelay)
    initRun()

# Recognized pattern callback
def foundSplit(event):
    global splitsFound
    global allStrings
    global currentlyDelaying
    global lastRunTime
    global lastRunTimeMilli

    if event.getPattern().getImage().getImageName() == splitPatterns[currentSplit]:
        type(splitKey)

        event.stopObserver()

        # Time difference calculation
        newTime = float("{0:.2f}".format(time.time() - startTime - timeNormalisation))
        newTimeMilli = str(newTime - int(newTime))[1:]
        if len(newTimeMilli) == 2: newTimeMilli = newTimeMilli + "0"
        segmentTime = float("{0:.2f}".format(newTime + startTime - lastRunTime))
        segmentTimeMilli = str(segmentTime - int(segmentTime))[1:]
        if len(segmentTimeMilli) == 2: segmentTimeMilli = segmentTimeMilli + "0"
        lastRunTime = newTime + startTime

        # Show final split time in console
        if showSplitNames == False:
            allStrings = printString("Split " + str(currentSplit + 1), allStrings)
            for i in range(0, longestName - 7 + len(str(currentSplit + 1)) + 2): allStrings = printString(" ", allStrings, False, False)
        else:
            allStrings = printString(splitNames[currentSplit], allStrings)
            for i in range(0, longestName - len(splitNames[currentSplit]) + 3): allStrings = printString(" ", allStrings, False, False)

        allStrings = printString(time.strftime('%H:%M:%S', time.gmtime(newTime)) + newTimeMilli + "   " + time.strftime('%M:%S', time.gmtime(segmentTime)) + segmentTimeMilli, allStrings, False, True)

        printRemainingSplits(currentSplit)

        splitsFound.append(currentSplit)
        currentlyDelaying = True

        time.sleep(splitDelay)

        if currentSplit < splitCount - 1:
            nextSplit(currentSplit + 1)
        else:
            lastRunTime = newTime
            lastRunTimeMilli = newTimeMilli
            finishRun()

# Next split
def nextSplit(index):
    global splitsFound
    global currentSplit
    global currentSplitRegion
    global currentlyDelaying

    pattern = splitPatterns[index]
    currentSplit = index

    currentlyDelaying = False

    currentScanRate = splitScanRate
    currentMinSimilarity = minSimilarity

    # Set correct scanrate
    if variableScanRates == True:
        Settings.ObserveScanRate = scanRates[index]
        currentScanRate = scanRates[index]
    else:
        Settings.ObserveScanRate = splitScanRate

    # Set correct min. similarity
    if variableMinSimilarities == True:
        Settings.MinSimilarity = minSimilarities[index]
        currentMinSimilarity = minSimilarities[index]
    else:
        Settings.MinSimilarity = minSimilarity

    region = Region(gameRegion)

    currentSplitRegion = region
    region.onAppear(pattern, foundSplit)
    region.observeInBackground(FOREVER)

    printStrings(allStrings)

    # Show information about current split
    if showSplitNames == False:
        print "Split " + str(index + 1) + "   -> " + str(currentScanRate) + " scans/s, match @ " + str(currentMinSimilarity * 100) + "% similarity"
    else:
        print splitNames[index] + "   -> " + str(currentScanRate) + " scans/s, match @ " + str(currentMinSimilarity * 100) + "% similarity"

    printRemainingSplits(index)

# Reset run
def resetRun(event):
    if (canRun == False) and (currentlyDelaying == False):
        currentSplitRegion.stopObserver()
        initRun()

# Unsplit split
def unsplitSplit(event):
    global splitsFound
    global allStrings

    if (canRun == False) and (currentlyDelaying == False):
        if len(splitsFound) > 0:
            currentSplitRegion.stopObserver()

            if showSplitNames == False:
                allStrings = allStrings.split("\nSplit " + str(currentSplit), 1)[0]
            else:
                allStrings = allStrings.split("\n" + splitNames[currentSplit - 1], 1)[0]

            printRemainingSplits(currentSplit)

            if currentSplit - 1 in splitsFound: splitsFound.remove(currentSplit - 1)
            nextSplit(currentSplit - 1)

# Skip split
def skipSplit(event):
    global splitsFound
    global allStrings
    global currentlyDelaying
    global lastRunTime
    global lastRunTimeMilli

    if (canRun == False) and (currentlyDelaying == False):
        currentSplitRegion.stopObserver()

        # Time difference calculation
        newTime = float("{0:.2f}".format(time.time() - startTime))
        newTimeMilli = str(newTime - int(newTime))[1:]
        if len(newTimeMilli) == 2: newTimeMilli = newTimeMilli + "0"

        if showSplitNames == False:
            allStrings = printString("Split " + str(currentSplit + 1), allStrings)
            for i in range(0, longestName - 7 + len(str(currentSplit + 1)) + 2): allStrings = printString(" ", allStrings, False, False)
        else:
            allStrings = printString(splitNames[currentSplit], allStrings)
            for i in range(0, longestName - len(splitNames[currentSplit]) + 3): allStrings = printString(" ", allStrings, False, False)

        allStrings = printString(time.strftime('%H:%M:%S', time.gmtime(newTime)) + newTimeMilli + "   -", allStrings, False, True)
        printRemainingSplits(currentSplit)

        splitsFound.append(currentSplit)

        currentlyDelaying = True
        time.sleep(skipDelay)

        if currentSplit < splitCount - 1:
            nextSplit(currentSplit + 1)
        else:
            lastRunTime = newTime
            lastRunTimeMilli = newTimeMilli
            finishRun()

###############
### HOTKEYS ###
###############
Env.addHotkey(splitKey, 0, startRun)
Env.addHotkey(resetKey, 0, resetRun)
Env.addHotkey(skipKey, 0, skipSplit)
Env.addHotkey(unsplitKey, 0, unsplitSplit)

############################
### INITIALIZE FIRST RUN ###
############################
initRun()

# Run script forever
while True:
    time.sleep(3600)