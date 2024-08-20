import json
import os
from crewai import Agent, Task, Crew, Process
from langchain.llms import OpenAI
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO
import logging
import tqdm
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize the OpenAI language model
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the agents
image_generator = Agent(
    role='Image Generator',
    goal='Generate stylized images for Terrible Teddies cards',
    backstory='You are an AI artist specializing in creating stylized teddy bear illustrations',
    verbose=True,
    llm=llm
)

card_designer = Agent(
    role='Card Designer',
    goal='Design balanced and interesting cards for the Terrible Teddies game',
    backstory='You are a game designer with expertise in card game mechanics and balance',
    verbose=True,
    llm=llm
)

rule_writer = Agent(
    role='Rule Writer',
    goal='Create clear and engaging rules for the Terrible Teddies game',
    backstory='You are an experienced technical writer specializing in game rule books',
    verbose=True,
    llm=llm
)

lore_creator = Agent(
    role='Lore Creator',
    goal='Develop a rich, satirical backstory for the Terrible Teddies universe',
    backstory='You are a creative writer skilled in crafting humorous and edgy lore for adult-themed games',
    verbose=True,
    llm=llm
)

# Define the tasks
generate_card_images = Task(
    description='Generate 40 unique, stylized teddy bear images for game cards based on the provided data',
    agent=image_generator,
    expected_output="A list of 40 image URLs for the generated card images"
)

design_cards = Task(
    description='Create 40 balanced cards with names, types, energy costs, and effects based on the provided teddy bear data',
    agent=card_designer,
    expected_output="A JSON string containing an array of 40 card objects with properties: name, type, energy_cost, effect"
)

write_game_rules = Task(
    description='Write comprehensive rules for the Terrible Teddies card game',
    agent=rule_writer,
    expected_output="A markdown formatted string containing the complete game rules"
)

create_game_lore = Task(
    description='Develop a satirical and edgy backstory for the Terrible Teddies universe',
    agent=lore_creator,
    expected_output="A markdown formatted string containing the game's lore and backstory"
)

# Create the crew
asset_generation_crew = Crew(
    agents=[image_generator, card_designer, rule_writer, lore_creator],
    tasks=[generate_card_images, design_cards, write_game_rules, create_game_lore],
    verbose=2,
    process=Process.sequential
)

# Process and save the results
def save_image(image_url, filename):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        os.makedirs('public/card_images', exist_ok=True)
        img.save(f"public/card_images/{filename}.png")
        logging.info(f"{Fore.GREEN}Image saved: {filename}.png{Style.RESET_ALL}")
    except requests.RequestException as e:
        logging.error(f"{Fore.RED}Error downloading image: {e}{Style.RESET_ALL}")
    except IOError as e:
        logging.error(f"{Fore.RED}Error saving image: {e}{Style.RESET_ALL}")

def process_results(results):
    try:
        card_images = json.loads(results[0])
        card_designs = json.loads(results[1])
        game_rules = results[2]
        game_lore = results[3]

        # Save card images
        print(f"{Fore.CYAN}Saving card images...{Style.RESET_ALL}")
        for i, image_url in tqdm.tqdm(enumerate(card_images), total=len(card_images)):
            save_image(image_url, f"card_{i+1}")

        # Save card designs
        os.makedirs('src/data', exist_ok=True)
        with open('src/data/cards.json', 'w') as f:
            json.dump(card_designs, f, indent=2)
        logging.info(f"{Fore.GREEN}Card designs saved to src/data/cards.json{Style.RESET_ALL}")

        # Save game rules
        with open('src/data/game_rules.md', 'w') as f:
            f.write(game_rules)
        logging.info(f"{Fore.GREEN}Game rules saved to src/data/game_rules.md{Style.RESET_ALL}")

        # Save game lore
        with open('src/data/game_lore.md', 'w') as f:
            f.write(game_lore)
        logging.info(f"{Fore.GREEN}Game lore saved to src/data/game_lore.md{Style.RESET_ALL}")

    except json.JSONDecodeError as e:
        logging.error(f"{Fore.RED}Error decoding JSON: {e}{Style.RESET_ALL}")
    except IOError as e:
        logging.error(f"{Fore.RED}Error writing to file: {e}{Style.RESET_ALL}")

def run_crew():
    try:
        print(f"{Fore.YELLOW}Starting asset generation process...{Style.RESET_ALL}")
        results = asset_generation_crew.kickoff()
        print(f"{Fore.GREEN}Asset generation process completed.{Style.RESET_ALL}")
        process_results(results)
        print(f"{Fore.GREEN}All assets have been processed and saved.{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}An error occurred during the crew run: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    run_crew()