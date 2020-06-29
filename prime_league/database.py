import os

import mysql.connector


class DatabaseConnector:
    class __DatabaseConnector:
        def __init__(self):
            print(os.getenv("DB_HOST"))
            print(os.getenv("DB_PASSWORD"))
            print(os.getenv("DB_PORT"))
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                db=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                passwd=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT"),
            )

    instance = None

    def __init__(self):
        if not DatabaseConnector.instance:
            DatabaseConnector.instance = DatabaseConnector.__DatabaseConnector()
        else:
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                db=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                passwd=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT"),
            )

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def insert_to_db(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        cursor.close()
        self.connection.commit()

    def close_connection(self):
        self.connection.close()

    def get_games_from_db(self, team_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM prime_league WHERE team_id={}".format(team_id))
        return cursor.fetchall()

    def get_uncompleted_games_from_db(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM prime_league WHERE game_closed=FALSE")
        return cursor.fetchall()

    def get_current_team_ids(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT(team_id) FROM prime_league")
        return cursor.fetchall()

    def get_next_uncompleted_game(self, team_id):
        cursor = self.connection.cursor()
        query = "SELECT * FROM prime_league WHERE game_closed=FALSE AND team_id={} ORDER BY game_day ASC LIMIT 1".format(
            team_id)
        cursor.execute(query)
        records = cursor.fetchall()
        return records[0] if len(records) == 1 else None

    def get_game_from_db(self, _id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM prime_league WHERE id={}".format(_id))
        game = cursor.fetchall()
        return game[0] if len(game) > 0 else None

    def truncate_games(self):
        cursor = self.connection.cursor()
        cursor.execute("TRUNCATE TABLE prime_league")

    def delete_game(self, _id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM prime_league where id={}".format(_id))
        cursor.close()
        self.connection.commit()
