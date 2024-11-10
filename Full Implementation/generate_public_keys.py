# Import necessary modules
def compute_public_key(a: int, q: int, private_key: int) -> int:
    """Compute the public key using modular exponentiation."""
    return pow(a, private_key, q)

def map_digits_to_letters(public_key: int) -> str:
    """Map digits of the public key to letters based on a specific rule."""
    public_key_str = str(public_key)
    mapped_letters = []
    
    for digit in public_key_str:
        if digit == '0':
            mapped_letters.append('J')  # 0 -> J
        else:
            mapped_letters.append(chr(int(digit) + ord('A') - 1))  # 1->A, 2->B, ..., 9->I

    return ''.join(mapped_letters)

def caesar_cipher(text: str, shift: int) -> str:
    """Encrypt text using Caesar Cipher with a given shift."""
    encrypted_text = []
    
    for letter in text:
        new_pos = (ord(letter) - ord('A') + shift) % 26
        encrypted_text.append(chr(new_pos + ord('A')))
    
    return ''.join(encrypted_text)

def caesar_decipher(text: str, shift: int) -> str:
    """Decrypt text encrypted with Caesar Cipher using the given shift."""
    decrypted_text = []
    
    for letter in text:
        new_pos = (ord(letter) - ord('A') - shift) % 26
        decrypted_text.append(chr(new_pos + ord('A')))
    
    return ''.join(decrypted_text)

def string_to_morse(input_string: str) -> str:
    """Convert a string to Morse code."""
    morse_code_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 
        'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
        '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', 
        '8': '---..', '9': '----.', ' ': ' / ', '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--', 
        '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.',
        '-': '-....-', '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.'
    }
    input_string = input_string.upper()
    morse_code = [morse_code_dict[char] for char in input_string if char in morse_code_dict]
    return ' '.join(morse_code)

def split_morse_code(morse_code: str) -> (str, str):
    """Split Morse code into separate strings for odd and even positions."""
    morse_chars = morse_code.split()
    video_morse = ' '.join(morse_chars[i] for i in range(0, len(morse_chars), 2))  # Odd positions: 1st, 3rd, 5th, ...
    audio_morse = ' '.join(morse_chars[i] for i in range(1, len(morse_chars), 2))  # Even positions: 2nd, 4th, 6th, ...
    return video_morse, audio_morse

if __name__ == "__main__":
    # Input for primitive root, prime number, and private key
    a = int(input('Provide primitive root (a): '))
    q = int(input('Provide prime number (q): '))
    private_key = int(input('Provide private key: '))
    
    # Step 1: Compute the public key
    public_key = compute_public_key(a, q, private_key)
    print(f"Public Key: {public_key}")
    
    # Step 2: Convert the public key to an alphabetic representation
    encoded_public_key = map_digits_to_letters(public_key)
    print(f"Encoded Public Key (letters): {encoded_public_key}")
    
    # Step 3: Perform Caesar Cipher encryption
    shift = a % 26  # Shift based on the primitive root
    encrypted_public_key = caesar_cipher(encoded_public_key, shift)
    print(f"Encrypted Public Key (Caesar Cipher): {encrypted_public_key}")
    
    # Step 4: Convert the encrypted public key to Morse code
    morse_string = string_to_morse(encrypted_public_key)
    print(f"Encrypted Public Key in Morse Code: {morse_string}")
    
    # Step 5: Separate Morse code for video (odd) and audio (even)
    video_morse, audio_morse = split_morse_code(morse_string)
    print(f"Encrypted Public Key in Morse Code - video (odd places): {video_morse}")
    print(f"Encrypted Public Key in Morse Code - audio (even places): {audio_morse}")