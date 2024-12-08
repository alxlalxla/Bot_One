from twitchio.ext import commands
import json
import subprocess
import time
import threading
import os

command_name = "pl"
description = "gestisci la playlist"
enable_access_control = True
access_denied_message = "{ctx.author.name} non sei autorizzato ad eseguire questo comando!"
playlist_start = "playlist avviata!"
playlist_stop = "playlist arrestata!"
playlist_already_started = "la playlist è già in esecuzione"
playlist_empty = "playlist vuota"
start = "start"
stop = "stop"
playback_error = "Errore durante la riproduzione di {title}"
playlist_dir = "./media/playlist/"
playlist_mod_file = f"{playlist_dir}playlist.json"
playlist_usr_file = f"{playlist_dir}user_playlist.json"

os.makedirs(playlist_dir, exist_ok=True)

if not os.path.exists(playlist_mod_file):
    with open(playlist_mod_file, 'w') as f:
        json.dump([], f)

if not os.path.exists(playlist_usr_file):
    with open(playlist_usr_file, 'w') as f:
        json.dump([], f)

with open("config.json", "r") as file:
    data = json.load(file)

with open("enabled_users.json", "r") as file:
    enabled_users = json.load(file)

playlist_running = False

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
    async def handle_command(self, ctx: commands.Context):
        global playlist_running

        if enable_access_control and ctx.author.name.lower() not in enabled_users:
            await ctx.send(access_denied_message.format(ctx=ctx))
            return

        if ctx.message.content.startswith(f'!{command_name} {start}'):
            with open(playlist_mod_file, 'r') as f:
                playlist_mod = json.load(f)
            if not playlist_mod:
                await ctx.send(playlist_empty)
                return
            if playlist_running:
                await ctx.send(playlist_already_started)
            else:
                playlist_running = True
                await ctx.send(playlist_start)
                threading.Thread(target=self.play_playlist, args=(ctx,)).start()
        elif ctx.message.content.startswith(f'!{command_name} {stop}'):
            playlist_running = False
            process = subprocess.Popen(["pkill", "mpv"])
            await ctx.send(playlist_stop)

    def play_playlist(self, ctx):
        global playlist_running

        with open(playlist_mod_file, 'r') as f:
            playlist_mod = json.load(f)

        while playlist_running:
            for item in playlist_mod:
                if not playlist_running:
                    break

                while True:
                    with open(playlist_usr_file, 'r') as f:
                        playlist_user = json.load(f)

                    if not playlist_user:
                        break

                    for user_item in playlist_user:
                        if not playlist_running:
                            break

                        user_video_id = user_item['video_id']
                        user_title = user_item['title']
                        user_command = f"mpv --no-video --cache=yes https://youtu.be/{user_video_id}"
                        user_process = subprocess.Popen(user_command, shell=True, stdin=subprocess.PIPE)

                        user_process.wait()

                        if user_process.returncode != 0:
                            self.loop.create_task(ctx.send(playback_error.format(title=user_title)))

                        with open(playlist_usr_file, 'r') as f:
                            playlist_user = json.load(f)

                        playlist_user.remove(user_item)

                        with open(playlist_usr_file, 'w') as f:
                            json.dump(playlist_user, f)

                if not playlist_running:
                    break

                video_id = item['video_id']
                title = item['title']
                command = f"mpv --no-video --cache=yes https://youtu.be/{video_id}"
                process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE)

                process.wait()

                if process.returncode != 0:
                    self.loop.create_task(ctx.send(playback_error.format(title=title)))

            if not playlist_running:
                self.current_title = None
                self.current_user = None

bot = Bot()
bot.run()
