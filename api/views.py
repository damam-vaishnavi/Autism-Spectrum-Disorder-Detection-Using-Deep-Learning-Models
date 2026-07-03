from django.shortcuts import render 
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Austin
from django.contrib import messages 
from torchvision import transforms, models
from PIL import Image
import os 
import torch 
# Create your views here. 
def index(request): 
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password: 
            if Austin.objects.filter(email=email).exists():
                messages.error(request, f"This Email ID already Exists, Try Another")
                return render(request, 'register.html')
            else: 
                query = Austin(name=name, email=email, password=password)
                query.save()
                messages.success(request, f"Registration Successfuly Completed, Thank you")
                return render(request, 'login.html')
        else: 
            messages.error(request, f"Password and Confirm Password does not match")
            return render(request, 'register.html')
    return render(request, 'register.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = Austin.objects.filter(email=email).first()

        if user:
            if user.password == password:
                return render(request, 'home.html')
            else: 
                messages.error(request, f"Invalid password")
                return render(request, 'login.html')
        else: 
            messages.error(request, f"This email Id is not exists, Please Go Register")
            return render(request, 'login.html')

    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html') 

# Function to load the model
def load_model(model, model_name="model.pth", device='cpu'):
    model.load_state_dict(torch.load(model_name, map_location=device))
    model.eval()  # Set the model to evaluation mode
    print(f"Model {model_name} loaded successfully!")
    return model

# Function to predict the class of a single image
def predict_single_image(model, image_path, device):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # Resize the image to match input size
        transforms.ToTensor(),  # Convert the image to a tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize the image
    ])
    
    # Load the image
    img = Image.open(image_path).convert('RGB')  # Ensure it's in RGB format
    
    # Pre-process the image
    img = transform(img).unsqueeze(0)  # Add batch dimension (1, C, H, W)
    img = img.to(device)  # Move to the correct device (GPU/CPU)
    
    # Make the prediction
    with torch.no_grad():  # No need to calculate gradients
        output = model(img)
    
    # Get the predicted class
    _, pred = torch.max(output, 1)
    return pred.item()  # Return the predicted class index

# View for handling the image upload and prediction
def detection(request):
    if request.method == 'POST' and request.FILES['image']:
        # Get the uploaded image
        uploaded_image = request.FILES['image']
        
        # Save the image to the media folder
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        image_path = fs.save(uploaded_image.name, uploaded_image)
        image_url = fs.url(image_path)

        # Set the device (GPU or CPU)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Define the model architecture (EfficientNet-B2)
        model = models.efficientnet_b2(pretrained=True)
        num_features = model.classifier[1].in_features
        model.classifier[1] = torch.nn.Linear(num_features, 2)  # Assuming binary classification

        # Load the trained model
        model = load_model(model, model_name="api/models/trained_effnet_b2.pth", device=device)

        # Get the prediction for the uploaded image
        predicted_class = predict_single_image(model, os.path.join(settings.MEDIA_ROOT, image_path), device)

        print(predicted_class)

        # Return the prediction result to the template
        context = {
            'image_url': image_url,
            'predicted_class': predicted_class,
        }
        return render(request, 'detection.html', context)

    return render(request, 'detection.html')