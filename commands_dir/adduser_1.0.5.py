import json
from twitchio.ext import commands
import os
import re

command_name = "adduser"
description = "aggiunge un utente"

enable_access_control = True
access_denied_message = "{ctx.author.name} non sei autorizzato ad eseguire questo comando!"

err_missing_parameter = "{ctx.author.name} specifica un nome utente dopo il comando !{command_name}"
user_added = "Utente {username} aggiunto."

with open("config.json", "r") as file:
    data = json.load(file)

with open("enabled_users.json", "r") as file:
    enabled_users = json.load(file)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=data["token"],
            prefix=data["prefix"],
            initial_channels=data["initial_channels"],
        )

    async def event_ready(self):
        print(f"Command \"{command_name}\" loaded")

    @commands.command(name=command_name)
    async def adduser(self, ctx: commands.Context, username: str = None):

        if enable_access_control and ctx.author.name.lower() not in enabled_users:
            await ctx.send(access_denied_message.format(ctx=ctx))
            return

        if not username:
            await ctx.send(err_missing_parameter.format(ctx=ctx, command_name=command_name))
            return

        usr = re.sub(r"[^a-zA-Z0-9_]", "", username).replace("@", "").lower()
        os.makedirs(f"usr/{usr}/media/sounds/", exist_ok=True)
        os.makedirs(f"usr/{usr}/media/songs/", exist_ok=True)

        await ctx.send(user_added.format(username=username))

bot = Bot()
bot.run()
