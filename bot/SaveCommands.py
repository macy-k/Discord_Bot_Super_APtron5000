import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt

from bot.PersistanceService import PersistenceService
from bot.SaveSelects import ChangeSavesSelect, RenameSavesSelect, DeleteSavesSelect
from database.Save import Save

SAVE_NAME_LENGTH_LIMIT = 50

class SaveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistence_service: PersistenceService = bot.persistence_service

    async def cog_load(self):
        guild_target = None
        if self.bot.dev_mode:
            guild_target = self.bot.dev_guild_object

        save_group = app_commands.Group(name="save", description="Manage your AP count saves")

        @save_group.command(name="current", description="View your current selected AP save")
        async def current(interaction: discord.Interaction):
            try:
                save: Save = self.persistence_service.current_save(interaction.user)

                msg = f"""{interaction.user.mention} Current save:
                **Name**: {save.name}
                **Creation Date:** {format_dt(save.creation_date, style='f')}
                **Count:** {save.count}
                """

                await interaction.response.send_message(msg, ephemeral=True)
            except Exception as e:
                print(f"Error for user id {interaction.user.id}: {e}")
                await interaction.response.send_message("Error occurred during command", ephemeral=True)

        @save_group.command(name="rename", description="Rename any of your AP saves")
        async def rename(interaction: discord.Interaction, new_name: str):
            try:
                if len(new_name) > SAVE_NAME_LENGTH_LIMIT:
                    await interaction.response.send_message(f"{interaction.user.mention} Save names must be <= 50 characters. Sorry! :(", ephemeral=True)
                    return

                saves = self.persistence_service.all_saves(interaction.user)
                view = discord.ui.View(timeout=180)
                view.add_item(RenameSavesSelect(saves=saves, persistence_svc=self.persistence_service, new_name=new_name))

                await interaction.response.send_message(f"{interaction.user.mention} Choose save to rename as {new_name}", view=view, ephemeral=True)
            except Exception as e:
                print(f"Error for user id {interaction.user.id}: {e}")
                await interaction.response.send_message("Error occurred during command", ephemeral=True)

        @save_group.command(name="select", description="Select a different AP save")
        async def select(interaction: discord.Interaction):
            try:
                saves = self.persistence_service.all_saves(interaction.user)
                view = discord.ui.View(timeout=180)
                view.add_item(ChangeSavesSelect(saves=saves, persistence_svc=self.persistence_service))

                await interaction.response.send_message(f"{interaction.user.mention} Select save", view=view, ephemeral=True)
            except Exception as e:
                print(f"Error for user id {interaction.user.id}: {e}")
                await interaction.response.send_message("Error occurred during command", ephemeral=True)

        @save_group.command(name="new", description="Create and select a new AP save")
        async def new(interaction: discord.Interaction, name: str):
            try:
                if len(name) > SAVE_NAME_LENGTH_LIMIT:
                    await interaction.response.send_message(f"{interaction.user.mention} Save names must be <= 50 characters. Sorry! :(", ephemeral=True)
                    return

                self.persistence_service.new_save(interaction.user, name)
                await interaction.response.send_message(f"{interaction.user.mention} Added and selected new save {name}!", ephemeral=True)
            except Exception as e:
                print(f"Error for user id {interaction.user.id}: {e}")
                await interaction.response.send_message("Error occurred during command", ephemeral=True)

        @save_group.command(name="delete", description="Delete an AP save")
        async def delete(interaction: discord.Interaction):
            try:
                saves = self.persistence_service.all_saves(interaction.user)
                view = discord.ui.View(timeout=180)
                view.add_item(DeleteSavesSelect(saves=saves, persistence_svc=self.persistence_service))

                await interaction.response.send_message(f"{interaction.user.mention} Select save to delete", view=view, ephemeral=True)
            except Exception as e:
                print(f"Error for user id {interaction.user.id}: {e}")
                await interaction.response.send_message("Error occurred during command", ephemeral=True)

        self.bot.tree.add_command(save_group, guild=guild_target)

async def setup(bot):
    await bot.add_cog(SaveCog(bot))