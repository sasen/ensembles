from __future__ import division
import pygame
from math import sqrt, tan, pi, log10
from experimenter import *
import random
import time
import sys

COLOR = (0,0,0)
numCircles = 20
DISTANCE = 60
SCREEN_DIAG = 48# 14.1` * 2.52

# Stimulus presentation parameters
NUM_TRIALS = 20 # total number of trials
BLANK_TIME = 500 #in ms, blank screen before each set is displayed
DISPLAY_TIME = 1500 #in ms, duration of each stimulus display


def instruct(drawer, text):
    # display instructions onscreen, then wait for space or return to continue.
    drawer.screenFill((COLOR))
    drawer.writeInstructions(text)
    drawer.screenFlip()
    while True:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                break
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                drawer.screen.fill(COLOR)
                pygame.display.flip()
                return
    pygame.quit()
    sys.exit(0)

def processInput():
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                break 
            if event.key == pygame.K_s:
                return True
            if event.key == pygame.K_d:
                return False            
    pygame.quit()
    sys.exit(0)

def buildRect(drawer, gaussType):
# make a list or array of rectangles
    global pix2cm
    count = 0
    rectangles = []
    setSize = numCircles + setSizeCondition*random.randint(round(-numCircles/3),round(numCircles/3)) ## SS changed
    # setSizeCondition should be 0 or 1; 0 means numCircles, 
    # 1 means uniformly draw in 33% more or less than numCircles 
    for r in range(0,setSize): ## SS changed
        x = random.randint(0, dispSize[0])
        y = random.randint(0, dispSize[1])
        whichMeanToUse = [meanS1, meanS2, meanS3, sampleMean]
        area = 10**random.gauss(whichMeanToUse[gaussType-1], sigma)  # get the right mean for this gaussType
        radiusDeg = float(sqrt(area)/pi)
        radiusCm = DISTANCE*tan(radiusDeg*(pi/180))
        radiusPix = radiusCm*pix2cm
        rectangle = pygame.Rect(x, y, 2*radiusPix, 2*radiusPix)
        rectangles.append(rectangle)

    while not checkOverlap(rectangles) and count <= 1500:
        count += 1
        for rectangle in rectangles:
            rectangle.top = random.randint(0,dispSize[1])
            rectangle.left = random.randint(0,dispSize[0])
    print "trial:%d, count:%d" % (trial, count)
    return rectangles

def drawCircles(drawer, gaussType):
# makes circles
    drawer.screenFill((COLOR))
    drawer.screenFlip()
    rectangles = buildRect(drawer, gaussType)
    for rect in rectangles:
        pygame.draw.circle(drawer.screen, (255,0,0), rect.center, int(rect.width/2), 0)
    return len(rectangles)  ## SS changed. ## SS TODO actually write circle locations!

def checkOverlap(rectangles):
# checks if there is overlap
    for rect in rectangles:
        if len(rect.collidelistall(rectangles)) != 1:
            return False
    return True

def displayText(text, top):
    rect = drawer.screen.get_rect() # returns a rectange of the pygame window starting at topleft (0,0), rightbottom goes all the way FULLSCREEN --- determined in experimenter.py
    rect.top = top # identify this rectangles top position as top instead of specific (0,0)
    drawer.screen.fill(COLOR, rect)
    font = pygame.font.Font(None, 36) # font - namespace / Font - class
    textRect = font.render(text, 1, (255, 255, 255)) # rectangular bitmap for text
    textpos = textRect.get_rect(centerx = drawer.screen.get_rect().centerx) # where the text rectangle will be flipped --- textRect.get_rect() returns the size of the bitmap
    textpos.top = top # set the text bitmap at the same level as rect
    drawer.screen.blit(textRect, textpos) # Block image transfer (combines 2 bitmaps : screen and textRect)  (textRect: bitmap, textpos: position for the)
    pygame.display.flip()

def askQuestion():
    displayText("Are the two sets of circles the same or different?", 450)
    displayText("press (S) if same and (D) if different", 500)
    pygame.event.clear()
    return processInput()


def runTrial(setSizeCondition): ## SS changed
    global trial
    global meanS1, meanS2, meanS3, sigma
    t = pygame.time.get_ticks()
    passed = pygame.time.get_ticks() - t
    trials = [1,1,2,3] 
    trialType = random.choice(trials)
    setSize1 = drawCircles(drawer, 1)
    pygame.time.wait(BLANK_TIME - passed)
    pygame.display.flip()
    pygame.time.wait(DISPLAY_TIME)
    setSize2 = drawCircles(drawer, trialType)
    pygame.time.wait(BLANK_TIME - passed)
    pygame.display.flip()
    pygame.time.wait(DISPLAY_TIME - passed)
    drawer.screenFill((COLOR))
    drawer.screenFlip()
    answer = askQuestion()
    if meanS2 >= log10(8):
        pygame.quit()
        print "CRAP DATA"
        sys.exit(0)
    if trialType == 1:
        f.write("%d, %d, %d, %d, %2f, %2f,%r \n"% (trial, trialType, setSize1, setSize2, 10**meanS1, 10**meanS1, answer)) ## SS changed
        print trial
        print " S1-S1 "
        if answer == True:
            print "correct\n"
        else:
            print "incorrect\n"
    if trialType == 2: 
        f.write("%d, %d, %d, %d, %2f, %2f, %r \n"% (trial, trialType, setSize1, setSize2, 10**meanS1, 10**meanS2, not answer)) ## SS changed
        if answer == True: # incorrect
            meanS2 = max(meanS1, meanS2 + .1*(meanS1)) #meanS2/meanS1
        else:
            meanS2 = max(meanS1, meanS2 - (.1*(meanS1))/3) # meanS2/meanS1
    if trialType == 3:
        f.write("%d, %d, %d, %d, %2f, %2f, %r \n"% (trial, trialType, setSize1, setSize2, 10**meanS1, 10**meanS3, not answer)) ## SS changed
        if answer == True: # incorrect
            meanS3 = min(meanS1, meanS3 - .1*(meanS1))
        else:
            meanS3 = min(meanS1, meanS3 + (.1*(meanS1)/3))
    trial += 1
    return answer

try:
    subject = raw_input("Enter subject ID here: ")
    print "Subject ID is:", subject
    setSizeCondition = int(raw_input("Enter setsize manipulation here: ")) ## SS changed
    if setSizeCondition == 1: ## SS changed
        print "Setsize manipulation is Unequal"
    elif setSizeCondition == 0:
        print "Setsize manipulation is Equal"
    else:
        print "Setsize not understood; please enter 0 or 1." ## SS TODO This should error or reprompt

    drawer = Experimenter()
    instruct(drawer, ['On every trial you will be presented with two displays of circles',
                      'First you will see one set and then you will see another',
                      'You will then be asked if those two displays on average have the same or different MEAN AREAS',
                      'Press "S" for Same and "D" for Different',
                      '',
                      'press "SPACE" or "Enter" to see a sample trial'])
    pix2cm = (sqrt(drawer.screen.get_width()**2 + drawer.screen.get_height()**2))/SCREEN_DIAG
    dispSize = [int(drawer.screen.get_width() * 0.75), int(drawer.screen.get_height() * 0.75)]
    maxArea = (((dispSize[0]*dispSize[1])/numCircles)*2/pi) # max area of a circle
    # ALL MEANS ARE IN PIXEL SQUARED
    meanS1 = 0.4 #log10(2.5) # deg.sqr.
    meanS2 = 0.5 #log10(3) # deg.sqr.
    meanS3 = 0.3 #log10(2) # deg.sqrr.
    sigma = 0.075
    sampleMean = 0.3
    trial = 1
    f = open("datafiles/" + subject + ".txt", 'w')
    f.write("Trial, TrialType, SetSize1, SetSize2, 1st Mean, 2nd Mean, Correct\n") # SS changed
    instruct(drawer, ['Now the actual experiment:',
                      'What you just saw was an exaggerated example to illustate the point and in the experiment the difference will not be as apparent',
                      '',
                      '',
                      'STOP, before you procede...',
		      '',
                      'Please tell the experimenter whether or not you understood the what was meant by "mean area"',
                      '',
                      'Start the experiment by pressing "SPACE" or "ENTER"'])
    while True and trial <= NUM_TRIALS: # SS changed 500
        runTrial(setSizeCondition) ## SS CHANGED
    f.close()
    
finally:
    pygame.quit()


