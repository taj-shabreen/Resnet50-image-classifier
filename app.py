from flask import Flask, render_template, request
import os
from PIL import Image
import torch
from torchvision import models, transforms
import json
import requests

app = Flask(__name__)

# Folder to save uploaded images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load ResNet50 model
model = models.resnet50(pretrained=True)
model.eval()

# Load ImageNet labels
LABELS_URL = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
labels = json.loads(requests.get(LABELS_URL).content)

# Image preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


@app.route('/')
def index():
    return render_template('index.html', prediction=None)


@app.route('/predict', methods=['POST'])
def predict():
    # Get file from form submission
    file = request.files['file']

    if file:
        # Save the uploaded file to 'uploads' folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Open the saved image
        img = Image.open(filepath).convert("RGB")
        input_tensor = preprocess(img).unsqueeze(0)

        # Run the model without tracking gradients
        with torch.no_grad():
            output = model(input_tensor)
            _, predicted = torch.max(output, 1)
            label = labels[predicted.item()]

        return render_template('index.html', prediction=label, image_path=file.filename)

    return render_template('index.html', prediction="No image uploaded", image_path=None)


if __name__ == '__main__':
    app.run(debug=True)
