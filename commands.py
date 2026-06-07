import logging
import os
import re
from random import choice, choices

import discord
from discord.ext import commands

import constants
import utils

logger = logging.getLogger(__name__)


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # kanyecoin
    @commands.slash_command(description="Feeling freaky?", name="kanyecoin")
    async def kanye_coin(self, ctx: discord.ApplicationContext):
        user_id: str = str(ctx.user.id)
        username: str = ctx.user.name

        counter_json = utils.load_json(constants.COUNTER_JSON_PATH)
        gif_json = utils.load_json(constants.GIF_JSON_PATH)

        # init user with 0 flips if they aren't in json file
        if user_id not in counter_json["users"]:
            logger.info(f"User {username}/{user_id} does not exist, making entry")
            counter_json["users"][user_id] = dict()
            counter_json["users"][user_id]["name"] = username
            counter_json["users"][user_id]["count"] = 0

        if username != counter_json["users"][user_id]["name"]:
            logger.info("Usernames don't match, changing")
            logger.info(
                f"Old: {counter_json['users'][user_id]['name']} New: {username}"
            )
            counter_json["users"][user_id]["name"] = username

        try:
            random_kanye = choice(
                choices(list(gif_json["gifs"].values()), weights=gif_json["weights"])[0]
            )["url"]
            counter_json["total"] += 1
            counter_json["users"][user_id]["count"] += 1
        except Exception:
            await ctx.respond("Kanye broken?")
            return

        await ctx.respond(random_kanye)

        utils.save_json(counter_json, constants.COUNTER_JSON_PATH)

    # kanyetotal
    @commands.slash_command(
        description="How many times have we felt freaky?", name="kanyetotal"
    )
    async def kanye_total(self, ctx):
        total_flips = utils.load_json(constants.COUNTER_JSON_PATH)["total"]

        await ctx.respond(f"The /kanyecoin has been flipped {total_flips} times")

    @commands.slash_command(
        description="How many times have you felt freaky?", name="kanyecounter"
    )
    async def kanye_counter(self, ctx: discord.ApplicationContext):
        user_id: str = str(ctx.user.id)

        counter_json = utils.load_json(constants.COUNTER_JSON_PATH)

        try:
            user_flips = counter_json["users"][user_id]["count"]
        except KeyError:
            await ctx.respond("You haven't flipped the coin yet!")
            return 1

        await ctx.respond(f"You have flipped the /kanyecoin {user_flips} times")

    # addgif
    @commands.slash_command(
        description="Add a gif to kanyecoin",
        name="addgif",
        default_member_permissions=discord.Permissions(administrator=True),
    )
    @discord.option("url", type=discord.SlashCommandOptionType.string)
    @discord.option("name", type=discord.SlashCommandOptionType.string)
    @discord.option(
        "group",
        required=True,
        type=discord.SlashCommandOptionType.string,
        choices=["good", "bad", "lbad", "lgood"],
    )
    async def add_gif(
        self, ctx: discord.ApplicationContext, url: str, name: str, group: str
    ):
        match_url = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
        if re.match(match_url, url) is re.Match:
            await ctx.respond(
                "Invalid URL, must be in the form `http(s)://*.*`", ephemeral=True
            )
            return

        gif_json = utils.load_json(constants.GIF_JSON_PATH)

        def value_generator():
            for gif_list in gif_json["gifs"].values():
                for gif_dict in gif_list:
                    yield gif_dict["name"]
                    yield gif_dict["url"]

        if url in value_generator():
            await ctx.respond("URL already exists", ephemeral=True)
            return
        elif name in value_generator():
            await ctx.respond("Name already exists", ephemeral=True)
            return

        gif_json["gifs"][group].append({"name": name, "url": url})
        await ctx.respond("Successfully added GIF", ephemeral=True)

        utils.save_json(gif_json, constants.GIF_JSON_PATH, indent=2)

    @commands.slash_command(
        description="Make Kanye say sumn",
        name="say",
        default_member_permissions=discord.Permissions(administrator=True),
    )
    @discord.option(
        "what_to_say",
        description="What should I say?",
        type=discord.SlashCommandOptionType.string,
    )
    @discord.option(
        "channel",
        description="What channel should I send it to?",
        required=False,
        type=discord.SlashCommandOptionType.channel,
    )
    async def say(
        self,
        ctx: discord.ApplicationContext,
        what_to_say: str,
        channel: discord.TextChannel | None,
    ):
        if channel is None:
            await ctx.channel.send(what_to_say)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        else:
            await channel.send(what_to_say)

    # reaction
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        react_list: dict[str, dict[str, str]] = utils.load_json(
            constants.REACT_JSON_PATH
        )

        found: list[tuple[int, str]] = [
            (message.content.lower().find(s), s)
            for s in react_list.keys()
            if message.content.lower().find(s) != -1
        ]

        found.sort()
        ordered_strings = [s for index, s in found]
        for string in ordered_strings:
            if react_list[string]["type"] == "file":
                file_path = os.path.join(
                    os.path.dirname(__file__),
                    "data/reacts/",
                    react_list[string]["response"],
                )

                try:
                    with open(file_path, "rb") as f:
                        await message.reply(file=discord.File(f))
                except OSError:
                    logger.error(f"File {file_path} not found")
            elif react_list[string]["type"] == "text":
                await message.reply(react_list[string]["response"])
            else:
                logger.error(f"Unrecognized type: {react_list[string]['type']}")


def setup(bot: discord.Bot):
    bot.add_cog(Commands(bot))
