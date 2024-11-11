import os
from generators.generate_public_keys import compute_public_key, map_digits_to_letters, caesar_cipher
from generators.morse_code_audio_generator import morsecode_to_audio, ttm
from generators.checksum_generator import get_checksum

# Define paths and constants
FILES_PATH = './files/'
OUTPUT_PATH = './audio_files/'
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Step 1: Read inputs from file with specific format
input_file = os.path.join(FILES_PATH, 'file.txt')
with open(input_file, 'r') as f:
    lines = f.readlines()
    a = int(lines[0].strip().split('=')[1])        # Primitive root (a)
    q = int(lines[1].strip().split('=')[1])        # Prime number (q)
    private_key = int(lines[2].strip().split('=')[1])  # Private key

# Compute public key
public_key = compute_public_key(a, q, private_key)

# Map public key to letters
encoded_public_key = map_digits_to_letters(public_key)

# Caesar Cipher encryption
shift = a % 26
encrypted_public_key = caesar_cipher(encoded_public_key, shift)

# Convert to Morse code
morse_string = ttm(encrypted_public_key)

def split_morse_code(morse_code: str) -> (str, str):
    """Split Morse code into separate strings for video (odd positions) and audio (even positions)."""
    morse_chars = morse_code.split()
    video_morse = ' '.join(morse_chars[i] for i in range(0, len(morse_chars), 2))  # Odd positions (for video)
    audio_morse = ' '.join(morse_chars[i] for i in range(1, len(morse_chars), 2))  # Even positions (for audio)
    return video_morse, audio_morse

video_morse, audio_morse = split_morse_code(morse_string)

if audio_morse:
    # Generate Morse code audio
    morse_audio = morsecode_to_audio(encrypted_public_key)

# Get the checksum
checksum = get_checksum(morse_string)
video_morse += " " + ttm(str(checksum))

# Write output to transmission file
output_file = os.path.join(FILES_PATH, 'transmission')
with open(output_file, 'w') as f:
    f.write(f"Public Key: {public_key}\n")
    f.write(f"Encoded Public Key (letters): {encoded_public_key}\n")
    f.write(f"Encrypted Public Key (Caesar Cipher): {encrypted_public_key}\n")
    f.write(f"Checksum: {checksum}\n")
    f.write(f"Video Morse Code (Odd positions + CheckSum): {video_morse}\n")
    f.write(f"Audio Morse Code (Even positions): {audio_morse}\n")
    f.write(f"Morse Code to be transmitted: {morse_string + ' ' + ttm(str(checksum))}\n")
    f.write(f"Morse code audio saved to: morse_code.wav\n")

print(f"Output saved to {output_file}")
