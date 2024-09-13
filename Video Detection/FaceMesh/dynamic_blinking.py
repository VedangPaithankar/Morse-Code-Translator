import cv2
import time
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot

# open a connection to the webcam or video
cap = cv2.VideoCapture(0)

# initialize face mesh detector, tracking a maximum of 1 face
detector = FaceMeshDetector(maxFaces=1)

# list of landmarks representing the eyes in the face mesh
idList = [22, 23, 24, 26, 110, 130, 157, 158, 159, 160, 161, 243]

# live plot for visualizing the eye opening ratio (for debugging purposes)
graph = LivePlot(1920 // 3, 1080 // 3, [280, 400])
ratioList = []  # list to store eye opening ratios for averaging

# counter and timing variables for blinks
counter = 0
blinkStart = 0  # store the start time of a blink
lastBlinkTime = 0  # store the time of the last blink
blinks = []  # list to store blink types ("long", "short", or "|")

# morse code related variables
morse_sequence = ""  # morse sequence for the current letter
morse_word = ""  # word being formed
letter = ""  # current letter being processed
last_displayed_word = ""  # to keep track of the last word for continuous display

# dictionary to map morse code to letters
morse_code_dict = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z", "-----": "0", ".----": "1", "..---": "2", "...--": "3",
    "....-": "4", ".....": "5", "-....": "6", "--...": "7", "---..": "8", "----.": "9"
}

# function to convert morse code to an english letter
def morse_to_english(morse_code):
    return morse_code_dict.get(morse_code, "")  # returns the letter or empty string if invalid

# calibration variables
calibrating = True  # to check if calibration is in progress
calibration_frames = 10  # number of frames to use for calibration
open_eye_ratios = []  # list to collect eye open ratios during calibration
blink_ratios = []  # list to collect blink ratios during calibration
calibrated_threshold = None  # dynamic blink threshold after calibration

# check if the video was opened correctly
if not cap.isOpened():
    print("error: could not open video.")
    exit()

while True:
    # read a frame from the video
    success, frame = cap.read()

    # check if the frame was read successfully
    if not success:
        print("error: could not read frame.")
        break

    # resize the frame for faster processing
    frame = cv2.resize(frame, (1280, 720))

    # detect the face mesh and get the landmarks
    frame, landmarks = detector.findFaceMesh(frame, draw=False)

    if landmarks:
        # get the first face's landmarks
        face = landmarks[0]

        # draw circles on the key eye landmarks for visualization
        for id in idList:
            cv2.circle(frame, face[id], 2, (0, 255, 0), cv2.FILLED)

        # get the positions of the key landmarks for the eyes
        up = face[159]
        down = face[23]
        left = face[130]
        right = face[243]

        # calculate the height and width of the eye
        height, _ = detector.findDistance(up, down)
        width, _ = detector.findDistance(left, right)

        # draw lines on the eye to show the dimensions being measured
        cv2.line(frame, up, down, (255, 0, 0), 2)
        cv2.line(frame, left, right, (255, 0, 0), 2)

        # calculate the eye opening ratio (width to height ratio)
        ratio = (width / height) * 100
        ratioList.append(ratio)

        # limit the ratio list to the last 4 values to smooth out noise
        if len(ratioList) > 4:
            ratioList.pop(0)

        # calculate the average eye opening ratio
        ratioAvg = sum(ratioList) / len(ratioList)

        # during calibration, collect data for both open-eye and blink ratios
        if calibrating:
            if len(open_eye_ratios) < calibration_frames:
                # collect open-eye ratios
                open_eye_ratios.append(ratioAvg)
                cv2.putText(frame, "calibrating open eye ratio...", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            elif len(blink_ratios) < calibration_frames:
                # collect blink ratios (larger than normal open-eye ratio)
                if ratioAvg > max(open_eye_ratios) * 1.15:
                    blink_ratios.append(ratioAvg)
                cv2.putText(frame, "calibrating blink ratio...", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            else:
                # once calibration is complete, calculate the blink threshold
                open_eye_avg = sum(open_eye_ratios) / len(open_eye_ratios)
                blink_avg = sum(blink_ratios) / len(blink_ratios)
                calibrated_threshold = (open_eye_avg + blink_avg) / 2
                calibrating = False
                print(f"calibration done. open eye: {open_eye_avg}, blink: {blink_avg}, threshold: {calibrated_threshold}")
                cv2.putText(frame, f"calibration done!", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # once calibration is complete, start detecting blinks
        if not calibrating and calibrated_threshold is not None:
            # if the eye ratio exceeds the threshold, start timing the blink
            if ratioAvg > calibrated_threshold:
                if blinkStart == 0:  # if blink just started
                    blinkStart = time.time()
                counter = 1
            else:
                # when the blink ends, calculate blink duration
                if blinkStart != 0:
                    blinkDuration = time.time() - blinkStart
                    blinkStart = 0

                    current_time = time.time()
                    # if enough time has passed since the last blink, consider it a new letter
                    if current_time - lastBlinkTime >= 1.26 and lastBlinkTime != 0:
                        blinks.append("|")  # append a separator for the end of a letter

                        # convert morse sequence to a letter and add to the word
                        if morse_sequence:  # check if there's a valid sequence
                            letter = morse_to_english(morse_sequence)
                            morse_word += letter  # add letter to the current word
                            morse_sequence = ""  # reset for the next letter
                        else:
                            morse_word += " "  # add space for a word separator
                    lastBlinkTime = current_time

                    # classify blink as long or short based on its duration
                    if 0.6 <= blinkDuration:
                        morse_sequence += "-"  # long blink
                    elif blinkDuration < 0.6:
                        morse_sequence += "."  # short blink

                counter = 0

        # if the word is updated, store it in `last_displayed_word`
        if morse_word:
            last_displayed_word = morse_word

        # display the current morse sequence and the formed word (or last word)
        cv2.putText(frame, f"morse: {morse_sequence}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"word: {last_displayed_word}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # resize the frame for display and show it
        display_frame = cv2.resize(frame, (960, 540))
        cv2.imshow('morse code blink detection', display_frame)

    # break the loop if 'q' is pressed
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# if there is an unfinished morse sequence, convert it to a letter and append to the word
if morse_sequence:
    letter = morse_to_english(morse_sequence)
    morse_word += letter
print(morse_word)

# release the video capture and close any open windows
cap.release()
cv2.destroyAllWindows()