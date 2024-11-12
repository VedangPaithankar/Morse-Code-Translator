import os
import numpy as np
import librosa
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

def audio_to_spectrogram(file_path, n_mels=64, n_fft=2048, hop_length=512):
    """Convert audio file to mel spectrogram"""
    y, sr = librosa.load(file_path, sr=None)
    spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length)
    log_spectrogram = librosa.power_to_db(spectrogram)
    return log_spectrogram

def initialize_label_encoder():
    """Initialize label encoder with all possible classes"""
    labels = [chr(i) for i in range(ord('A'), ord('Z')+1)]  # A-Z
    labels.extend([str(i) for i in range(1, 10)])  # 1-9
    label_encoder = LabelEncoder()
    label_encoder.fit(labels)
    return label_encoder

def preprocess_audio_file(file_path, target_size=(64, 64)):
    """Preprocess a single audio file"""
    try:
        # Generate spectrogram
        spectrogram = audio_to_spectrogram(file_path)
        
        # Resize to target size
        spectrogram_resized = cv2.resize(spectrogram, target_size)
        
        # Normalize
        spectrogram_normalized = (spectrogram_resized - spectrogram_resized.min()) / \
                               (spectrogram_resized.max() - spectrogram_resized.min())
        
        return spectrogram_normalized[..., np.newaxis]  # Add channel dimension
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def predict_audio(audio_file_path, model_path="./audio_model/rnn_model.h5"):
    """Predict the label for a single audio file"""
    try:
        # Load the model
        print("Loading the model...")
        model = load_model(model_path)
        label_encoder = initialize_label_encoder()
        
        # Process the audio file
        print("Processing the audio file...")
        processed_audio = preprocess_audio_file(audio_file_path)
        
        if processed_audio is not None:
            # Make prediction
            print("Making prediction...")
            prediction = model.predict(np.array([processed_audio]), verbose=0)
            predicted_label = label_encoder.inverse_transform([np.argmax(prediction)])[0]
            confidence = np.max(prediction) * 100
            
            print("\nPrediction Results:")
            print("-" * 50)
            print(f"Audio File: {os.path.basename(audio_file_path)}")
            print(f"Predicted Label: {predicted_label}")
            print(f"Confidence: {confidence:.2f}%")
            print("-" * 50)
            
            # Return prediction results
            return {
                'label': predicted_label,
                'confidence': confidence
            }
        else:
            print("Failed to process the audio file.")
            return None
            
    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Set paths
    model_path = "./audio_model/rnn_model.h5"
    
    # You can either hardcode the audio file path or use input()
    audio_file_path = './audio_files/tampered_audio.wav'
    
    # Make prediction
    result = predict_audio(model_path, audio_file_path)
    
    # Optional: you can add more processing based on the prediction result
    if result:
        # Example: you might want to do something based on the predicted label
        print(f"\nPredicted class: {result['label']}")
        
        # Example: you might want to take different actions based on confidence level
        if result['confidence'] > 90:
            print("High confidence prediction!")
        elif result['confidence'] > 70:
            print("Moderate confidence prediction.")
        else:
            print("Low confidence prediction. Please verify.")