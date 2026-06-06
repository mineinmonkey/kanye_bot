import logging

import discord

import commands
import constants
import utils

logger = logging.getLogger(__name__)


def main():
    bot = discord.Bot(activity=constants.BOT_ACTIVITY, intents=constants.INTENTS)
    logging.basicConfig(level=logging.INFO)
    utils.wait_for_internet()
    commands.setup(bot)
    bot.run(constants.TOKEN)


if __name__ == "__main__":
    main()
