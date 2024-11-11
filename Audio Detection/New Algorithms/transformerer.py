import matplotlib.pyplot as plt
import torch
import torchaudio
from torch.utils.data import Dataset, DataLoader
from torch import nn
# Import TransformerEncoder and TransformerEncoderLayer from torch.nn instead of transformers
from torch.nn import TransformerEncoder, TransformerEncoderLayer

from google.colab import drive
drive.mount('/content/drive')

import torch
import torchaudio.transforms as transforms

fixed_length = 1544  # Set based on the longest sequence you observed

def collate_fn(batch):
    mfccs, labels = zip(*batch)
    # Pad or truncate each MFCC to the fixed length
    padded_mfccs = [
        torch.nn.functional.pad(mfcc, (0, max(0, fixed_length - mfcc.size(1))))[:, :fixed_length] for mfcc in mfccs
    ]
    # Stack them into a single tensor
    mfccs = torch.stack(padded_mfccs)
    labels = torch.tensor(labels)
    return mfccs, labels


# Create a label map for characters A-Z (0-25) and numbers 0-9 (26-35)
label_map = {chr(i): i - 65 for i in range(65, 91)}  # A-Z mapped to 0-25
label_map.update({str(i): i + 26 for i in range(10)})  # 0-9 mapped to 26-35

import torchaudio.transforms as transforms

class MorseCodeDataset(Dataset):
    def __init__(self, data_path, labels):
        self.data_path = data_path
        self.labels = labels
        self.files = [f"{data_path}/{label}.wav" for label in labels]

        # Specify MFCC transformation with desired mel filter bank count
        self.mfcc_transform = transforms.MFCC(
            sample_rate=16000,
            n_mfcc=40,
            melkwargs={'n_fft': 400, 'hop_length': 160, 'n_mels': 64, 'center': False}
        )
    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        waveform, _ = torchaudio.load(self.files[idx])
        mfcc = self.mfcc_transform(waveform).squeeze(0)  # Apply MFCC transformation
        label = self.labels[idx]
        numeric_label = label_map[label]  # Convert label to numeric using label_map
        return mfcc, numeric_label


class MorseCodeTransformer(nn.Module):
    def __init__(self, input_dim, num_classes, nhead=8, num_layers=4):
        super().__init__()
        self.embedding = nn.Linear(input_dim, 512)  # Adjust input_dim to 40
        encoder_layer = TransformerEncoderLayer(d_model=512, nhead=nhead, batch_first=True)
        self.transformer = TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        # x: [batch_size, 40, 1544]
        x = x.transpose(1, 2)  # Transpose to [batch_size, 1544, 40]
        x = self.embedding(x)  # Apply embedding: now [batch_size, 1544, 512]
        x = x.permute(1, 0, 2)  # Permute to [1544, batch_size, 512] for Transformer
        x = self.transformer(x)  # Pass through transformer
        x = x.mean(dim=0)  # Aggregate sequence dimension to get [batch_size, 512]
        return self.fc(x)  # Pass through final fully connected layer

# Initialize dataset and model
labels = [chr(i) for i in range(65, 91)] + [str(i) for i in range(10)]
dataset = MorseCodeDataset(data_path='/content/drive/MyDrive/Project I/training_data', labels=labels)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True, collate_fn=collate_fn)

model = MorseCodeTransformer(input_dim=40, num_classes=36)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)

# Lists to store the losses and accuracies for plotting
train_losses = []
train_accuracies = []

# Training loop
for epoch in range(10):
    total_loss = 0.0
    correct_predictions = 0
    total_samples = 0

    for mfcc, label in dataloader:
        optimizer.zero_grad()
        output = model(mfcc)
        loss = criterion(output, label)
        loss.backward()
        optimizer.step()

        # Calculate training metrics
        total_loss += loss.item()  # Accumulate the loss for this batch
        _, predicted = torch.max(output, 1)  # Get the predicted labels
        correct_predictions += (predicted == label).sum().item()  # Compare with true labels
        total_samples += label.size(0)  # Total number of samples in the batch

    avg_loss = total_loss / len(dataloader)  # Average loss for the epoch
    accuracy = correct_predictions / total_samples  # Accuracy for the epoch

    train_losses.append(avg_loss)
    train_accuracies.append(accuracy)

    print(f"Epoch [{epoch+1}/10], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")

# Optionally, plot the training loss and accuracy
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))

# Plot Loss
plt.subplot(1, 2, 1)
plt.plot(range(1, 11), train_losses, label='Training Loss', color='blue')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training Loss Over Epochs')
plt.legend()

# Plot Accuracy
plt.subplot(1, 2, 2)
plt.plot(range(1, 11), train_accuracies, label='Training Accuracy', color='green')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.title('Training Accuracy Over Epochs')
plt.legend()

plt.tight_layout()
plt.show()


print(labels)