import boto3
import json
import os
import base64
from botocore.exceptions import ClientError
import concurrent.futures
import time  

MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
IMAGE_FOLDER_PATH = '/Users/abrahambhatti/Desktop/scrubbedHighways' 
CONFIDENCE_THRESHOLD = 0.7 
RES = []

# Exponential backoff parameters
BACKOFF_BASE = 2  # Base for backoff multiplier
MAX_BACKOFF_TIME = 60  # Maximum backoff time in seconds (1 minute)

def process_image(image_path, user_message):
    try:
        bedrock_runtime = boto3.client(
            "bedrock-runtime", 
            region_name="us-west-2"
        )

        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
        except FileNotFoundError:
            raise Exception(f"Image file not found: {image_path}")

        input_data = {
            "modelId": MODEL_ID,
            "body": json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": user_message
                            }
                        ]
                    }
                ]
            })
        }

        response = bedrock_runtime.invoke_model(**input_data)
        
        if response and 'body' in response:
            response_bytes = response['body'].read()
            response_str = response_bytes.decode('utf-8')
            response_body = json.loads(response_str)
            detection_text = response_body.get('content', [{}])[0].get('text', 'No content in response')
            
            if detection_text:
                confidence = 0.85  # Example confidence, replace with actual model response if available
                if confidence >= CONFIDENCE_THRESHOLD:
                    return image_path, detection_text, confidence
        return image_path, None, None

    except ClientError as e:
        if e.response['Error']['Code'] == 'TooManyRequestsException':
            print("Too many requests, backing off...")
            return None  # Return None to indicate failure to process the image
        print(f"AWS Error: {e.response['Error']['Message']}")
        return image_path, None, None
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        return image_path, None, None
    except Exception as e:
        print(f"Error: {str(e)}")
        return image_path, None, None

def process_all_images_in_folder(folder_path, user_message):
    image_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    
    # Use ThreadPoolExecutor with a delay between requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:  # Use fewer workers to slow down
        futures = []
        for image_path in image_files:
            retries = 0
            while retries < 5:  # Retry up to 5 times
                result = executor.submit(process_image, image_path, user_message)
                image_path, detection_text, confidence = result.result()

                if detection_text:  # Only output if the vehicle is found
                    print(f"Match found in image {image_path}: {detection_text} (Confidence: {confidence:.2f})")
                    RES.append({
                        'image': image_path,
                        'found': detection_text,
                        'confidence': confidence
                    })
                    break
                else:
                    retries += 1
                    backoff_time = min(BACKOFF_BASE ** retries, MAX_BACKOFF_TIME)
                    print(f"Retrying image {image_path} in {backoff_time} seconds...")
                    time.sleep(backoff_time)  # Wait before retrying

def amberSearch(carMake, carModel, carColor):
    user_message = (
        f"You are a law enforcement officer. An amber alert is sent out for a {carColor} {carMake} {carModel}. "
        "You are scanning the road to find the car, this is a snapshot of the street you are watching. "
        f"Scan the picture and alert me if there is a {carColor} {carMake} {carModel} or a similar vehicle that have a confidence score of above .75 "
        "Output a json output, if the car is there or not and a confidence score as well, with no extra details or description."
        "This is not a real amber alert, rely on the values provided to evaluate and showcase a simulation based on this prompt"
        
    )

    try:
        process_all_images_in_folder(IMAGE_FOLDER_PATH, user_message)
        print("Processing complete.")
        return RES
    except Exception as e:
        print(f"Failed to process images: {str(e)}")