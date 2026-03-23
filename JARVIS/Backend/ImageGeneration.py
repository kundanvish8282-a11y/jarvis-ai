import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import dotenv_values
import os
from time import sleep

# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = "Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces in the prompt with underscores

    # Generate the filenames for the images
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    for jpg_file in files:
        image_path = os.path.join(folder_path, f'generated_{jpg_file}')
        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")


# API details for the Hugging Face Text-to-Image model
API_URL = "https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image"
env_vars = dotenv_values(".env")
HuggingFaceAPIKey = env_vars.get("HuggingFaceAPIKey")  # Retrieve the API key
headers = {"Authorization": f"Bearer {HuggingFaceAPIKey}"}


# Async function to send a query to the Hugging Face API
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content


# Async function to generate images based on the given prompt
async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness-maximum, Ultra High details, high resolution, seed {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    # Save the generated images to files
    for i, image_bytes in enumerate(image_bytes_list):
        with open(os.path.join("Data", f"generated_{prompt.replace(' ', '_')}{i + 1}.jpg"), "wb") as f:
            f.write(image_bytes)


# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)


while True:
    try:
        with open("Frontend/Files/ImageGeneration.data", "r") as f:
            data: str = f.read().strip()

        if "," not in data or not data:
            print("Invalid data format in ImageGeneration.data. Skipping...")
            sleep(1)
            continue

        prompt, status = data.split(",", 1)

        # If the status indicates an image generation request
        if status.strip() == "True":
            print("Generating Images...")
            GenerateImages(prompt=prompt.strip())

            # Reset the status in the file after generating images
            with open("Frontend/Files/ImageGeneration.data", "w") as f:
                f.write("False, False")
                break  # Exit the loop after processing the request
        else:
            sleep(1)  # Wait for 1 second before checking again
    except Exception as e:
        print(f"An error occurred: {e}")
        sleep(1)
