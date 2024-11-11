import cv2
import time
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot

def process_morse_video(video_path):
    # open a connection to the video file
    cap = cv2.VideoCapture(video_path)

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
        print("Error: Could not open video.")
        return

    while True:
        # read a frame from the video
        success, frame = cap.read()

        # check if the frame was read successfully
        if not success:
            print("End of video or error: Could not read frame.")
            break

        # resize the frame for faster processing
        frame = cv2.resize(frame, (1280, 720))

        # detect the face mesh and get the landmarks
        frame, landmarks = detector.findFaceMesh(frame, draw=False)

        if landmarks:
            face = landmarks[0]
            for id in idList:
                cv2.circle(frame, face[id], 2, (0, 255, 0), cv2.FILLED)

            up, down = face[159], face[23]
            left, right = face[130], face[243]
            height, _ = detector.findDistance(up, down)
            width, _ = detector.findDistance(left, right)
            cv2.line(frame, up, down, (255, 0, 0), 2)
            cv2.line(frame, left, right, (255, 0, 0), 2)
            ratio = (width / height) * 100
            ratioList.append(ratio)
            if len(ratioList) > 4:
                ratioList.pop(0)
            ratioAvg = sum(ratioList) / len(ratioList)

            if calibrating:
                if len(open_eye_ratios) < calibration_frames:
                    open_eye_ratios.append(ratioAvg)
                    cv2.putText(frame, "Calibrating open eye ratio...", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                elif len(blink_ratios) < calibration_frames:
                    if ratioAvg > max(open_eye_ratios) * 1.10:
                        blink_ratios.append(ratioAvg)
                    cv2.putText(frame, "Calibrating blink ratio...", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    open_eye_avg = sum(open_eye_ratios) / len(open_eye_ratios)
                    blink_avg = sum(blink_ratios) / len(blink_ratios)
                    calibrated_threshold = (open_eye_avg + blink_avg) / 2
                    calibrating = False
                    print(f"Calibration done. Open eye: {open_eye_avg}, Blink: {blink_avg}, Threshold: {calibrated_threshold}")
                    cv2.putText(frame, f"Calibration done!", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if not calibrating and calibrated_threshold is not None:
                if ratioAvg > calibrated_threshold:
                    if blinkStart == 0:
                        blinkStart = time.time()
                else:
                    if blinkStart != 0:
                        blinkDuration = time.time() - blinkStart
                        blinkStart = 0
                        current_time = time.time()
                        if current_time - lastBlinkTime >= 2.2 and lastBlinkTime != 0:
                            blinks.append("|")
                            if morse_sequence:
                                letter = morse_to_english(morse_sequence)
                                morse_word += letter
                                morse_sequence = ""
                            else:
                                morse_word += " "
                        lastBlinkTime = current_time
                        if 0.9 <= blinkDuration:
                            morse_sequence += "-"
                        elif blinkDuration < 0.9:
                            morse_sequence += "."

            if morse_word:
                last_displayed_word = morse_word

            cv2.putText(frame, f"Morse: {morse_sequence}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, f"Word: {last_displayed_word}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            display_frame = cv2.resize(frame, (960, 540))
            cv2.imshow('Morse Code Blink Detection', display_frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    if morse_sequence:
        letter = morse_to_english(morse_sequence)
        morse_word += letter
    #print("Final Word:", morse_word)

    cap.release()
    cv2.destroyAllWindows()
    return morse_word

if __name__ == "__main__":
    # Example usage:
    print(process_morse_video("./video_files/test1.mp4"))