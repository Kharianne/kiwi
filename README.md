# Kiwi Python Weekend
## Basics
This short script looks for:
* --one-way (default) - it is not necessary to run script with this parameter
* --return X
* --cheapest (default) - it is not necessary to run script with this parameter
* --shortest
flights.

One-way and return are mutually excluded for program run so as shortest with cheapest.

## .ini files
* book_flight.ini - there are all api configs such as urls and api_key
* passenger.ini - this file could be edited to change info about passangers. In this version fields as birthday and email are not validated 

## IATA validation
For real-time validation I used open API https://iatacodes.org - script is just checking if it has appropriate response for given IATA code.
