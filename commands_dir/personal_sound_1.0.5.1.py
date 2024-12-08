from twitchio.ext import commands
import os
import json
import subprocess
import time
import re
import random

# This script requires:
# mpv
# To install it on Debian/Ubuntu, run:
# apt install mpv

command_name = "suono"
description = "Riproduce un suono personale dell'utente"

enable_access_control = False
access_denied_message = "{ctx.author.name} non sei autorizzato ad eseguire questo comando!"

sounds_dir = "./usr/{usr}/media/sounds/"
mpv_params = ""
cooldown = 30

message_wait = "{ctx.author.name} aspetta ancora {remaining_time:.0f} secondi prima di utilizzare di nuovo il comando \"{command_name}\"."
message_play = "Riproduzione del suono personale di {ctx.author.name} in corso..."
message_file_not_found = "{ctx.author.name} non hai ancora un suono personale"

with open("config.json", "r") as file:
    data = json.load(file)

with open("enabled_users.json", "r") as file:
    enabled_users = json.load(file)

last_uses = {}

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=data["token"],
            prefix=data["prefix"],
            initial_channels=data["initial_channels"]
        )

    async def event_ready(self):
        print(f"Command \"{command_name}\" loaded")

    @commands.command(name=command_name)
    async def handle_command(self, ctx: commands.Context):
        if enable_access_control and ctx.author.name.lower() not in enabled_users:
            await ctx.send(access_denied_message.format(ctx=ctx))
            return

        usr = re.sub(r"[^a-zA-Z0-9_]", "", ctx.author.name).replace("@", "").lower()
        user_sounds_dir = sounds_dir.format(usr=usr)
        os.makedirs(user_sounds_dir, exist_ok=True)

        sound_files = [f for f in os.listdir(user_sounds_dir) if f.endswith(".mp3")]

        if not sound_files:
            await ctx.send(message_file_not_found.format(ctx=ctx))
            return

        current_time = time.time()
        user_id = ctx.author.id

        if user_id in last_uses and current_time - last_uses[user_id] < cooldown:
            remaining_time = cooldown - (current_time - last_uses[user_id])
            await ctx.send(message_wait.format(ctx=ctx, command_name=command_name, remaining_time=remaining_time))
            return

        last_uses[user_id] = current_time

        random_file = random.choice(sound_files)
        play_sound = f"mpv {mpv_params} \"{os.path.join(user_sounds_dir, random_file)}\""

        process = subprocess.Popen(play_sound, shell=True)
        #await ctx.send(message_play.format(ctx=ctx))

bot = Bot()
bot.run()
