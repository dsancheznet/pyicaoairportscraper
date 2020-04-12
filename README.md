# ICAO Airport Scraper

## A tool to scrape airport data from the internet

### Usage

`./scrape.py XXXX [DEBUG]`

Where XXXX is the ICAO code for the airport you want to get the info for;

There are two ways of using this tool:

1 - Just downloading the data and presenting it on the terminal

This would be done by appending the parameter `DEBUG` to the scape command.

2 - Saving the scraped data into a sqlite database ( `icao.db` )

This does not require anything special. If the airport is not found, nothing is printed out. If the airport is found, the information is printed to the terminal and at the same time the data is inserted into the DB. If the airport does already exist in the DB, an error is thrown and the ICAO code is saved to errors.txt.

Let's say you wanted to scrape a whole country. Then you could write a terminal loop to scrape various letters (be aware that this takes an awful lot of time):

```bash
START_time=`date`;
LETTER='X';
clear;
for t in {A..Z}; do
   for s in {A..Z}; do
       for l in {A..Z}; do
           echo -ne " $LETTER$t$s$l\\r";
           ./scrape.py $LETTER$t$s$l;
       done;
   done;
done;
echo "Start time: $START_TIME";
$END_TIME=`date`;
echo "End   time: $END_TIME"
```

You could even add another level of depth to scrape the whole database. But be aware:

Let's say that every airport takes 2 seconds to check on average; that would make

<b>T</b><sub>total</sub> = T<sub>iter</sub> * ( I<sub>digit</sub><super>4</super> )

Being a total of 913.952 seconds. This makes a total of 10,578148148 days.

### icao.db structure

This sqlite3 database is structured as follows:

```sqlite3
create table airports (
  cao varchar(4) unique primary key,
  iata varchar(3) ,
  name varchar(255),
  city varchar(255),
  region varchar(255),
  country varchar(255),
  latitude numeric,
  longitude numeric,
  flag varchar(3)
)
```

### Data source

The source of out data is the [OurAirports](https://ourairports.com/) webpage, which seems pretty complete regarding the information stored.
