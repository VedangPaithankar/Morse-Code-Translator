import os
import pygame
import numpy as np
import wave

# Initialize pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Define Morse Code dictionary
CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..',
    'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.'
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

# Function to generate a sine wave sound for a dot (short beep)
def generate_dot():
    frequency = 1000  # 1000 Hz for the dot sound
    duration = ONE_UNIT / 1000  # Convert to seconds
    return pygame.sndarray.make_sound(generate_sine_wave(frequency, duration))

# Function to generate a sine wave sound for a dash (long beep)
def generate_dash():
    frequency = 1000  # 1000 Hz for the dash sound
    duration = THREE_UNITS / 1000  # Convert to seconds
    return pygame.sndarray.make_sound(generate_sine_wave(frequency, duration))

# Function to generate silence
def generate_silence(duration):
    return pygame.sndarray.make_sound(generate_sine_wave(0, duration / 1000))

# Helper to generate a sine wave (using numpy)
def generate_sine_wave(frequency, duration):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t) * 32767  # Max amplitude for 16-bit audio

    # Convert to stereo by duplicating the mono signal into two channels
    stereo_wave = np.column_stack((wave, wave))  # Two identical channels for stereo sound
    return np.array(stereo_wave, dtype=np.int16)  # Return as 2D array for stereo

# Function to generate Morse code audio for a specific character
def generate_morse_audio(char):
    morse_code = CODE[char.upper()]
    morse_audio = []

    for symbol in morse_code:
        if symbol == '.':
            morse_audio.append(generate_dot())
        elif symbol == '-':
            morse_audio.append(generate_dash())
        morse_audio.append(generate_silence(SILENCE_UNIT))

    return morse_audio

# Function to generate the full audio for a string of alternating characters
def generate_alternating_morse_audio(input_string):
    final_audio = []

    for i, char in enumerate(input_string):
        if i % 2 == 1:  # Only process every second character
            if char.upper() in CODE:
                final_audio.extend(generate_morse_audio(char))
        else:
            final_audio.append(generate_silence(2000))  # Add 2 seconds silence for skipped characters

    return final_audio

# Function to save the generated audio to a WAV file
def save_audio_to_wav(audio_data, filename):
    sample_rate = 44100
    with wave.open(filename, 'wb') as wav_file:
        # Set parameters for the WAV file
        wav_file.setnchannels(2)  # Stereo audio
        wav_file.setsampwidth(2)  # 16-bit audio
        wav_file.setframerate(sample_rate)

        # Convert numpy array to byte data and write to file
        audio_bytes = audio_data.tobytes()
        wav_file.writeframes(audio_bytes)

# Main function
if __name__ == "__main__":
    input_string = "AUX"
    morse_audio = generate_alternating_morse_audio(input_string)

    # Combine all the individual sound arrays into one
    combined_audio = np.empty((0, 2), dtype=np.int16)  # Initialize as 2D array for stereo
    for sound in morse_audio:
        # Convert pygame sound to numpy array
        sound_array = pygame.sndarray.array(sound)
        combined_audio = np.concatenate((combined_audio, sound_array), axis=0)

    # Save the combined audio to a WAV file
    output_filename = os.path.join(OUTPUT_PATH, "morse_code_output.wav")
    save_audio_to_wav(combined_audio, output_filename)

    print(f"Morse code audio saved to: {output_filename}")