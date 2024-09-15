import sounddevice as sd
from scipy.io.wavfile import write, read
import numpy as np
import noisereduce as nr
from pydub import AudioSegment
from pydub.effects import normalize
from morse_audio_decoder.morse import MorseCode
import os

# Function to record audio in mono
def record_audio(filename, duration, fs=44100):
    print(f"Recording for {duration} seconds in mono...")
    # Record audio with 1 channel (mono)
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    write(filename, fs, audio_data)  # Save as WAV file
    print(f"Audio recorded and saved as {filename}")

# Function to reduce noise in recorded audio
def reduce_noise(input_file, output_file):
    # Read the recorded audio file
    fs, data = read(input_file)
    print("Reducing noise...")
    # Apply noise reduction
    reduced_noise_data = nr.reduce_noise(y=data, sr=fs)
    # Save the cleaned (noise-reduced) audio file
    write(output_file, fs, reduced_noise_data)
    print(f"Noise-reduced audio saved as {output_file}")

# Function to amplify and normalize the cleaned audio
def amplify_audio(input_file, output_file):
    print("Amplifying the closer sound (foreground)...")
    # Load the noise-reduced audio
    audio = AudioSegment.from_wav(input_file)
    # Normalize the audio to amplify the foreground sound
    normalized_audio = normalize(audio)
    # Export the amplified audio
    normalized_audio.export(output_file, format="wav")
    print(f"Amplified audio saved as {output_file}")

# Function to decode Morse code from WAV file
def decode_morse_from_wav(wavfile):
    morse_code = MorseCode.from_wavfile(wavfile)
    decoded_text = morse_code.decode()
    print("Decoded Morse Code:", decoded_text)

# Paths for different audio files
raw_audio = "morse_input_mono.wav"
clean_audio = "morse_input_clean.wav"
amplified_audio = "morse_input_amplified.wav"

# Step 1: Record audio from the microphone (adjust the duration as needed)
record_audio(raw_audio, 3)  # Records 10 seconds of audio in mono

# Step 2: Apply noise reduction to the recorded audio
reduce_noise(raw_audio, clean_audio)

# Step 3: Amplify the foreground sound in the noise-reduced audio
amplify_audio(clean_audio, amplified_audio)

# Step 4: Decode the Morse code from the amplified and noise-reduced audio
decode_morse_from_wav(amplified_audio)