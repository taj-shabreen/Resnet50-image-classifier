import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import requests
from io import BytesIO

# Step 1: Load a Pretrained ResNet Model
model = models.resnet50(pretrained=True)
model.eval()  # Set the model to evaluation mode

# Step 2: Define Preprocessing Steps for ImageNet
# ImageNet uses 224x224 images, normalize to the dataset mean and std
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Step 3: Load Image from the Web or Locally
# You can load the image directly from the web
img_url = "https://up.yimg.com/ib/th?id=OIP.o2uLuzW-jnMCdmgTQEjgtQHaE8&pid=Api&rs=1&c=1&qlt=95&w=166&h=110"  # Replace with actual image URL
response = requests.get(img_url)
img = Image.open(BytesIO(response.content))

# Step 4: Preprocess the Image
img_tensor = preprocess(img)
img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension

# Step 5: Run Inference with the Pretrained Model
with torch.no_grad():
    output = model(img_tensor)

# Step 6: Get Predicted Class
# Load ImageNet labels
LABELS_URL = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
labels = requests.get(LABELS_URL).json()

# Get the predicted class index
_, predicted_idx = torch.max(output, 1)

# Step 7: Output the Prediction
predicted_label = labels[predicted_idx.item()]
print(f'Predicted label: {predicted_label}')
