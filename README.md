# StarcraftDataExtractor #
Copyright July 2016, Justin Dallal

The StarcraftDataExtractor is a utility to create a database of events from Starcraft 2 replays.  Support should be in place for WOL, HOTS, and LOTV replays.  Data will be inserted into a sqllite database (.db) file for each unit purchase, each unit death, location, and team, player, and game metadata like map, game length, player location, clan.  The database schema is designed in such a way to maximize the ability to extract out trends using BI utilities like Tableau.

## REQUIREMENTS
1.  python 2.7.x
2.  sc2reader (latest) (pip install sc2reader)
3.  sqlite3 python module (should come by default)

## USAGE
dataExtractor.py [filename.sc2replay|directory_of_sc2replay_files] [filename.csv|database.db]

  .sc2replay or directory required
  
  .csv for diagnostic or single replay metaanalysis, .db for most cases
  
  * Example 1 - output a single replay to a csv file (aggregated over all unit purchases): dataExtractor.py replay.sc2replay output.csv
  * Example 2 - output a single replay to a sqllite db: dataExtractor.py replay.sc2replay output.db
  * Example 3 - output a whole directory to a sqllite db: dataExtractor.py replay_dirs all_replays.db

## DATABASE SCHEMA
### GAMES TABLE
game_length - int - Length of game in seconds

game_type - string - Type of game in terms of 1v1, 2v2, or archon mode

hash - PRIMARY KEY - string - Unique hash of the game from the replay file, used to identify duplicate games

map_name - string - Name of the map on which the game was played

team_1_hash - string - Hash of the first team playing.  Keyed to *teams* table primary key.

team_2_hash - string - Hash of the second team playing.  Keyed to *teams* table primary key.

winner_team_hash - string - Hash of the winning team.  Will be a duplicate of one of the previous 2   
