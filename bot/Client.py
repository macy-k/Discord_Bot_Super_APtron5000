import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.PersistanceService import PersistenceService

class Client(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.persistence_service = PersistenceService()

        load_dotenv()
        dev_mode = os.getenv("DEV_MODE")
        if dev_mode is not None and dev_mode == "TRUE":
            dev_guild_id = os.getenv("DEV_GUILD_ID")
            if dev_guild_id is None:
                print("DEV_GUILD_ID not set. Cannot enter Dev mode")
                self.dev_guild_object = None
                self.dev_mode = False
                return

            self.dev_guild_object = discord.Object(dev_guild_id)
            self.dev_mode = True
        else:
            self.dev_guild_object = None
            self.dev_mode = False


    async def setup_hook(self):
        extensions = ["bot.ApCommands", "bot.SaveCommands"]
        for extension in extensions:
            try:
                await self.load_extension(extension)
                print(f"Successfully loaded extension: {extension}")
            except Exception as e:
                print(f"Failed to load extension {extension}: {e}")


    async def on_ready(self):
        print(f'Logged in as {self.user}')

        # sync dev guild
        if self.dev_mode:
            try:
                synced = await self.tree.sync(guild=self.dev_guild_object)
                print(f'Synced {len(synced)} cogs to guild {self.dev_guild_object.id}')
            except Exception as e:
                print(f'Failed to sync cogs to guild {self.dev_guild_object.id}: {e}')


    async def close(self):
        self.persistence_service.close()
        await super().close()