import json
from twitchio.ext import commands

command_name = "so"
description = "shoutout"

enable_access_control = True
access_denied_message = "{ctx.author.name} non sei autorizzato ad eseguire questo comando!"

message = "Corri a mettere un follow a twitch.tv/{so_channel}"
so_command = "/shoutout {so_channel}"

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
    async def handle_command(self, ctx: commands.Context, so_channel: str):
        if so_channel.startswith("@"):
            so_channel = so_channel[1:]

        # Controllo dell'accesso solo se enable_access_control è True
        if enable_access_control and ctx.author.name.lower() not in enabled_users:
            await ctx.send(access_denied_message.format(ctx=ctx))
            return  # Esci dalla funzione se l'accesso è negato

        await ctx.send(message.format(so_channel=so_channel))
        await ctx.send(so_command.format(so_channel=so_channel))

bot = Bot()
bot.run()
