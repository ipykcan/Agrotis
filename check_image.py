from PIL import Image
import os

image_path = "dataset/plantvillage/Tomato___Early_blight/0a2726e0-3358-4a46-b6dc-563a5a9f2bdf___RS_Erly.B 7860.JPG"  # Replace with your image path
try:
    img = Image.open(image_path)
    img.verify()  # Check for corruption
    img = Image.open(image_path)  # Reopen for format check
    print(f"Image format: {img.format}, Size: {img.size}, Mode: {img.mode}")
except Exception as e:
    print(f"Error: {str(e)}")