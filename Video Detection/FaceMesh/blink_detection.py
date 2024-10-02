import cv2
import cvzone
import time
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot

# open a connection to the webcam (0 is the default camera)
cap = cv2.VideoCapture('hello_morse_code_freezeframe.mov') # testing file -> 'test_morse_code.mp4', replace 0 if webcam not working

# using FaceMesh detector
detector = FaceMeshDetector(maxFaces=1)

# points on the face mesh to detect the eyes
idList = [22, 23, 24, 26, 110, 130, 157, 158, 159, 160, 161, 243]

# live plot to visualize eye opening ratio
graph = LivePlot(1920//3, 1080//3, [280, 400])
ratioList = []  # store eye opening ratios

counter = 0
blinkStart = 0  # store the start time of a blink
blinks = []  # list to store blink types ("Long" or "Short")

# check if the webcam is opened correctly
if not cap.isOpened():
    print("error: could not open webcam.")
    exit()

while True:
    # read a frame from the webcam
    success, frame = cap.read()

    # if frame is not captured successfully, exit the loop
    if not success:
        print("error: could not read frame.")
        break

    # flip the frame horizontally
    # frame = cv2.flip(frame, 1)

    # detect the face mesh and get landmarks
    frame, landmarks = detector.findFaceMesh(frame, draw=False)

    if landmarks:
        face = landmarks[0]

        # draw circles on eye landmarks
        for id in idList:
            cv2.circle(frame, face[id], 2, (0, 255, 0), cv2.FILLED)

        # get positions of key landmarks for eyes
        up = face[159]
        down = face[23]
        left = face[130]
        right = face[243]

        # calculate height and width of the eye
        height, _ = detector.findDistance(up, down)
        width, _ = detector.findDistance(left, right)

        # draw lines to visualize eye height and width
        cv2.line(frame, up, down, (255, 0, 0), 2)
        cv2.line(frame, left, right, (255, 0, 0), 2)

        # calculate eye opening ratio
        ratio = (width / height) * 100
        ratioList.append(ratio)

        # limit ratio list to the last 4 values
        if len(ratioList) > 4:
            ratioList.pop(0)

        # calculate average ratio
        ratioAvg = sum(ratioList) / len(ratioList)

        # update the live plot with the average ratio
        ratioPlot = graph.update(ratioAvg)

        # resize the frame to a smaller size for better viewing
        frame = cv2.resize(frame, (1920 // 3, 1080 // 3))

        # stack the frame and plot together
        stack = cvzone.stackImages([frame, ratioPlot], 2, 1)

        # detect blink when the average ratio is high (eyes closed)
        if ratioAvg > 240:  
            if blinkStart == 0:  # start the timer for the blink
                blinkStart = time.time()
            counter = 1  # set the counter flag
        else:
            if blinkStart != 0:  # if blink ends
                blinkDuration = time.time() - blinkStart  # calculate how long the blink lasted
                blinkStart = 0  # reset the timer

                # classify the blink as "Long" or "Short"
                if 0.7 <= blinkDuration:
                    blinks.append("Long")
                elif blinkDuration < 0.7:
                    blinks.append("Short")

                # print the list of blinks
                print(blinks)

            counter = 0

    else:
        print("no landmarks found")

    # display the frame and plot
    cv2.imshow('Stacked Images', stack)

    # break the loop if the user presses 'q'
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# release the webcam and close the window
cap.release()
cv2.destroyAllWindows()