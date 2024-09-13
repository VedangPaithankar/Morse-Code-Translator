# Morse Code Translator with Eye Blinks

## Overview

This project is a real-time Morse code translator that uses video input to detect eye blinks and translates them into Morse code. It leverages facial landmark detection to measure the eye aspect ratio (EAR) and identify blinks as Morse code dots and dashes. The translated Morse code is then converted into text.

## Features

* Real-time Morse code translation using eye blinks
* Detects and differentiates between short and long blinks
* Displays the detected Morse code and its English translation in real-time

## Requirements

To run this project, you'll need to install the following Python libraries:

* `opencv-python`
* `imutils`
* `dlib`
* `scipy`
* `numpy`
* `keyboard`

Install these libraries using pip:

```bash
pip install opencv-python imutils dlib scipy numpy keyboard
```
if dlib gives error of cmake then download binaries from [here](https://github.com/z-mahmud22/Dlib_Windows_Python3.x) and then do:
```bash
pip install path/to/dlib_binaries
``` 
## Download Pre-trained Models

Download the pre-trained facial landmark model:

* [shape_predictor_68_face_landmarks.dat](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)

Extract the file and keep it in your working directory.

## Usage

**1. Clone the Repository:**

```bash
git clone https://github.com/yourusername/morse-code-translator.git
cd morse-code-translator
```

**2. Run the Script:**

Execute the script with the path to the facial landmark predictor:

```bash
python morse_code_translator.py -p path/to/shape_predictor.dat
```

Replace `path/to/shape_predictor.dat` with the path to the downloaded `shape_predictor_68_face_landmarks.dat` file.

## Code Explanation

* **`eye_aspect_ratio(eye)`:** Calculates the eye aspect ratio to determine if the eyes are closed or open.
* **`setup_detector_video(args)`:** Initializes the video stream and facial landmark detector.
* **`loop_camera(vs, detector, predictor, lStart, lEnd, rStart, rEnd)`:** Captures video frames, processes them to detect eye blinks, and translates them into Morse code. Handles both short and long blinks to correctly interpret Morse code.

## Constants

* `EYE_AR_THRESH`: Threshold for the eye aspect ratio to determine if the eyes are closed.
* `EYE_AR_CONSEC_FRAMES`: Number of consecutive frames with closed eyes required to consider it a blink.
* `BREAK_LOOP_FRAMES`: Number of frames to wait before breaking out of the loop if no eye blinks are detected.
* `SHORT_BLINK_DURATION`: Duration considered for a short blink.
* `LONG_BLINK_DURATION`: Duration considered for a long blink.

## Troubleshooting

* **Blink Detection Issues**: Adjust the `EYE_AR_THRESH` and duration constants based on your testing results to improve blink detection.
* **Model Path**: Ensure that the path to `shape_predictor_68_face_landmarks.dat` is correctly specified.
