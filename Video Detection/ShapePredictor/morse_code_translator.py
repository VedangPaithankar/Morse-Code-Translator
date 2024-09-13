from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import dlib
import cv2
import keyboard
import morse_code  # This module should handle Morse code translation
import constants  # This module should define constants like EYE_AR_THRESH
import time

SHORT_BLINK_DURATION = 1.0  # in seconds
LONG_BLINK_DURATION = 2.0   # in seconds
BREAK_DURATION = 0.5        # Duration to recognize the end of a Morse character

'''
Eye Aspect Ratio

The function measures how the shape of the eye changes over time. Specifically, it helps determine whether the eye is open or closed based on its aspect ratio. This is useful for applications like detecting blinks or monitoring eye movement.

Formula
The formula for EAR is:

EAR = (A+B)/2xC
​
 

Where:

A is the distance between the top and bottom vertical eye landmarks.
B is the distance between the top and bottom vertical eye landmarks on the other side.
C is the distance between the horizontal eye landmarks (the width of the eye).
Interpretation
EAR > Threshold: The eye is considered open.
EAR < Threshold: The eye is considered closed.
The threshold value is empirically determined and varies based on individual characteristics. It’s used to decide whether the eye is in an open or closed state.

Write this in markdown
'''

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

'''
Load Face Detector and Landmark Predictor:

It loads a pre-trained model to detect faces in video frames.
It also loads another model to find specific facial landmarks (points) around the eyes.
Identify Eye Landmarks:

It gets the indices (positions) of the facial landmarks specifically for the left and right eyes.
Start Video Stream:

It opens the webcam (or other video source) to start capturing live video frames.
Return Setup Details:

It returns everything needed for processing the video: the video stream object, face detector, landmark predictor, and the eye landmark indices.
In summary, this function sets up the tools and models required to detect faces and track eye movements in real-time video.
'''

def setup_detector_video(args):
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    print("[INFO] starting video stream thread...")
    vs = VideoStream(src=0).start()
    return vs, detector, predictor, lStart, lEnd, rStart, rEnd

'''
Initialize Counters and Flags: It sets up some counters and flags to keep track of eye movements and Morse code timing.

Capture Video Frames: It continuously captures frames from the camera.

Detect Faces and Eyes: For each frame, it detects faces and then identifies the position of the eyes.

Calculate Eye Aspect Ratio: It calculates how closed the eyes are by measuring the distance between key points around the eyes.

Draw Eye Contours: It highlights the eyes in the video feed for better visualization.

Check Eye Status:

If the eyes are closed for a certain amount of time, it interprets this as a Morse code dot or dash.
If the eyes are open for a while, it handles the separation between dots and dashes, or words.
Update Morse Code: It updates and displays the current Morse code based on the eye movements.

Display Information: It shows the current eye aspect ratio and Morse code on the screen.

Handle User Input: It checks if a specific key is pressed to exit the program.

Return Results: Finally, it returns the complete Morse code that was detected.
'''

def loop_camera(vs, detector, predictor, lStart, lEnd, rStart, rEnd):
    # Initialize counters and flags
    COUNTER = 0
    BREAK_COUNTER = 0
    EYES_OPEN_COUNTER = 0
    CLOSED_EYES = False
    WORD_PAUSE = False
    PAUSED = False
    LAST_BLINK_TIME = time.time()
    LAST_BLINK_TYPE = None

    total_morse = ""
    morse_word = ""
    morse_char = ""

    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            left_eye_ar = eye_aspect_ratio(leftEye)
            right_eye_ar = eye_aspect_ratio(rightEye)
            eye_ar = (left_eye_ar + right_eye_ar) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            current_time = time.time()
            blink_duration = current_time - LAST_BLINK_TIME

            if eye_ar < constants.EYE_AR_THRESH:
                COUNTER += 1
                BREAK_COUNTER += 1
                if COUNTER == 1:  # Start of a blink
                    LAST_BLINK_TIME = current_time
                if COUNTER >= constants.EYE_AR_CONSEC_FRAMES:
                    CLOSED_EYES = True
                if BREAK_COUNTER >= constants.BREAK_LOOP_FRAMES:
                    break
            else:
                if BREAK_COUNTER < constants.BREAK_LOOP_FRAMES:
                    BREAK_COUNTER = 0
                EYES_OPEN_COUNTER += 1

                # Determine blink type based on duration
                if COUNTER >= constants.EYE_AR_CONSEC_FRAMES:
                    if blink_duration >= LONG_BLINK_DURATION:
                        if LAST_BLINK_TYPE != '-':
                            morse_word += "-"
                            total_morse += "-"
                            morse_char += "-"
                            LAST_BLINK_TYPE = '-'
                    else:
                        if LAST_BLINK_TYPE != '.':
                            morse_word += "."
                            total_morse += "."
                            morse_char += "."
                            LAST_BLINK_TYPE = '.'
                    COUNTER = 0
                    CLOSED_EYES = False
                    PAUSED = True
                    EYES_OPEN_COUNTER = 0

                elif CLOSED_EYES:
                    morse_word += "."
                    total_morse += "."
                    morse_char += "."
                    COUNTER = 1
                    CLOSED_EYES = False
                    PAUSED = True
                    EYES_OPEN_COUNTER = 0

                elif PAUSED and EYES_OPEN_COUNTER >= constants.PAUSE_CONSEC_FRAMES:
                    morse_word += "/"
                    total_morse += "/"
                    morse_char = "/"
                    PAUSED = False
                    WORD_PAUSE = True
                    CLOSED_EYES = False
                    EYES_OPEN_COUNTER = 0
                    keyboard.write(morse_code.from_morse(morse_word))
                    morse_word = ""

                elif WORD_PAUSE and EYES_OPEN_COUNTER >= constants.WORD_PAUSE_CONSEC_FRAMES:
                    total_morse += "¦/"
                    morse_char = ""
                    WORD_PAUSE = False
                    CLOSED_EYES = False
                    EYES_OPEN_COUNTER = 0
                    keyboard.write(morse_code.from_morse("¦/"))

            cv2.putText(frame, "EAR: {:.2f}".format(eye_ar), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "{}".format(morse_char), (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)

            print("\033[K", "morse_word: {}".format(morse_word), end="\r")

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("]") or BREAK_COUNTER >= constants.BREAK_LOOP_FRAMES:
            keyboard.write(morse_code.from_morse(morse_word))
            break

    return total_morse

def cleanup(vs):
    cv2.destroyAllWindows()
    vs.stop()

def print_results(total_morse):
    print("Morse Code: ", total_morse.replace("¦", " "))
    print("Translated: ", morse_code.from_morse(total_morse))

def main():
    arg_par = argparse.ArgumentParser()
    arg_par.add_argument("-p", "--shape-predictor", required=True, help="path to facial landmark predictor")
    args = vars(arg_par.parse_args())

    (vs, detector, predictor, lStart, lEnd, rStart, rEnd) = setup_detector_video(args)
    total_morse = loop_camera(vs, detector, predictor, lStart, lEnd, rStart, rEnd)
    cleanup(vs)
    print_results(total_morse)

if __name__ == "__main__":
    main()