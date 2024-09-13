import cv2
import cvzone
import time
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot

# open a connection to the webcam (0 is the default camera)
cap = cv2.VideoCapture(0) # testing file -> 'test_morse_code.mp4', 'hello_morse_code.mp4', replace 0 if webcam not working

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

# Calibration variables
calibrating = True
calibration_frames = 10 # number of frames for calibration
open_eye_ratios = []  # to collect open eye ratios
blink_ratios = []  # to collect blink ratios
calibrated_threshold = None  # to hold the dynamic blink threshold

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

        # Calibration process
        if calibrating:
            print("Caliberating")
            if len(open_eye_ratios) < calibration_frames:
                print(len(open_eye_ratios))
                open_eye_ratios.append(ratioAvg)  # store open eye ratios
            elif len(blink_ratios) < calibration_frames:
                print(blink_ratios)
                if ratioAvg > max(open_eye_ratios) * 1.15:  # detect blink
                    blink_ratios.append(ratioAvg)  # store blink ratios
            else:
                # calculate threshold dynamically (avg of open eye and blink)
                open_eye_avg = sum(open_eye_ratios) / len(open_eye_ratios)
                blink_avg = sum(blink_ratios) / len(blink_ratios)
                calibrated_threshold = (open_eye_avg + blink_avg) / 2
                calibrating = False
                print(f"Calibration done. Open eye: {open_eye_avg}, Blink: {blink_avg}, Threshold: {calibrated_threshold}")

        if not calibrating and calibrated_threshold is not None:
            # detect blink when the average ratio exceeds calibrated threshold
            if ratioAvg > calibrated_threshold:  
                if blinkStart == 0:  # start the timer for the blink
                    blinkStart = time.time()
                counter = 1  # set the counter flag
            else:
                if blinkStart != 0:  # if blink ends
                    blinkDuration = time.time() - blinkStart  # calculate blink duration
                    blinkStart = 0  # reset the timer

                    # classify the blink as "Long" or "Short"
                    if 0.75 <= blinkDuration:
                        blinks.append("Long")
                    elif blinkDuration < 0.75:
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