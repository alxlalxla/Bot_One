import json
from twitchio.ext import commands
import os
import time
import math

command_name = "lurk"
description = "attiva il lurk mode"

enable_access_control = False
access_denied_message = "{ctx.author.name} non sei autorizzato ad eseguire questo comando!"

cooldown = 60 * 10
message_wait = "{ctx.author.name} hai già lurkato duro! Aspetta almeno {remaining_time:.0f} minuti prima di usare di nuovo il comando \"!{command_name}\". Il tuo saldo è di {lurkcoins} lurkcoins."
message = "{ctx.author.name} grazie per il lurk, hai guadagnato un lurkcoin! Il tuo saldo attuale è di {lurkcoins} lurkcoins, usali responsabilmente!"

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
            initial_channels=data["initial_channels"],
        )

    async def event_ready(self):
        print(f"Command \"{command_name}\" loaded")

    @commands.command(name=command_name)
    async def handle_lurk(self, ctx: commands.Context):
        user_lowercase = ctx.author.name.lower()
        if enable_access_control and user_lowercase not in enabled_users:
            await ctx.send(access_denied_message.format(ctx=ctx))
            return

        current_time = time.time()
        user_id = ctx.author.id

        lurkcoins_path = f"usr/{user_lowercase}/lurkcoins.json"
        os.makedirs(os.path.dirname(lurkcoins_path), exist_ok=True)

        if os.path.exists(lurkcoins_path):
            with open(lurkcoins_path, "r") as f:
                lurkcoins = json.load(f)["lurkcoins"]
        else:
            with open(lurkcoins_path, "w") as f:
                json.dump({"lurkcoins": 0}, f)
            lurkcoins = 0

        if user_id in last_uses and current_time - last_uses[user_id] < cooldown:
            remaining_time = math.ceil((cooldown - (current_time - last_uses[user_id])) / 60)
            await ctx.send(message_wait.format(ctx=ctx, command_name=command_name, remaining_time=remaining_time, lurkcoins=lurkcoins))
            return

        last_uses[user_id] = current_time

        lurkcoins += 1
        with open(lurkcoins_path, "w") as f:
            json.dump({"lurkcoins": lurkcoins}, f)

        await ctx.send(message.format(ctx=ctx, lurkcoins=lurkcoins))

bot = Bot()
bot.run()
