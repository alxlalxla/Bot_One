from twitchio.ext import commands
import os
import json
import subprocess
import random
import time
import re

# This script requires:
# mpv
# To install it on Debian/Ubuntu, run:
# apt install mpv

command_name = "s"
description = "Riproduce un suono"
sounds_dir = "./media/sounds/"

enable_access_control = False
access_denied_message = "{ctx.author.name} non sei autorizzato ad eseguire questo comando!"

cooldown = 30
message_wait = "{ctx.author.name} aspetta ancora {remaining_time:.0f} secondi prima di utilizzare di nuovo il comando !{command_name}."

mpv_params = ""
message_does_not_exist = "{ctx.author.name} il suono \"{file_name}\" non esiste! I suoni disponibili sono: {sounds_available}."
message_play = "Riproduzione del suono \"{file_name}\" in corso..."

message_random = "{ctx.author.name} {random_answer} I suoni disponibili sono: {sounds_available}."
answer_list = [
    "specifica il nome del suono da riprodurre.",
    f"prova con \"!{command_name} NomeSuono\".",
    f"digita \"!{command_name} NomeSuono\"."
]

with open("config.json", "r") as file:
    data = json.load(file)

with open("enabled_users.json", "r") as file:
    enabled_users = json.load(file)

last_uses = {}

os.makedirs(sounds_dir, exist_ok=True)
placeholder_file_path = os.path.join(sounds_dir, "put_mp3_files_here")
if not os.path.isfile(placeholder_file_path):
    with open(placeholder_file_path, 'w') as placeholder_file:
        pass

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
    async def handle_command(self, ctx: commands.Context, file_name: str = None):
        for filename in os.listdir(sounds_dir):
            if filename.endswith(".mp3"):
                if not re.match(r'^[a-z0-9]+\.mp3$', filename):
                    sanitized_name = re.sub(r'[^a-zA-Z0-9]', '_', filename.split('.')[0]).lower() + '.mp3'
                    original_file_path = os.path.join(sounds_dir, filename)
                    sanitized_file_path = os.path.join(sounds_dir, sanitized_name)
                    os.rename(original_file_path, sanitized_file_path)

        if enable_access_control and ctx.author.name.lower() not in enabled_users:
            await ctx.send(access_denied_message.format(ctx=ctx))
            return

        if file_name:
            file_name = file_name.lower()

        sounds_available = [f.split(".")[0] for f in os.listdir(sounds_dir) if f.endswith(".mp3")]

        if not file_name:
            await ctx.send(message_random.format(ctx=ctx, random_answer=random.choice(answer_list), sounds_available=', '.join(sounds_available)))
            return

        if not os.path.isfile(os.path.join(sounds_dir, f"{file_name}.mp3")):
            await ctx.send(message_does_not_exist.format(ctx=ctx, file_name=file_name, sounds_available=', '.join(sounds_available)))
            return

        current_time = time.time()
        user_id = ctx.author.id

        if user_id in last_uses and current_time - last_uses[user_id] < cooldown:
            remaining_time = cooldown - (current_time - last_uses[user_id])
            await ctx.send(message_wait.format(ctx=ctx, command_name=command_name, remaining_time=remaining_time))
            return

        last_uses[user_id] = current_time

        play_sound = f"mpv {mpv_params} {sounds_dir}{file_name}.mp3"

        process = subprocess.Popen(play_sound, shell=True)

        await ctx.send(message_play.format(ctx=ctx, file_name=file_name))

bot = Bot()
bot.run()
