# main.py
import os
import numpy as np
import pygame
from decode_video import process_morse_video
from generate_public_keys import compute_public_key, map_digits_to_letters, caesar_cipher, string_to_morse, caesar_decipher
from morse_code_audio_generator import generate_alternating_morse_audio, save_audio_to_wav
from checksum_generator import get_checksum


# Define paths and constants
OUTPUT_PATH = './morse_code_output/'
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Step 1: Get inputs and compute public key
a = int(input('Provide primitive root (a): '))
q = int(input('Provide prime number (q): '))
private_key = int(input('Provide private key: '))

public_key = compute_public_key(a, q, private_key)
print(f"Public Key: {public_key}")

# Step 2: Map public key to letters
encoded_public_key = map_digits_to_letters(public_key)
print(f"Encoded Public Key (letters): {encoded_public_key}")

# Step 3: Caesar Cipher encryption
shift = a % 26
encrypted_public_key = caesar_cipher(encoded_public_key, shift)
print(f"Encrypted Public Key (Caesar Cipher): {encrypted_public_key}")

# Step 4: Convert to Morse code
morse_string = string_to_morse(encrypted_public_key)
print(f"Morse Code to be transmitted: {morse_string}")

def split_morse_code(morse_code: str) -> (str, str):
    """Split Morse code into separate strings for video (odd positions) and audio (even positions)."""
    morse_chars = morse_code.split()
    video_morse = ' '.join(morse_chars[i] for i in range(0, len(morse_chars), 2))  # Odd positions (for video)
    audio_morse = ' '.join(morse_chars[i] for i in range(1, len(morse_chars), 2))  # Even positions (for audio)
    return video_morse, audio_morse

video_morse, audio_morse = split_morse_code(morse_string)

# Step 5: Generate Morse code audio
morse_audio = generate_alternating_morse_audio(morse_string)

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

# Step 6: Get the checksum
checksum = get_checksum(morse_string)
print(f"Checksum: {checksum}")

video_morse += " " + string_to_morse(str(checksum))
print(f"Video Morse Code (Odd positions + CheckSum): {video_morse}")
print(f"Audio Morse Code (Even positions): {audio_morse}")

# Step 7: Decode them using morse code translator
video_decoded_word = process_morse_video('./morse_code_train_data/hello_morse_code.mp4')
print(video_decoded_word)

# Step 8: Decode them using morse code translator
video_decoded_word = process_morse_video('./morse_code_train_data/hello_morse_code.mp4')
print(video_decoded_word)

# Step 9: Verify the checksum
if checksum == video_decoded_word[-1]:
    print("Checksum verified!")
else:
    print("Checksum failed to verify! Audio tampered. Retransmission required!")

# Step 10: Adding Both Audio and Video Together

# Step 11: decrypt them using ceasar cypher
public_Key = caesar_decipher(text=video_decoded_word[:-1], shift=a)
print(public_Key)
print("Keys exchanged successfully!")