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
* game_length - int - Length of game in seconds
* game_type - string - Type of game in terms of 1v1, 2v2, or archon mode
* hash - PRIMARY KEY - string - Unique hash of the game from the replay file, used to identify duplicate games
* map_name - string - Name of the map on which the game was played
* team_1_hash - string - Hash of the first team playing.  Keyed to *teams* table primary key
* team_2_hash - string - Hash of the second team playing.  Keyed to *teams* table primary key
* winner_team_hash - string - Hash of the winning team.  Will be a duplicate of one of the previous 2.  Keyed to *teams* table primary key


### PLAYERS TABLE
* clan - string - Clan tag for the player
* name - string - Player's name.  Not guaranteed to be unique
* region - string - Region on which this player plays.  us/kr/eu
* subregion - string - User subregion.  Used to identify the player
* toon_id - PRIMARY KEY - int - Should be unique for the user
* url - string - URL to user's b.net page

### TEAMS TABLE
* hash - PRIMARY KEY - string - Hash from replay file to uniquely identify the team
* player_1 - int - toon_id of the first player on the team.  Guaranteed to be not null
* player_2 - int - toon_id of the second player on the team.  May be null, which would indicate a 1v1 team

### PURCHASES TABLE
* game_hash - string - Key in games table of in which game this unit was created
* game_second - int - Time in game seconds in which this unit creation occurred/created (not when it was triggered)
* location_x - int - X location in map coordinates where unit was created
* location_y - int - Y location in map coordinates where unit was created
* owner - int - toon_id of the player who created this unit (see *players* table)
* unit_type - string - Unit type created (larva, zealot, broodlord, etc.)
* unit_id - int - ID of this unit purchase.  Unique to this game.  This plus game_hash uniquely identifies the purchase across all replays

### DEATHS TABLE
* game_hash - string - Key in games table of in which game this unit death occurred
* game_second - int - Time in game seconds in which this unit death occurred
* killing_unit_id - int - ID of unit that killed this unit.  This plus the game_hash will create a unique match of which unit did killed this one from the *purchses* table
* location_x - int - X location in map coordinates where death occurred
* location_y - int - Y location in map coordinates where death occurred
* unit_id - int - ID of unit that died.  This plus the game_hash will create a unique match of which unit died and can be matched to the *purchases* table

###### Thanks to Greg, for never believing in me.
