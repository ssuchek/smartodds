# Smartodds: Python Developer Test

## Task:
You've been asked to import data from the [tennis-data](http://tennis-data.co.uk) website. The project should use python and provide:
* A HTTP API that add/edit/get the tennis data (no UI needed)
* A way to import data from the source
* A well organized repository showing your best practices
* An example of your approach to unit test / TDD
* An easy and documented way to run the project
* A deployment / CI strategy. Config files and/or explanation in the README. This part do not need to work.
* A short explanation of your choices, assumptions and shortcuts, notably the way you structure the data in storage

The data is provided as zip file. e.g. [2011](http://tennis-data.co.uk/2011/2011.zip).  
A description of the fields contained in the file can be found [here](http://www.tennis-data.co.uk/notes.txt).


Additionnally, in the context of your development team being asked to implement the following :
* We have another provider giving the current weather data for any given coordinate via an HTTP API.
* And another one is providing live action by action account of a tennis game via websocket.
* we need to provide for each live game a live stream of mixed event (game action, weather conditions changes)

You are having a brainstorming session with your fellow developers about your approach/design/technology choices. Write/draw 3-4 ideas/concerns you would bring to the table (what you can come up in 10-15 mins max). Specify any assumptions that you made. 

## Description

It is a Python-based API build using Flask. It allows to:
1. Extract yearly data from [tennis data](http://tennis-data.co.uk/), transform and load into the SQLite local database. 
2. Get and download data from database using filtering and global search.
3. Upload additional JSON data to database.
4. Delete data from database.

## Data structure 

Data structure is based on the description given in [notes](http://www.tennis-data.co.uk/notes.txt) and yearly data samples available in the form of ZIP files: `http://www.tennis-data.co.uk/<year>/<year>.zip`.

Database contains three tables that correspond to main entities: tournaments, match results and bets as described in [schema file](data/db/db_table_schemas.json).
The main keys are:
1. **ATP**: tournament number for a given year. The tournament order is the same for each year, so one-to-one correspondence of a certain tournament to its number is assumed.
2. **Year**: year is the part of unique identifier as ATP cannot be the only unique key (the pool of ATP numbers is the same each year). 
3. **Winner** and **Loser**: results and bets tables contain information about results and bets for each match in each round of the tournament. Therefore ATP and Year are no longer unique identifiers and should be extended using Winner and Loser fields correspond to match winner and match loser.
4. Results and bets tables reference main tournament table on the delete cascade using ATP and Year keys - if any tournament information is deleted from tournaments table, the corresponding match results and bets are also deleted.



