import os
import json
import subprocess
from twitchio.ext import commands

command_name = "comandi"
commands_dir = "./commands_dir/"
message_usr_cmd = "{ctx.author.name}, i comandi disponibili sono: "
message_mod_cmd = "{ctx.author.name}, i comandi per mod sono: "

config_bot = "--- configurazione bot ---"
config_token = "scrivi il tuo token Twitch:"
config_initial_channels = "scrivi il nome del canale a cui collegare il bot:"

if not os.path.exists("config.json"):
    print(config_bot)
    token = input(config_token + " ")
    initial_channel = input(config_initial_channels + " ")

    config_data = {
        "token": token,
        "prefix": ["!"],
        "initial_channels": [initial_channel]
    }

    with open("config.json", "w") as file:
        json.dump(config_data, file)

with open("config.json", "r") as file:
    data = json.load(file)

if not os.path.exists("enabled_users.json"):
    enabled_users = data["initial_channels"]
    with open("enabled_users.json", "w") as file:
        json.dump(enabled_users, file)

with open("enabled_users.json", "r") as file:
    enabled_users = json.load(file)

def run_script(script_path):
    process = subprocess.Popen(["python3", script_path])

scripts = [os.path.join(commands_dir, f) for f in os.listdir(commands_dir) if f.endswith(".py")]
for script in scripts:
    run_script(script)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=data["token"],
            prefix=data["prefix"],
            initial_channels=data["initial_channels"],
        )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is   | {self.user_id}")
        print(f"Prefix is    | {data['prefix']}")
        print(f"Channels is  | {data['initial_channels']}")

    @commands.command(name=command_name)
    async def handle_command(self, ctx: commands.Context):
        mod_commands = []
        usr_commands = []

        for filename in os.listdir(commands_dir):
            if filename.endswith(".py"):
                with open(os.path.join(commands_dir, filename), "r") as file:
                    file_content = file.read()
                    enable_access_control = False
                    command_name = None
                    description = None

                    for line in file_content.splitlines():
                        if line.startswith("command_name"):
                            command_name = line.split("=")[1].strip()[1:-1]
                        elif line.startswith("description"):
                            description = line.split("=")[1].strip()[1:-1]
                        elif line.startswith("enable_access_control"):
                            enable_access_control = eval(line.split("=")[1].strip())

                    if enable_access_control and ctx.author.name in enabled_users:
                        command_message = f"!{command_name} ({description})"
                        mod_commands.append(command_message)
                    elif not enable_access_control:
                        command_message = f"!{command_name} ({description})"
                        usr_commands.append(command_message)

        full_message_usr_cmd = message_usr_cmd + ", ".join(usr_commands)
        await ctx.send(full_message_usr_cmd.format(ctx=ctx))

        if ctx.author.name in enabled_users:
            full_message_mod_cmd = message_mod_cmd + ", ".join(mod_commands)
            await ctx.send(full_message_mod_cmd.format(ctx=ctx))

bot = Bot()
bot.run()
