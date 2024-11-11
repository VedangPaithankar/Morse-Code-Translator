import librosa
import numpy as np
from tensorflow.keras.models import load_model
from morse_audio_decoder.morse import MorseCode

# Load the saved model
loaded_model = load_model("./audio_model/cnn_audio_model.h5")

# Function to convert audio to a Mel spectrogram
def audio_to_spectrogram(file_path, n_mels=64, n_fft=2048, hop_length=512):
    y, sr = librosa.load(file_path, sr=None)
    spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length)
    log_spectrogram = librosa.power_to_db(spectrogram)
    return log_spectrogram

# Function to preprocess the spectrogram and predict the label
def predict_audio_label(file_path):
    # Convert audio to spectrogram
    spectrogram = audio_to_spectrogram(file_path)
    
    # Resize the spectrogram to (96, 96) to match the model's input
    target_size = (64, 64)  # This should match the model's expected input size
    resized_spectrogram = np.zeros(target_size)
    
    # Resize or pad the spectrogram to match the target size
    resized_spectrogram[:spectrogram.shape[0], :spectrogram.shape[1]] = spectrogram[:target_size[0], :target_size[1]]
    
    # Normalize the resized spectrogram
    resized_spectrogram = resized_spectrogram / np.max(np.abs(resized_spectrogram))
    
    # Expand dimensions to match model input (batch_size, height, width, channels)
    input_data = np.expand_dims(resized_spectrogram, axis=(0, -1))
    
    # Predict the label
    prediction = loaded_model.predict(input_data)
    
    # Get the label with the highest probability
    #predicted_label = np.argmax(prediction)
    predicted_label = MorseCode.from_wavfile(file_path).decode()
    return predicted_label

# Main function
if __name__ == "__main__":
    # Example usage
    file_path = "./morse_code_train_data/3.wav"
    label = predict_audio_label(file_path)
    print("Predicted label:", label)