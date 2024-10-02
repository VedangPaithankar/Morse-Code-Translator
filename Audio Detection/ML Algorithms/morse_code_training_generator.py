import os
import time
import pygame
from pydub import AudioSegment
from pydub.generators import Sine

# Initialize pygame mixer
pygame.mixer.init()

# Define Morse Code dictionary
CODE = {'A': '.-',     'B': '-...',   'C': '-.-.', 
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
     	'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',
        
        '0': '-----',  '1': '.----',  '2': '..---',
        '3': '...--',  '4': '....-',  '5': '.....',
        '6': '-....',  '7': '--...',  '8': '---..',
        '9': '----.' 
        }

# Timing Constants (in milliseconds)
ONE_UNIT = 200  # Unit time for a dot in milliseconds
THREE_UNITS = 3 * ONE_UNIT  # Time for a dash
SILENCE_UNIT = ONE_UNIT  # Silence between dots and dashes within a letter
LETTER_GAP = THREE_UNITS  # Gap between letters
WORD_GAP = 7 * ONE_UNIT  # Gap between words

# File path to save the generated Morse code audio files
OUTPUT_PATH = './morse_code_train_data/'
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

# Function to generate a sine wave for a dot (short beep)
def generate_dot():
    dot = Sine(1000).to_audio_segment(duration=ONE_UNIT)  # 1000 Hz, for ONE_UNIT duration
    return dot

# Function to generate a sine wave for a dash (long beep)
def generate_dash():
    dash = Sine(1000).to_audio_segment(duration=THREE_UNITS)  # 1000 Hz, for THREE_UNITS duration
    return dash

# Function to generate silence
def generate_silence(duration):
    return AudioSegment.silent(duration=duration)

# Function to generate Morse code audio for a specific character and save it as a .wav file
def generate_morse_audio(char):
    morse_code = CODE[char.upper()]
    morse_audio = AudioSegment.silent(duration=0)  # Start with silence
    
    for symbol in morse_code:
        if symbol == '.':
            morse_audio += generate_dot()
        elif symbol == '-':
            morse_audio += generate_dash()
        morse_audio += generate_silence(SILENCE_UNIT)  # Silence between parts of the letter

    # Save the generated audio as a .wav file
    output_file = os.path.join(OUTPUT_PATH, f'{char.upper()}.wav')
    morse_audio.export(output_file, format='wav')
    print(f'Saved: {output_file}')

# Main function to generate Morse code audio for all letters and digits
def generate_all_morse_audio():
    for char in CODE.keys():
        generate_morse_audio(char)

# Run the function to generate all Morse code audio files
if __name__ == "__main__":
    generate_all_morse_audio()