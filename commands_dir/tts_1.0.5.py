import subprocess
from twitchio.ext import commands
import json

# This script requires:
# espeak
# To install it on Debian/Ubuntu, run:
# apt install espeak-ng espeak-ng-data

command_name = "tts"
description = "text to speech"
espeak_parameters = "-v it -s 100 -p 0 -a 200"

# espeak_parameters:
# -a <integer> Amplitude, 0 to 200, default is 100
# -g <integer> Word gap. Pause between words, units of 10mS at the default speed
# -k <integer> Indicate capital letters with: 1=sound, 2=the word "capitals",higher values indicate a pitch increase (try -k20).
# -l <integer> Line length. If not zero (which is the default), consider lines less than this length as end-of-clause
# -p <integer> Pitch adjustment, 0 to 99, default is 50
# -s <integer> Speed in approximate words per minute. The default is 175
# -v <voice name> Use voice file of this name from espeak-data/voices

with open("config.json", "r") as file:
    data = json.load(file)

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
    async def tts(self, ctx: commands.Context):
        text = ctx.message.content[len(data["prefix"]) + len(command_name):]
        text = text.replace(" ", "_")
        text = text.replace("&", "_")
        text = text.replace(">", "_")
        text = text.replace("<", "_")
        text = text.replace("|", "_")
        espeak_command = f"espeak-ng {espeak_parameters} {text}"
        try:
            subprocess.run(espeak_command.split(), check=True)

        except subprocess.CalledProcessError as e:
            await ctx.send(f"espeak error: {e}")

bot = Bot()
bot.run()
