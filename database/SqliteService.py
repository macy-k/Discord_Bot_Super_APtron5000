import sqlite3
from datetime import datetime, timezone
from sqlite3 import Cursor
from typing import Any, List

from database.Save import Save
from database.User import User

DATABASE_FILE = "database/database.db"

def adapt_datetime_epoch(dt: datetime) -> float:
    if dt.tzinfo is None or dt.tzinfo != timezone.utc:
        raise ValueError("Datetime must be timezone-aware UTC.")
    return dt.timestamp()

def convert_epoch_datetime(val: bytes) -> datetime:
    epoch_val = float(val)
    return datetime.fromtimestamp(epoch_val, tz=timezone.utc)

sqlite3.register_adapter(datetime, adapt_datetime_epoch)
sqlite3.register_converter("TIMESTAMP", convert_epoch_datetime)

class SqliteService:
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute('PRAGMA foreign_keys = ON')
        self.connection.commit()


    def increment_user(self, user_id: int):
        save = self.find_user_active_save(user_id)
        sql_increment_save_count = "UPDATE saves SET count = ? WHERE id = ?"
        cursor = self.__execute_sql(sql_increment_save_count, (save.count + 1, save.id,))
        if cursor.rowcount == 0:
            raise LookupError("User increment failed for id {}".format(user_id))


    def decrement_user(self, user_id: int):
        save = self.find_user_active_save(user_id)
        sql_increment_save_count = "UPDATE saves SET count = ? WHERE id = ?"
        cursor = self.__execute_sql(sql_increment_save_count, (save.count - 1, save.id,))
        if cursor.rowcount == 0:
            raise LookupError("User decrement failed for id {}".format(user_id))


    def reset_user(self, user_id: int):
        save = self.find_user_active_save(user_id)
        sql_increment_save_count = "UPDATE saves SET count = ? WHERE id = ?"
        cursor = self.__execute_sql(sql_increment_save_count, (0, save.id,))
        if cursor.rowcount == 0:
            raise LookupError("User reset failed for id {}".format(user_id))


    def count_user(self, user_id: int) -> int:
        save = self.find_user_active_save(user_id)
        return save.count


    def new_save(self, user_id: int, new_name: str):
        sql_insert_new_save = "INSERT INTO saves (userId, name, creationDate) VALUES (?, ?, ?)"
        cursor = self.__execute_sql(sql_insert_new_save, (user_id, new_name, datetime.now(timezone.utc),))
        if cursor.rowcount == 0:
            raise LookupError("New save creation failed for user id {}".format(user_id))

        save_id = cursor.lastrowid
        if save_id is None:
            raise LookupError(
                "New save creation for user id {} failed to register 'cursor.lastrowid'".format(user_id))
        self.change_user_active_save(user_id, save_id)


    def delete_save(self, save_id: int):
        sql_delete_save = "DELETE FROM saves WHERE id = ?"
        cursor = self.__execute_sql(sql_delete_save, (save_id,))
        if cursor.rowcount == 0:
            raise LookupError("Save deletion failed for save id {}".format(save_id))


    def rename_save(self, save_id: int, new_name: str):
        sql_update_save_name = "UPDATE saves SET name = ? WHERE id = ?"
        cursor = self.__execute_sql(sql_update_save_name, (new_name, save_id,))
        if cursor.rowcount == 0:
            raise LookupError(
                "Failed to update name for save {}".format(save_id))


    def change_user_active_save(self, user_id: int, save_id: int):
        sql_update_user_save = "UPDATE users SET activeSave = ? WHERE id = ?"
        cursor = self.__execute_sql(sql_update_user_save, (save_id, user_id,))
        if cursor.rowcount == 0:
            raise LookupError(
                "Failed to update user's default save to {} for user id {}".format(save_id, user_id))


    def find_user_active_save(self, user_id: int) ->  Save:
        user = self.__find_user(user_id)
        if user.active_save is None:
            raise LookupError("User {} with null active save found".format(user_id))

        return self.find_save(user.active_save)


    def find_user_saves(self, user_id: int) -> List[Save]:
        return self.__find_saves(user_id)


    def find_save(self, save_id: int) -> Save:
        save_raw = self.__find_save_raw(save_id)
        if save_raw is None:
            raise LookupError("Save {} not found", save_id)
        return Save.from_row(save_raw)


    def __find_user(self, user_id: int) ->  User:
        user_raw = self.__find_user_raw(user_id)
        return User.from_row(user_raw)


    def __find_saves(self, user_id: int) -> list[Save]:
        saves_raw = self.__find_saves_raw(user_id)
        if saves_raw is None:
            raise LookupError("No saves found for user {}", user_id)
        return [Save.from_row(save_raw) for save_raw in saves_raw]


    def __find_user_raw(self, user_id: int) -> Any:
        sql_find_user = "SELECT * FROM users WHERE id = ?"
        cursor = self.__execute_sql(sql_find_user, (user_id,))
        return cursor.fetchone()


    def __find_save_raw(self, save_id: int) -> Any:
        sql_find_save = "SELECT * FROM saves WHERE id = ?"
        cursor = self.__execute_sql(sql_find_save, (save_id,))
        return cursor.fetchone()


    def __find_saves_raw(self, user_id: int) -> list[Any]:
        sql_find_saves = "SELECT * FROM saves WHERE userId = ?"
        cursor = self.__execute_sql(sql_find_saves, (user_id,))
        return cursor.fetchall()


    def verify_user(self, user_id: int) -> bool:
        user_raw = self.__find_user_raw(user_id)
        if user_raw is None:
            return False
        return True


    def verify_user_save(self, user_id: int) -> bool:
        user = self.__find_user(user_id)
        if user.active_save is None:
            return False
        return True


    def verify_tables(self):
        sql_saves = """
        CREATE TABLE IF NOT EXISTS saves (
            id INTEGER PRIMARY KEY,
            userId INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT 'Default Save',
            count INTEGER NOT NULL DEFAULT 0,
            creationDate TIMESTAMP NOT NULL,
            CONSTRAINT user_fk FOREIGN KEY (userId) REFERENCES users (id) ON DELETE CASCADE 
        );
        """
        sql_users = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activeSave INTEGER,
            CONSTRAINT active_save_fk FOREIGN KEY (activeSave) REFERENCES saves (id) ON DELETE SET NULL
        );
        """
        self.__execute_sql(sql_saves)
        self.__execute_sql(sql_users)


    def setup_user(self, user_id: int):
        sql_create_user = "INSERT INTO users (id) VALUES (?)"
        cursor = self.__execute_sql(sql_create_user, (user_id,))
        if cursor.rowcount == 0:
            raise LookupError("User creation failed for id {}".format(user_id))


    def setup_default_user_save(self, user_id: int):
        sql_create_save = "INSERT INTO saves (userId, creationDate) VALUES (?, ?)"
        cursor = self.__execute_sql(sql_create_save, (user_id, datetime.now(timezone.utc),))
        if cursor.rowcount == 0:
            raise LookupError("Default save creation failed for user id {}".format(user_id))

        save_id = cursor.lastrowid
        if save_id is None:
            raise LookupError("Default save creation for user id {} failed to register 'cursor.lastrowid'".format(user_id))
        self.change_user_active_save(user_id, save_id)


    def close_connection(self):
        self.connection.close()


    def __execute_sql(self, sql: str, params: tuple = ()) -> Cursor:
        cursor = self.connection.cursor()
        cursor = cursor.execute(sql, params)
        self.connection.commit()
        return cursor
