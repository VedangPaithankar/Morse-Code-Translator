import numpy as np
from scipy.io import wavfile
from morse_audio_decoder.morse import MorseCode

# Function to convert stereo WAV to mono
def convert_stereo_to_mono(input_file, output_file):
    sample_rate, data = wavfile.read(input_file)
    
    # Check if the file is stereo (2 channels)
    if len(data.shape) == 2:
        print("Converting stereo to mono...")
        # Convert stereo to mono by averaging the two channels
        mono_data = np.mean(data, axis=1, dtype=data.dtype)
        wavfile.write(output_file, sample_rate, mono_data)
        print(f"Converted file saved as {output_file}")
    else:
        print("File is already mono.")

# Function to decode Morse code from WAV
def decode_morse_from_wav(wavfile):
    morse_code = MorseCode.from_wavfile(wavfile)
    decoded_text = morse_code.decode()
    print("Decoded Morse Code:", decoded_text)

# Convert the stereo audio file to mono
convert_stereo_to_mono("morse_audio.wav", "morse_audio_mono.wav")

# Decode Morse code from the mono file
decode_morse_from_wav("morse_audio_mono.wav")