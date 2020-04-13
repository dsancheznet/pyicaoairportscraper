#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys, requests, string, sqlite3
from bs4 import BeautifulSoup
from bs4 import diagnose

class Airport:
    isValid = None
    def __init__( self, tmpCode, tmpDebug = False ):
        #Set the airport Code
        self.ICAO = tmpCode.upper()
        #Search for the airport online
        #Define URL
        myURL = "https://ourairports.com/airports/" + tmpCode.upper() + "/"
        #Request HTML
        myData = requests.get(myURL)
        #Decode HTML
        mySoup = BeautifulSoup( myData.content, 'html.parser')
        #Check if we have an error reading back data
        try:
            #Got a NOTFOUND?
            if mySoup.find('p', class_='alert alert-danger').b.text=='“Not found”':
                #YES - Set data validity to false
                self.isValid = False
        #This code is executed whenever we DID get an error (this is what we want)
        except AttributeError:
            #Find the airport info paragraph
            myArray1 = mySoup.find('p', class_='airport-info')
            #Find the information table
            myArray2 = mySoup.find('table', class_='small table table-striped').text.split('\n')
            #Find the county flag
            myFlag = mySoup.find( 'img', class_='flag' )['src']
            #Store it...
            self.FLAG = myFlag.split('/')[3].split('.')[0]
            #Store IATA Code
            self.IATA = mySoup.title.text.split(' ')[0]
            #Is IATA equal to ICAO?
            if self.IATA == self.ICAO:
                #YES - Leave IATA code blank
                self.IATA = ""
            #Initialize an impossible position
            tmpPosition = -1
            #Iterate over the airport information (including line numbers)
            for tmpCounter, tmpLine in enumerate( myArray1.prettify().split('\n') ):
                #Does this line exist?
                if  tmpLine == ' <br class="visible-xs"/>':
                    #YES - Then the next line is going to be (hopefully) the Cityname
                    tmpPosition = tmpCounter + 1
                #Is this the line where the city name should be??
                if tmpCounter == tmpPosition:
                    #YES - Do we have the city name at hand?
                    if not tmpLine[:20] == ' <a href="/countries':
                        #YES - Store it ...
                        self.CITY = tmpLine.strip(' ,').replace("'","`")
                    else:
                        #NO - Leave it blank, because then there is no city.
                        self.CITY = ""
            #Store everything else...
            self.NAME = myArray1.strong.text.strip().replace("'","`")
            #Is a Region AND Country declared?
            if len( myArray1.find_all('a') )>1:
                #YES - Get the region
                self.REGION = myArray1.find_all('a')[0].text.replace("'","`")
                #Get the country from the array
                self.COUNTRY = myArray1.find_all('a')[1].text.replace("'","`")
            #Is a region declared?
            elif len( myArray1.find_all('a') )==1:
                #NO - Leave the region field empty
                self.REGION = ""
                #Get the country from the array
                self.COUNTRY = myArray1.find_all('a')[0].text.replace("'","`")
            else:
                #NONE OF THE ABOVE - Leave region empty
                self.REGION = ""
                #Leave country empty
                self.COUNTRY = ""
            #Get latitude
            self.LAT = myArray2[3].strip().split(' ')[0]
            #Get longitude
            self.LON = myArray2[7].strip().split(' ')[0]
            #Mark the data as valid
            self.isValid = True

if __name__ == "__main__":
    #The airport code (ICAO) should be the first parameter.
    myAirport = Airport( sys.argv[1], True )
    #Are there more parameters?
    if len( sys.argv )>2:
        #YES - Shall we enter the debug mode?
        if sys.argv[2].upper() == "DEBUG":
            #Is the data valid?
            if myAirport.isValid == True:
                #YES - Print all the information
                print( " ℹ️   " )
                print()
                print( " OACI    " + sys.argv[1].upper() )
                print( " IATA    " + myAirport.IATA )
                print( " Name    " + myAirport.NAME )
                print( " City    " + myAirport.CITY )
                print( " Region  " + myAirport.REGION )
                print( " Country " + myAirport.COUNTRY )
                print( " Flag    " + myAirport.FLAG )
                print( " Coord   " + myAirport.LAT + " / " + myAirport.LON )
                print()
        else:
            print( "You may want to check your parameters." )
    else:
        #NO - Is the data valid?
        if myAirport.isValid == True:
            #YES - Print overview
            print( " 💽   " + sys.argv[1] )
            print()
            print(" Name    " + myAirport.NAME )
            print(" ICAO    " + myAirport.ICAO )
            print(" IATA    " + myAirport.IATA )
            print(" City    " + myAirport.CITY )
            print(" Region  " + myAirport.REGION )
            print(" Country " + myAirport.COUNTRY )
            print(" Coord   " + myAirport.LAT + "," +myAirport.LON )
            print(" Flag    " + myAirport.FLAG )
            #Store it in the database
            try:
                #Connect to DB
                myConnection = sqlite3.connect('icao.db') #TODO: Get the DB name as a command line argument.
                #Get the cursor
                myCursor = myConnection.cursor()
                #Instert data
                myCursor.execute("INSERT INTO airports VALUES( '"+myAirport.ICAO+"', '"+myAirport.IATA+"', '"+myAirport.NAME+"', '"+myAirport.CITY+"', '"+myAirport.REGION+"', '"+myAirport.COUNTRY+"', "+myAirport.LAT+", "+myAirport.LON+", '"+myAirport.FLAG+"' )")
                #Write it
                myConnection.commit()
                #Inform upon success
                print()
                print(" ✔️   saved")
                print()
            #If there is any error of type sqlite3.OperationalError, sqlite3.IntegrityError
            except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
                #Inform the user
                print()
                print( " ⚠️   " + str(e) )
                print()
                #Open the error log
                myErrorLog = open("errors.txt","a")
                #Log the error to file
                myErrorLog.write("Error storing:" + myAirport.ICAO + ":" + str(e) + '\n')
                #Flose the file
                myErrorLog.close()
            #Execute this anyways
            finally:
                #Close the database
                myConnection.close()
            #Print message
