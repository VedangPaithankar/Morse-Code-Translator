def get_checksum(morse_code: str) -> int:
    """
    Calculate checksum based on Morse code transmitted through audio.
    The checksum is defined as the difference between the number of dots and dashes in the audio transmission.
    
    Parameters:
    - morse_code (str): The complete Morse code string to be split and analyzed.
    
    Returns:
    - int: Checksum value calculated as (number of dots - number of dashes) in the audio Morse code.
    """
    # Split Morse code into video and audio sequences
    morse_chars = morse_code.split()
    video_morse = ' '.join(morse_chars[i] for i in range(0, len(morse_chars), 2))  # Odd positions (for video)
    audio_morse = ' '.join(morse_chars[i] for i in range(1, len(morse_chars), 2))  # Even positions (for audio)
    
    # Count dots and dashes in the audio Morse code
    num_dots = audio_morse.count('.')
    num_dashes = audio_morse.count('-')
    
    # Calculate checksum
    checksum = abs(num_dots - num_dashes)
    return checksum
