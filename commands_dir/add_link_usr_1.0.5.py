from twitchio.ext import commands
import json
import subprocess
import os
import time
import re

# This script requires:
# yt-dlp
# To install it on Debian/Ubuntu, run:
# apt install yt-dlp

command_name = "sr"
description = "aggiunge un link alla playlist utenti"
enable_access_control = False
access_denied_message = "{ctx.author.name} non sei autorizzato ad eseguire questo comando!"
show_queue = "coda"
queue_title = "coda: {titles}"
empty_queue = "{ctx.author.name} coda vuota, scrivi \"!{command_name} LinkYouTube\" per aggiungere un link"
message_invalid_youtube_link = "{ctx.author.name} link YouTube non valido, scrivi \"!{command_name} LinkYouTube\" per aggiungere un link oppure \"!{command_name} {show_queue}\" per vedere la coda"
message_added_to_playlist = "{ctx.author.name} aggiunge alla playlist: {title}"
message_wait = "{ctx.author.name} aspetta ancora {remaining_time:.0f} secondi prima di utilizzare di nuovo il comando !{command_name}."
playlist_dir = "./media/playlist/"
playlist_file = "user_playlist.json"
user_playlist_path = os.path.join(playlist_dir, playlist_file)
cooldown = 5
max_length = 300
message_max_length = "{ctx.author.name} il link supera la durata massima consentita che è di {max_length} secondi."

with open("config.json", "r") as file:
    data = json.load(file)

with open("enabled_users.json", "r") as file:
    enabled_users = json.load(file)

last_uses = {}

def convert_duration_to_seconds(duration):
    parts = duration.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    else:  # ss
        return int(parts[0])

def save_to_playlist(user_playlist_path, video_id, user_name, title):
    if not os.path.exists(os.path.dirname(user_playlist_path)):
        os.makedirs(os.path.dirname(user_playlist_path))
    if os.path.isfile(user_playlist_path):
        with open(user_playlist_path, "r") as f:
            playlist = json.load(f)
    else:
        playlist = []
    playlist.append({"video_id": video_id, "user_name": user_name, "title": title})
    with open(user_playlist_path, "w") as f:
        json.dump(playlist, f, indent=4)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=data["token"],
            prefix=data["prefix"],
            initial_channels=data["initial_channels"],
        )

    async def event_ready(self):
        print(f'Command "{command_name}" loaded')

    @commands.command(name=command_name)
    async def addlink_command(self, ctx, link: str = None):
        if enable_access_control and ctx.author.name.lower() not in enabled_users:
            await ctx.send(access_denied_message.format(ctx=ctx))
            return

        # Controlla se il comando è per mostrare la coda
        if link == show_queue:
            if os.path.isfile(user_playlist_path):
                with open(user_playlist_path, 'r') as f:
                    playlist_user = json.load(f)
            else:
                playlist_user = []

            if not playlist_user:
                await ctx.send(empty_queue.format(ctx=ctx, command_name=command_name))
                return

            queue_message = []
            for index, item in enumerate(playlist_user):
                queue_message.append(f"{index + 1}# {item['user_name']} - \"{item['title']}\"")

            await ctx.send(queue_title.format(titles=', '.join(queue_message)))
            return

        if not link:
            await ctx.send(message_invalid_youtube_link.format(ctx=ctx, command_name=command_name, show_queue=show_queue))
            return
        if '&list=' in link:
            link = link.split('&list=')[0]  # pulisce link YT
        current_time = time.time()
        user_id = ctx.author.name
        if last_uses.get(user_id) and current_time - last_uses[user_id] < cooldown:
            remaining_time = cooldown - (current_time - last_uses[user_id])
            await ctx.send(message_wait.format(ctx=ctx, command_name=command_name, remaining_time=remaining_time))
            return

        try:
            title = subprocess.check_output(['yt-dlp', '--get-title', link]).decode('utf-8').strip()
            title = re.sub(r'[^a-zA-Z0-9\s\-.,]', '', title)
            video_id = subprocess.check_output(['yt-dlp', '--get-id', link]).decode('utf-8').strip()
            duration = subprocess.check_output(['yt-dlp', '--get-duration', link]).decode('utf-8').strip()
            duration_seconds = convert_duration_to_seconds(duration)
            if duration_seconds > max_length:
                await ctx.send(message_max_length.format(ctx=ctx, max_length=max_length))
                return
        except subprocess.CalledProcessError:
            await ctx.send(message_invalid_youtube_link.format(ctx=ctx, command_name=command_name, show_queue=show_queue))
            return

        save_to_playlist(user_playlist_path, video_id, user_id, title)
        last_uses[user_id] = current_time
        await ctx.send(message_added_to_playlist.format(ctx=ctx, title=title))

bot = Bot()
bot.run()
