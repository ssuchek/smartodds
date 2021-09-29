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
1. Extract yearly data from [tennis data source](http://tennis-data.co.uk/), transform and load into the SQLite local database. 
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

## Quickstart

### Install required dependencies

`python -m pip install requirements.txt`

### Run Flask application

To run Flask application, use the following code:
`python api.py `

Database is created automatically.

### Import year data in database

Yearly data is available in the form of ZIP files at 
`http://www.tennis-data.co.uk/<year>/<year>.zip`

To import data in the database, one can use:
1. Simple UI link: `http://<hostname>/api/import/data/<year>`
2. POST request to `http://<hostname>/api/import/data/<year>`. E.g., for application run on the localhost, a Python request to import data for 2012 would look as follows:
`import requests

url = 'http://127.0.0.1:5000/api/get/import/2012'

r = requests.post(url)`

### Upload data in database

To manually load data in the database, one can use post request with JSON body:

```
import requests

url = 'http://127.0.0.1:5000/api/upload/data'

data = {
    "ATP":122,"AvgL":"2.5","AvgW":"1.51","B365L":"2.62","B365W":"1.44","Best of":3,"Comment":"Completed","Court":"Outdoor","Date":"2022-05-04","EXL":"2.5","EXW":"1.5","L1":4,"L2":2,"L3":0,"L4":0,"L5":0,"LBL":"2.25","LBW":"1.57","LPts":1215,"LRank":28,"Location":"Brisbane","Loser":"Mayer F.","Lsets":0,"MaxL":"3.2","MaxW":"1.57","PSL":"2.73","PSW":"1.52","Round":"2nd Round","SJL":"2.38","SJW":"1.53","Series":"ATP250","Surface":"Hard","Tournament":"Brisbane International","W1":6,"W2":6,"W3":0,"W4":0,"W5":0,"WPts":1070,"WRank":36,"Winner":"Pffeifer M.","Wsets":2,"Year":2022
}

r = requests.post(url, json=data)
```

Required fields are ATP (integer) and Year (integer). Other fields are optional:
1. String fields: Winner, Loser, Comment, Court, Location, Tournament, Series, Surface.
2. Intefer fields: ATP, Year, W1, W2, W3, W4, W5, L1, L2, L3, L4, L5, WRank, LRank, Wsets, Lsets, Best of, LPts, WPts
3. Float fields: AvgL, AvgW, B365L, B365W, EXL, EXW, LBL, LBW, MaxL, MaxW, PSL, PSW, SJL, SJW
4. Date fields: Date (%Y-%M-%d)\

### Get data from database

To get data from database, one can use UI link
`http://<hostname>/api/get/data/<year>`

Link supports additional filters, global search and pagination. 

E.g., link to get all data for year 2014 with *ATP=2* that contains phrase *Hard* looks as follows:
`http://<hostname>/api/get/data/2014?ATP=2&search=Hard`

Valid filters include: *ATP, Date, Tournament, Location, Series, Court, Surface, Winner, Loser, Round, BestOf, WRank, LRank, WPts, LPts,  W1, L1, W2, L2,  W3, L3, W4, L4, W5, L5, Wsets, Lsets,  Comment, B365W, B365L, EXW, EXL,  LBW, LBL, PSW, PSL,  SJW, SJL, MaxW, MaxL, AvgW, AvgL*

Search is performed only over string and year fields: *Winner, Loser, Comment, Court, Location, Tournament, Series, Surface, Year*

If one wants to display a certain page, use page parameter:
`http://<hostname>/api/get/data/2014?page=1`

### Download data from database

To download data from database, one can use UI link
`http://<hostname>/api/get/data/<year>/download`

which will download the file `<year>.json`.

Filters, search and pagination is applied in the same way as described in [section **Get data from database**](#get-data-from-database).







