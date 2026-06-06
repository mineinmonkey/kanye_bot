import os

import discord
import dotenv

dotenv.load_dotenv()
TOKEN = os.environ.get("KANYE_BOT_TOKEN")

INTENTS = discord.Intents.none()
INTENTS.message_content = True
INTENTS.messages = True
INTENTS.members = True

BOT_ACTIVITY = discord.Game(name="Playing with himself")

COUNTER_JSON_PATH = os.path.join(os.path.dirname(__file__), "data/kanyecounter.json")
GIF_JSON_PATH = os.path.join(os.path.dirname(__file__), "data/kanyegif.json")
REACT_JSON_PATH = os.path.join(os.path.dirname(__file__), "data/kanyereact.json")
