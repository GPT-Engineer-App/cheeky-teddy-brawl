import sys
import subprocess
import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_and_install_packages():
    required_packages = ['openai', 'supabase', 'python-dotenv', 'Pillow', 'requests']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            logging.info(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    logging.info("All required packages are installed.")

# Check and install required packages
check_and_install_packages()

# Now import the required modules
from openai import OpenAI
from supabase import create_client, Client
import random

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize Supabase client
supabase: Client = create_client(os.environ.get("VITE_SUPABASE_PROJECT_URL"), os.environ.get("VITE_SUPABASE_API_KEY"))

CARD_TYPES = ['Action', 'Trap', 'Special', 'Defense', 'Boost']

def ensure_table_structure():
    try:
        # Check if the energy_cost column exists
        result = supabase.table("generated_images").select("energy_cost").limit(1).execute()
        if 'error' in result:
            # If the column doesn't exist, add it
            supabase.table("generated_images").alter().add("energy_cost", "int4").execute()
            logging.info("Added energy_cost column to generated_images table")
    except Exception as e:
        logging.error(f"Error ensuring table structure: {e}")

def generate_card_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return None

def generate_and_store_card(name, type, energy_cost):
    prompt = f"A cute teddy bear as a {type} card for a card game called Terrible Teddies. The teddy should look {random.choice(['mischievous', 'adorable', 'fierce', 'sleepy', 'excited'])} and be doing an action related to its type. Cartoon style, vibrant colors, white background."
    image_url = generate_card_image(prompt)
    
    if image_url:
        card_data = {
            "name": name,
            "type": type,
            "url": image_url,
            "prompt": prompt,
            "energy_cost": energy_cost
        }
        
        try:
            result = supabase.table("generated_images").insert(card_data).execute()
            logging.info(f"Generated and stored card: {name}")
            return result
        except Exception as e:
            logging.error(f"Error storing card data: {e}")
    else:
        logging.error(f"Failed to generate image for card: {name}")
    
    return None

def main():
    logging.info("Starting asset generation for Terrible Teddies...")
    
    ensure_table_structure()
    
    for card_type in CARD_TYPES:
        for i in range(8):  # Generate 8 cards of each type
            name = f"{card_type} Teddy {i+1}"
            energy_cost = random.randint(1, 5)
            result = generate_and_store_card(name, card_type, energy_cost)
            if result:
                logging.info(f"Successfully generated and stored {name}")
            else:
                logging.warning(f"Failed to generate or store {name}")
    
    logging.info("Asset generation complete!")

if __name__ == "__main__":
    main()