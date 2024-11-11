import numpy as np
import wave

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', 
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', 
    '0': '-----', ' ': '/'
}

# Audio settings
DOT_DURATION = 0.2  # seconds
DASH_DURATION = DOT_DURATION * 3
FREQUENCY = 800  # in Hz, frequency of the tone
SAMPLE_RATE = 44100  # samples per second

def ttm(text):
    morse_code = ' '.join(MORSE_CODE_DICT.get(char.upper(), '') for char in text)
    return morse_code

def text_to_morse(text):
    # Convert each character to Morse code, then filter out the characters
    morse_code = ' '.join(MORSE_CODE_DICT.get(char.upper(), '') for char in text)
    
    # Extract alternating Morse code characters starting from the first
    result = ' '.join(morse_code.split(' ')[i] for i in range(len(morse_code.split(' '))) if i % 2 == 1)
    return result

def generate_tone(duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * FREQUENCY * t)
    return tone

def generate_silence(duration):
    return np.zeros(int(SAMPLE_RATE * duration))

def morse_to_audio(morse_code, filename="./audio_files/tampered_audio.wav"):
    audio_data = []

    for symbol in morse_code:
        if symbol == '.':
            audio_data.extend(generate_tone(DOT_DURATION))
        elif symbol == '-':
            audio_data.extend(generate_tone(DASH_DURATION))
        elif symbol == ' ':
            audio_data.extend(generate_silence(1.5))  # Between letters
        elif symbol == '/':
            audio_data.extend(generate_silence(1.5))  # Between words

        audio_data.extend(generate_silence(DOT_DURATION))

    audio_data = np.array(audio_data)

    with wave.open(filename, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes((audio_data * 32767).astype(np.int16).tobytes())

    print(f"Audio file saved as {filename}")

def morsecode_to_audio(text):
    morse_to_audio(text_to_morse(text))

if __name__ == "__main__":
    text = "13"
    morsecode_to_audio(text)
    # morse_code = text_to_morse(text)
    # print("Morse Code:", morse_code)
    # morse_to_audio(morse_code)