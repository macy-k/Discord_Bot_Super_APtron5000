import discord

from bot.PersistanceService import PersistenceService
from database.Save import Save

class __SavesSelect(discord.ui.Select):
    def __init__(self, persistence_svc: PersistenceService, saves: list[Save]):
        self.persistence_svc = persistence_svc

        options = []
        for save in saves:
            date_str = save.creation_date.strftime("%b %d, %Y")
            options.append(discord.SelectOption(label=save.name, value=str(save.id), description=f"Created {date_str} (UTC) "
                                                                             f"Count: {save.count}"),)
        super().__init__(placeholder="Select a save", max_values=1, min_values=1, options=options)


class ChangeSavesSelect(__SavesSelect):
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        self.placeholder = "Save selected"
        try:
            save = self.persistence_svc.change_save(interaction.user, int(self.values[0]))
            await interaction.response.edit_message(content=f"{interaction.user.mention} Save changed to {save.name}", view=self.view)
        except Exception as e:
            print(f"Error for user id {interaction.user.id}: {e}")
            await interaction.response.send_message("Error occurred during command", ephemeral=True)


class RenameSavesSelect(__SavesSelect):
    def __init__(self, persistence_svc: PersistenceService, saves: list[Save], new_name: str):
        self.new_name = new_name
        super().__init__(persistence_svc, saves)

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        self.placeholder = "Save selected"
        try:
            save = self.persistence_svc.rename_save(interaction.user, int(self.values[0]), self.new_name)
            await interaction.response.edit_message(content=f"{interaction.user.mention} Renamed save {save.name} to {self.new_name}", view=self.view)
        except Exception as e:
            print(f"Error for user id {interaction.user.id}: {e}")
            await interaction.response.send_message("Error occurred during command", ephemeral=True)


class DeleteSavesSelect(__SavesSelect):
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        self.placeholder = "Save selected"
        try:
            current_save = self.persistence_svc.current_save(interaction.user)
            save = self.persistence_svc.delete_save(interaction.user, int(self.values[0]))

            if current_save.id != save.id:
                await interaction.response.edit_message(content=f"{interaction.user.mention} Deleted save {save.name} :(", view=self.view)
            else:
                await interaction.response.edit_message(content=f"{interaction.user.mention} Deleted save {save.name} :( "
                                                                f"\n**WARNING:** deleted currently selected save. A Default Save has been created and selected",
                                                        view=self.view)
        except Exception as e:
            print(f"Error for user id {interaction.user.id}: {e}")
            await interaction.response.send_message("Error occurred during command", ephemeral=True)