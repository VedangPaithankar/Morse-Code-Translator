from translator.decode_video import process_morse_video
from translator.decode_audio import predict_audio_label
from generators.generate_public_keys import caesar_decipher

# Step 7: Decode them using morse code translator - Video
video_decoded_word = process_morse_video('./morse_code_train_data/hello_morse_code.mp4')
print("Decoded Word: ", video_decoded_word)

# Step 8: Decode them using morse code translator - Audio
audio_decoded_word = predict_audio_label('./audio_files/morse_code.wav')
print("Decoded Word: ", audio_decoded_word)

# Step 9: Verify the checksum


# Step 10: Adding Both Audio and Video Together
if video_decoded_word:
    video_decoded_word = video_decoded_word[:-1]

public_key_encrypted = ""
min_len = min(len(video_decoded_word), len(audio_decoded_word))
for i in range(min_len):
    public_key_encrypted += video_decoded_word[i] + audio_decoded_word[i]

public_key_encrypted += video_decoded_word[min_len:] + audio_decoded_word[min_len:]


# Step 11: decrypt them using ceasar cypher
public_Key = caesar_decipher(text=public_key_encrypted, shift=a)
print(public_Key)
print("Keys exchanged successfully!")