from twitchio.ext import commands
import json
import subprocess
import os

command_name = "kill"
description = "termina un'applicazione"
enable_access_control = True
access_denied_message = "{ctx.author.name} non sei autorizzato ad eseguire questo comando!"
app_denied_message = "{ctx.author.name} operazione non consentita."
# Messaggio che elenca le applicazioni killabili
killable_apps_message = "{ctx.author.name}, le app killabili sono: {apps}."
# Messaggio di successo per la terminazione dell'applicazione
app_terminated_message = "{app} è stato terminato."
# Lista di applicazioni che possono essere terminate
killable_apps = ["mpv", "espeak-ng"]

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
        print(f'Command "{command_name}" loaded')

    @commands.command(name=command_name)
    async def kill_command(self, ctx, app: str = None):
        if enable_access_control and ctx.author.name.lower() not in enabled_users:
            await ctx.send(access_denied_message.format(ctx=ctx))
            return

        # Se l'app è None, invia il messaggio con le app killabili
        if app is None:
            await ctx.send(killable_apps_message.format(ctx=ctx, apps=', '.join(killable_apps)))
            return

        # Controlla se l'app è nella lista delle app killabili
        if app.lower() not in killable_apps:
            await ctx.send(app_denied_message.format(ctx=ctx))
            return

        # Esegui il comando pkill per terminare l'applicazione
        subprocess.run(["pkill", app.lower()])
        await ctx.send(app_terminated_message.format(app=app))

bot = Bot()
bot.run()