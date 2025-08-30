import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from fastapi import UploadFile, HTTPException
import logging
import mimetypes
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the pre-trained TFLite model
try:
    if not os.path.exists("ml/disease_model.tflite"):
        raise FileNotFoundError("TFLite model file not found")
    interpreter = tf.lite.Interpreter(model_path="ml/disease_model.tflite")
    interpreter.allocate_tensors()
    logger.info("TFLite model loaded successfully")
except Exception as e:
    logger.error(f"Error loading TFLite model: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Get class labels from PlantVillage dataset
try:
    if not os.path.exists("dataset/plantvillage/"):
        raise FileNotFoundError("PlantVillage dataset not found")
    disease_labels = list(tf.keras.preprocessing.image_dataset_from_directory(
        "dataset/plantvillage/", 
        labels="inferred"
    ).class_names)
    logger.info(f"Loaded {len(disease_labels)} class labels: {disease_labels}")
except Exception as e:
    logger.error(f"Error loading PlantVillage labels: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Error loading dataset labels: {str(e)}")

# Pesticide recommendation database
pesticide_recommendations = {
    "Tomato___healthy": "No treatment needed; maintain regular care.",
    "Tomato___Bacterial_spot": "Apply copper-based bactericides like Kocide 3000.",
    "Tomato___Early_blight": "Apply chlorothalonil or mancozeb; rotate crops.",
    "Tomato___Late_blight": "Apply fungicides like Ridomil Gold; remove affected leaves.",
    "Corn___healthy": "No treatment needed; maintain regular care.",
    "Corn___Common_rust": "Use fungicides like azoxystrobin; improve air circulation.",
    "Corn___Northern_Leaf_Blight": "Apply propiconazole; ensure crop rotation.",
    "Potato___healthy": "No treatment needed; maintain regular care.",
    "Potato___Early_blight": "Apply chlorothalonil or mancozeb; rotate crops.",
    "Potato___Late_blight": "Use metalaxyl-based fungicides; avoid overhead irrigation."
}

async def predict_disease(file: UploadFile):
    try:
        # Validate file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ('.jpg', '.jpeg', '.png'):
            logger.error(f"Invalid file extension: {file_extension}")
            raise HTTPException(status_code=400, detail="Only JPEG or PNG images are supported.")

        # Read image data
        image_data = await file.read()
        logger.info(f"Received image: {file.filename}, size: {len(image_data)} bytes")
        if len(image_data) == 0:
            logger.error("Empty image file")
            raise HTTPException(status_code=400, detail="Empty image file.")

        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file.filename)
        if mime_type not in ('image/jpeg', 'image/png'):
            logger.error(f"Invalid MIME type: {mime_type}")
            raise HTTPException(status_code=400, detail="Invalid image format. Only JPEG or PNG supported.")

        # Process image
        try:
            image_stream = BytesIO(image_data)
            image = Image.open(image_stream)
            image.verify()  # Verify image integrity
            image_stream.seek(0)  # Reset stream pointer
            image = Image.open(image_stream).convert('RGB').resize((224, 224))
            logger.info(f"Image format: {image.format}, Size: {image.size}, Mode: {image.mode}")
            image_array = np.array(image, dtype=np.float32) / 255.0
            image_array = np.expand_dims(image_array, axis=0)
        except UnidentifiedImageError as e:
            logger.error(f"UnidentifiedImageError: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid or corrupted image file. Please upload a valid JPEG or PNG image.")
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], image_array)

        # Run inference
        interpreter.invoke()

        # Get output
        output_data = interpreter.get_tensor(output_details[0]['index'])
        predicted_index = np.argmax(output_data[0])
        confidence = float(output_data[0][predicted_index])

        # Get recommendation
        disease = disease_labels[predicted_index]
        recommendation = pesticide_recommendations.get(disease, f"Consult local agricultural extension services for {disease}.")
        logger.info(f"Prediction: {disease}, Confidence: {confidence}")

        return {
            "disease": disease,
            "confidence": confidence,
            "recommendation": recommendation
        }
    except Exception as e:
        logger.error(f"Unexpected error in predict_disease: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")