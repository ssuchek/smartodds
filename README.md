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
