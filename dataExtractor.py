import argparse
import csv
import sqlite3
import sys
from os import listdir
from os.path import isfile, join

#SC2 related imports
import sc2reader
from sc2reader.engine.plugins import SelectionTracker, APMTracker

banned_units = ['Beacon']

games_columns = {
    'hash': 'varchar(255) NOT NULL PRIMARY KEY',
    'team_1_hash': 'varchar(255) NOT NULL default \'\'',
    'team_2_hash': 'varchar(255) NOT NULL default \'\'',
    'winner_team_hash': 'varchar(255) NOT NULL default \'\'',
    'map_name': 'int(11) NOT NULL default \'-1\'',
    'game_length': 'int(11) NOT NULL default \'0\'',
    'game_type': "varchar(20) NOT NULL default \'0\'"
}

players_columns = {
    'toon_id': 'INTEGER PRIMARY KEY NOT NULL',
    'name': 'varchar(255) NOT NULL default \'\'',
    'clan': 'varchar(10) NOT NULL default \'\'',
    'subregion': 'INTEGER NOT NULL',
    'region': 'varchar(10) NOT NULL default \'\'',
    'url': 'varchar(255) NOT NULL default \'\''
}

teams_columns = {
    'hash': 'varchar(255) NOT NULL PRIMARY KEY',
    'player_1': 'INTEGER NOT NULL',
    'player_2': 'INTEGER NOT NULL'
}

units_died_columns = {
    'unit_id': 'int(11) NOT NULL',
    'killing_unit_id': 'int(11) NOT NULL',
    'location_x': 'int(11) NOT NULL',
    'location_y': 'int(11) NOT NULL',
    'game_second': 'int(11) NOT NULL',
    'game_hash': 'varchar(255) NOT NULL'
}

units_bought_columns = {
    'game_hash': 'varchar(255) NOT NULL',
    'location_x': 'int(11) NOT NULL',
    'location_y': 'int(11) NOT NULL',
    'unit_type': 'varchar(255) NOT NULL',
    'game_second': 'int(11) NOT NULL',
    'unit_id': 'int(11) NOT NULL',
    'owner': 'INTEGER NOT NULL'
}

sql_tables = {
    "games" : games_columns,
    "players": players_columns,
    "teams": teams_columns,
    "deaths": units_died_columns,
    "purchases": units_bought_columns
}

class database:
    def __init__(self, filename):
        self.db = sqlite3.connect(filename)

        for table_name, table_columns in sql_tables.iteritems():
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS `{0}` (
                    {1}
                )
            '''.format( table_name,
                        (", ".join([col + ' ' + col_type for col, col_type in sorted(table_columns.iteritems())]))))


    def __del__(self):
        self.db.close()

    def db_row_exists(self, table_name, unique_id_name, unique_id, exists_message):
        row_sql = self.db.execute('''
                    SELECT {1} FROM {0} WHERE {0}.{1} = '{2}'
                '''.format(table_name, unique_id_name, unique_id))

        if row_sql.fetchone() is not None:
            print("    " + exists_message)
            return True

        return False

    def add_team(self, team, db_cursor):
        if(self.db_row_exists('teams', 'hash', team.hash, "Team {0} with hash {1} already in db.  Not inserting.".format(str(team), team.hash))):
            return

        if len(team.players) > 1:
            team_metadata = {
                'hash': team.hash,
                'player_1': sorted(team.players)[0].toon_id,
                'player_2': sorted(team.players)[1].toon_id
            }
        else:
            team_metadata = {
                'hash': team.hash,
                'player_1': sorted(team.players)[0].toon_id,
                'player_2': ''
            }

        db_cursor.execute('''
                INSERT INTO teams ({0})
                VALUES ({1})
            '''.format( \
              (",".join([col for col,col_type in sorted(teams_columns.iteritems())])), \
              (",".join(['\'' + str(data) + '\'' for col,data in sorted(team_metadata.iteritems())]))))

    def add_player(self, player, db_cursor):
        if self.db_row_exists('players', 'toon_id', player.toon_id, "Player {0} with toon_id {1} already in db.  Not inserting.".format(str(player), player.toon_id)):
            return

        player_metadata = {
            'toon_id': player.toon_id,
            'name': player.name,
            'clan': player.clan_tag,
            'subregion': player.subregion,
            'region': player.region,
            'url': player.url,
        }

        db_cursor.execute('''
                INSERT INTO players ({0})
                VALUES ({1})
            '''.format( \
              (",".join([col for col,col_type in sorted(players_columns.iteritems())])), \
              (",".join(['\'' + str(data) + '\'' for col,data in sorted(player_metadata.iteritems())]))))

    def add_purchase(self, player, unit_name, unit_count, game_id, db_cursor):
        purchase_metadata = {
            'game_id': game_id,
            'player': player,
            'unit': unit_name,
            'count': unit_count
        }

        db_cursor.execute('''
                INSERT INTO purchases ({0})
                VALUES ({1})
            '''.format( \
              (",".join([col for col,col_type in sorted(purchases_columns.iteritems()) if col is not 'id'])), \
              (",".join(['\'' + str(data) + '\'' for col,data in sorted(purchase_metadata.iteritems())]))))

    def add_death(self, death, game_hash, db_cursor):
        death['game_hash'] = game_hash

        db_cursor.execute('''
                INSERT INTO deaths ({0})
                VALUES ({1})
            '''.format( \
              (",".join([col for col,col_type in sorted(units_died_columns.iteritems())])), \
              (",".join(['\'' + str(data) + '\'' for col,data in sorted(death.iteritems())]))))

    def add_purchase(self, purchase, game_hash, db_cursor):
        purchase['game_hash'] = game_hash

        db_cursor.execute('''
                INSERT INTO purchases ({0})
                VALUES ({1})
            '''.format( \
              (",".join([col for col,col_type in sorted(units_bought_columns.iteritems())])), \
              (",".join(['\'' + str(data) + '\'' for col,data in sorted(purchase.iteritems())]))))

    def add_game(self, game):
        if self.db_row_exists('games', 'hash', game.game_metadata['hash'], "Game {0} already in the db.  Not inserting.".format(game.game_metadata['hash'])):
            return

        c = self.db.cursor()
        c.execute('''
                INSERT INTO games ({0})
                VALUES ({1})
            '''.format( \
              (",".join([col for col,col_type in sorted(games_columns.iteritems())])), \
              (",".join(['\'' + str(data).replace("\'", "") + '\'' for col,data in sorted(game.game_metadata.iteritems())]))))

        for player in game.game_players:
            self.add_player(player, c)

        for team in game.game_teams:
            self.add_team(team, c)

        for death in game.unit_deaths:
            self.add_death(death, game.game_metadata['hash'], c)

        for purchase in game.game_purchases:
            c = self.db.cursor()
            self.add_purchase(purchase, game.game_metadata['hash'], c)
            self.db.commit()

        self.db.commit()

class game_extract:
    def __init__(self, game_metadata, game_players, game_teams, unit_deaths, purchases):
        self.game_metadata = game_metadata
        self.game_purchases = purchases
        self.game_players = game_players
        self.game_teams = game_teams
        self.unit_deaths = unit_deaths

    #BUG:  Doesn't output correct winner for Archon, 2v2
    def export_game_to_csv(self, path):
        with open(path, 'wb') as csvfile:
            fieldnames = ['player', 'winner', 'unit', 'count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i,j in self.game_purchases.iteritems():
                for m,n in j.iteritems():
                    writer.writerow({'player': i, 'winner': str(i) in self.game_metadata['winner_team_hash'], 'unit': m, 'count': n})

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Dumps replay data to .csv')
    parser.add_argument('in_path', metavar='PATH', type=str, help='Path to a replay file (.sc2replay or directory)')
    parser.add_argument('out_path', metavar='PATH', type=str, help='Path to output .csv or .db')
    return parser.parse_args()

def extract_file(in_path, out_path):
    game = sc2reader.load_replay(in_path, load_level=4)
    deaths = []
    purchases = []
    if len(game.teams) is not 2:
        print('Abandon ship!  We aren\'t ready for more than 2 team games.  Player count == ' + game.teams.count)
        quit(1)

    game_metadata = {
        "hash": game.filehash,
        "team_1_hash": game.teams[0].hash,
        "team_2_hash": game.teams[1].hash,
        "winner_team_hash": game.winner.hash,
        "map_name": game.map_name,
        "game_length": int(game.length.total_seconds()),
        "game_type": game.type
    }

    for evt in game.events:
        # Unit purchases
        if type(evt) is sc2reader.events.tracker.UnitBornEvent:
            if  not hasattr(evt, 'unit_controller') or \
                evt.unit_controller is None or \
                len([unit_short_name for unit_short_name in banned_units if unit_short_name in str(evt.unit)]) is 1:
                    continue

            purchase_metadata = {
                'location_x': evt.location[0],
                'location_y': evt.location[1],
                'unit_type': evt.unit_type_name,
                'game_second': evt.second,
                'owner': evt.unit_controller.toon_id,
                'unit_id': evt.unit_id
            }

            purchases.append(purchase_metadata)

        if type(evt) is sc2reader.events.tracker.UnitDiedEvent:
            # This is the death of a unit due to someone leaving the game, I think?  Either way, it means
            # the unit didn't have a killing unit, so omit it from our tracking data.
            if evt.killing_unit_id is None:
                continue

            death_metadata = {
                'unit_id': evt.unit_id,
                'killing_unit_id': evt.killing_unit_id,
                'location_x': evt.location[0],
                'location_y': evt.location[1],
                'game_second': evt.second
            }

            deaths.append(death_metadata)


    all_game = game_extract(game_metadata, game.players, game.teams, deaths, purchases)

    if '.csv' in out_path:
        all_game.export_game_to_csv(out_path)
    elif '.db' in out_path:
        db = database(out_path)
        db.add_game(all_game)
    else:
        print('Abandon ship!  We don\'t support your ouput format.  Please use .csv or .db')
        quit(1)

def main():
    args = parse_args()
    if(".sc2replay" in args.in_path.lower()):
        extract_file(args.in_path, args.out_path)
    else:
        replays = [f for f in listdir(args.in_path) if isfile(join(args.in_path, f)) and ".sc2replay" in f.lower()]
        for replay in replays:
            print("Attempting to load replay: " + join(args.in_path, replay))
            try:
                    extract_file(join(args.in_path, replay), args.out_path)
            except:
                    print("     Failed to load due to {0} -- Continuing...".format(sys.exc_info()[0]))


if __name__ == '__main__':
    main()
