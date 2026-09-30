import discord

from database.Save import Save
from database.SqliteService import SqliteService

class PersistenceService:
    def __init__(self):
        self.sqlite_service = SqliteService()


    def increment_user(self, user: discord.User | discord.Member) -> int:
        self.__verify_setup(user.id)

        self.sqlite_service.increment_user(user.id)
        return self.sqlite_service.count_user(user.id)


    def decrement_user(self, user: discord.User | discord.Member) -> int:
        self.__verify_setup(user.id)

        self.sqlite_service.decrement_user(user.id)
        return self.sqlite_service.count_user(user.id)


    def reset_user(self, user: discord.User | discord.Member) -> int:
        self.__verify_setup(user.id)

        self.sqlite_service.reset_user(user.id)
        return self.sqlite_service.count_user(user.id)


    def count_user(self, user: discord.User | discord.Member) -> int:
        self.__verify_setup(user.id)

        return self.sqlite_service.count_user(user.id)


    def current_save(self, user: discord.User | discord.Member) -> Save:
        self.__verify_setup(user.id)

        return self.sqlite_service.find_user_active_save(user.id)


    def all_saves(self, user: discord.User | discord.Member) -> list[Save]:
        self.__verify_setup(user.id)

        return self.sqlite_service.find_user_saves(user.id)


    def new_save(self, user: discord.User | discord.Member, new_name: str):
        self.__verify_setup(user.id)

        self.sqlite_service.new_save(user.id, new_name)

    def delete_save(self, user: discord.User | discord.Member, save_id: int) -> Save:
        self.__verify_setup(user.id)

        accessed_save: Save = self.sqlite_service.find_save(save_id)
        if accessed_save.user_id != user.id:
            raise PermissionError(f"Save being accessed doesn't have matching userId. Save userId: {accessed_save.user_id}, user id: {user.id}")

        self.sqlite_service.delete_save(save_id)
        return accessed_save

    def change_save(self, user: discord.User | discord.Member, save_id: int) -> Save:
        self.__verify_setup(user.id)

        accessed_save: Save = self.sqlite_service.find_save(save_id)
        if accessed_save.user_id != user.id:
            raise PermissionError(f"Save being accessed doesn't have matching userId. Save userId: {accessed_save.user_id}, user id: {user.id}")

        self.sqlite_service.change_user_active_save(user.id, save_id)
        return accessed_save


    def rename_save(self, user: discord.User | discord.Member, save_id: int, new_name: str) -> Save:
        self.__verify_setup(user.id)

        accessed_save: Save = self.sqlite_service.find_save(save_id)
        if accessed_save.user_id != user.id:
            raise PermissionError(f"Save being accessed doesn't have matching userId. Save userId: {accessed_save.user_id}, user id: {user.id}")

        self.sqlite_service.rename_save(save_id, new_name)
        return accessed_save



    def close(self):
        self.sqlite_service.close_connection()


    def __verify_setup(self, user_id: int):
        self.sqlite_service.verify_tables()
        verified_user = self.sqlite_service.verify_user(user_id)
        if not verified_user:
            self.sqlite_service.setup_user(user_id)
        verified_user_save = self.sqlite_service.verify_user_save(user_id)
        if not verified_user_save:
            self.sqlite_service.setup_default_user_save(user_id)