import discord
from discord import app_commands
from discord.ext import commands

from bot.PersistanceService import PersistenceService


class APCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistence_service: PersistenceService = bot.persistence_service

    async def cog_load(self):
        guild_target = None
        if self.bot.dev_mode:
            guild_target = self.bot.dev_guild_object

        @app_commands.command(name="ap", description="Increment your AP count!")
        async def increment(interaction: discord.Interaction):
            try:
                ap_count = self.persistence_service.increment_user(interaction.user)
                await interaction.response.send_message(f"{interaction.user.mention} has {ap_count} APs!!")
            except Exception as e:
                print(f"Error for user id {interaction.user.id}: {e}")
                await interaction.response.send_message("Error occurred during command", ephemeral=True)

        ap_group = app_commands.Group(name="count", description="Manage your AP count")

        @ap_group.command(name="view", description="View your current AP count")
        async def count(interaction: discord.Interaction):
            try:
                ap_count = self.persistence_service.count_user(interaction.user)
                await interaction.response.send_message(f"{interaction.user.mention} has {ap_count} APs!!")
            except Exception as e:
                print(f"Error for user id {interaction.user.id}: {e}")
                await interaction.response.send_message("Error occurred during command", ephemeral=True)

        @ap_group.command(name="decrement", description="Decrement your AP count :(")
        async def decrement(interaction: discord.Interaction):
            try:
                ap_count = self.persistence_service.decrement_user(interaction.user)
                await interaction.response.send_message(f"{interaction.user.mention} {ap_count} APs :(")
            except Exception as e:
                print(f"Error for user id {interaction.user.id}: {e}")
                await interaction.response.send_message("Error occurred during command", ephemeral=True)

        @ap_group.command(name="reset", description="Reset your AP count to 0")
        async def reset(interaction: discord.Interaction):
            try:
                ap_count = self.persistence_service.reset_user(interaction.user)
                await interaction.response.send_message(f"{interaction.user.mention} now has a whopping {ap_count} APs :)")
            except Exception as e:
                print(f"Error for user id {interaction.user.id}: {e}")
                await interaction.response.send_message("Error occurred during command", ephemeral=True)

        self.bot.tree.add_command(ap_group, guild=guild_target)
        self.bot.tree.add_command(increment, guild=guild_target)

async def setup(bot):
    await bot.add_cog(APCog(bot))