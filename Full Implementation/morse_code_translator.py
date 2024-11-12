from translator.decode_video import process_morse_video
from translator.decode_audio import predict_audio
from generators.generate_public_keys import caesar_decipher
from generators.morse_code_audio_generator import ttm

# Step 7: Decode them using morse code translator - Video
video_decoded_word = process_morse_video('./video_files/test1-Bob.mp4')

# Step 8: Decode them using morse code translator - Audio
audio_decoded_word = predict_audio('./audio_files/test1-Bob.wav')
audio_decoded_word = audio_decoded_word['label']

# Step 9: Verify the checksum
checksum_video = int(video_decoded_word[-1])
print(checksum_video)
checksum_audio = ttm(audio_decoded_word)
print(checksum_audio)
checksum = abs(sum(1 if i == '.' else -1 for i in checksum_audio))

checksum_verification = "Checksum Verified!!" if checksum_video == checksum else "Checksum Failed!!"

# Step 10: Adding Both Audio and Video Together
if video_decoded_word and len(video_decoded_word) > 3:
    video_decoded_word = video_decoded_word[1:-1]
else:
    video_decoded_word = video_decoded_word[:-1]
public_key_encrypted = ""
min_len = min(len(video_decoded_word), len(audio_decoded_word))
for i in range(min_len):
    public_key_encrypted += video_decoded_word[i] + audio_decoded_word[i]

public_key_encrypted += video_decoded_word[min_len:] + audio_decoded_word[min_len:]

# Step 11: Decrypt using Caesar cipher
public_Key = caesar_decipher(text=public_key_encrypted, shift=3)

# Save the results to file
with open('./files/test1_results.txt', 'w') as file:
    file.write("Decoded Word (Video): " + video_decoded_word + "\n")
    file.write("Decoded Word (Audio): " + audio_decoded_word + "\n")
    file.write(checksum_verification + "\n")
    if checksum_verification == "Checksum Verified!!":
        file.write("Public Key of Alice: " + public_Key + "\n")
        file.write("Keys exchanged successfully!\n")

print("Test results are in the file test1_results.txt")