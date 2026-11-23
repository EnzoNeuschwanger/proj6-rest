# Brevet Time Calculator with MongoDB database and WebAPI + FrontEnd 

This project is a webAPI reimplementation of the RUSA ACP controle time calculator using Flask and AJAX. It also stores the calculated times in a MongoDB database. It also comes with a front end to use the API

## Dependancies
This project uses the python libraries:
* arrow
* Flask
* nose
* pep8
* autopep8
* python 

Which can be installed using Python-Pip

This project also relies on the Docker MongoDB image, although you can use the frontend attached to any instance of MongoDB

## Usage
### Starting the Server
* Make a copy of the "credentials-skel.ini" file in both the api_server and frontend directories, named credentials.ini. Fill out all the details for both respectively.
* Run "docker compose up --build" in your terminal

### Using the Frontend
* Set the time, date and brevet at the top of the page.
* Type the distances of your controls. As you do the times should begin to appear
* Clicking "submit" will save all the times you've typed in into the database
* Clicking "display" will take you to a page, where you can try out the different features of the webAPI.

### Using the WebAPI
You can access the WebAPI from it's IP Address at port 5001 (don't change this unless you really have to).
Accessing the entire database can be done using the "/listAll" URI. 
By default, the webAPI will give you JSON formated information

Example:
````json
{
  "row0": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "close_t": "Sun 1/1 1:30 ",
    "distance": "200",
    "km": "10",
    "location": "Control 1",
    "miles": "6.2",
    "open_t": "Sun 1/1 0:17 "
  },
  "row1": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "close_t": "Sun 1/1 2:00 ",
    "distance": "200",
    "km": "20",
    "location": "Control 2",
    "miles": "12.4",
    "open_t": "Sun 1/1 0:35 "
  },
  "row2": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "close_t": "Sun 1/1 6:40 ",
    "distance": "400",
    "km": "100",
    "location": "Control 3",
    "miles": "62.1",
    "open_t": "Sun 1/1 2:56 "
  },
  "row3": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "close_t": "Sun 1/1 13:20 ",
    "distance": "400",
    "km": "200",
    "location": "Control 4",
    "miles": "124.3",
    "open_t": "Sun 1/1 5:52 "
  }
}
````
You can also specifiy a CSV output by adding /csv/ to the URI

Example:
````csv
distance,begin_date,begin_time,km,mi,location,open,close
200,2017-01-01,00:00,10,6.2,Control 1,Sun 1/1 0:17 ,Sun 1/1 1:30 
200,2017-01-01,00:00,20,12.4,Control 2,Sun 1/1 0:35 ,Sun 1/1 2:00 
400,2017-01-01,00:00,100,62.1,Control 3,Sun 1/1 2:56 ,Sun 1/1 6:40 
400,2017-01-01,00:00,200,124.3,Control 4,Sun 1/1 5:52 ,Sun 1/1 13:20 
````
Using the URIs: "/listOpenOnly" and "/listCloseOnly", you can get exculsively those datapoints

listOpenOnly:
````json
{
  "row0": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "distance": "200",
    "km": "10",
    "location": "Control 1",
    "miles": "6.2",
    "open_t": "Sun 1/1 0:17 "
  },
  "row1": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "distance": "200",
    "km": "20",
    "location": "Control 2",
    "miles": "12.4",
    "open_t": "Sun 1/1 0:35 "
  },
  "row2": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "distance": "400",
    "km": "100",
    "location": "Control 3",
    "miles": "62.1",
    "open_t": "Sun 1/1 2:56 "
  },
  "row3": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "distance": "400",
    "km": "200",
    "location": "Control 4",
    "miles": "124.3",
    "open_t": "Sun 1/1 5:52 "
  }
}
````
The WebAPI also supports using the top argument to get the top number of controls ordered from shortest time to longest time

example (?top=2):
````json
{
  "row0": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "close_t": "Sun 1/1 1:30 ",
    "distance": "200",
    "km": "10",
    "location": "Control 1",
    "miles": "6.2",
    "open_t": "Sun 1/1 0:17 "
  },
  "row1": {
    "begin_date": "2017-01-01",
    "begin_time": "00:00",
    "close_t": "Sun 1/1 2:00 ",
    "distance": "200",
    "km": "20",
    "location": "Control 2",
    "miles": "12.4",
    "open_t": "Sun 1/1 0:35 "
  }
}
````

## Credits

acp_times and other bits and bobs written by Enzo Neuschwanger (eneuschw@uoregon.edu)

Everything else is from UO CS322

