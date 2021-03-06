import sys
import cx_Oracle # the package used for accessing Oracle in Python
import getpass # the package for getting password from user without displaying it
import random
from operator import itemgetter

# This function when evoked will create a view that is extremely useful
#for the rest of the program and is utilized quite a bit.
def create_available_view(connection):

    #crazy shit creating the available flights view table if it does not exist,
    #if it already exist, drop it then create.
    curs = connection.cursor()
    curs.execute("SELECT view_name from user_views")
    rows = curs.fetchall()
    for row in rows:
        #print(row[0])
        if row[0] == "AVAILABLE_FLIGHTS" :
            curs.execute("DROP view available_flights")
    curs.execute("create view available_flights(flightno,dep_date, src,dst,dep_time,arr_time,fare,seats,price) as select f.flightno, sf.dep_date, f.src, f.dst, f.dep_time+(trunc(sf.dep_date)-trunc(f.dep_time)), f.dep_time+(trunc(sf.dep_date)-trunc(f.dep_time))+(f.est_dur/60+a2.tzone-a1.tzone)/24, fa.fare, fa.limit-count(tno), fa.price from flights f, flight_fares fa, sch_flights sf, bookings b, airports a1, airports a2 where f.flightno=sf.flightno and f.flightno=fa.flightno and f.src=a1.acode and f.dst=a2.acode and fa.flightno=b.flightno(+) and fa.fare=b.fare(+) and sf.dep_date=b.dep_date(+) group by f.flightno, sf.dep_date, f.src, f.dst, f.dep_time, f.est_dur,a2.tzone, a1.tzone, fa.fare, fa.limit, fa.price having fa.limit-count(tno) > 0 ")
    connection.commit()
    curs.close()

def create_good_connections(connection):
    #crazy shit creating the good_connections view table if it does not exist,
    #if it already exist, drop it then create.
    curs = connection.cursor()
    curs.execute("SELECT view_name from user_views")
    rows = curs.fetchall()
    for row in rows:
        if row[0] == "GOOD_CONNECTIONS":
            curs.execute("DROP view good_connections")
    curs.execute("create view good_connections (src,dst,dep_date,arr_time,flightno1,flightno2, layover,price,seats,fare1,fare2) as select a1.src, a2.dst, a1.dep_date,a2.arr_time, a1.flightno, a2.flightno, a2.dep_time-a1.arr_time, min(a1.price+a2.price), min(a1.seats+a2.seats),a1.fare,a2.fare from available_flights a1, available_flights a2 where a1.dst=a2.src and a1.arr_time +1.5/24 <=a2.dep_time and a1.arr_time +5/24 >=a2.dep_time group by a1.src, a2.dst, a1.dep_date, a1.flightno, a2.flightno, a2.dep_time, a1.arr_time, a2.arr_time, a1.fare, a2.fare")
    connection.commit()
    curs.close()

# loginMenu is the first thing that the user will hit in the terminal screen, 
#where the user is going to have to decide if they are already registered or
#if they are not already registered. Alternatively they can just exit.
#Perhaps one of the most core things about this aside from that is the fact
#that this returns the username and password of the user to the main bulk of
#the program.
def loginMenu(connection):
    #Here the connection cursor is established! 
    curs= connection.cursor()
    #INITIAL SCREEN FOR SCREENING NEW OR OLD USERS.
    loginMenu = True
    oldUser = False
    newUser = False
    userEmail = "irrelevantPlaceholder"
    userPassword = "irrelevantPlaceholder2"
    loginOptions = {}
    loginOptions['1'] = "Already Registered"
    loginOptions['2'] = "Not Already Registered" 
    loginOptions['3'] = "Exit"
    
    # So long as the loginMenu is true we will continually loop through this.
    #essentially forcing the user to make some meaningful decision.
    while loginMenu == True:
        print("LOGIN SCREEN:\nAre you registered yet or not?\n")
        for eachOption in sorted(loginOptions):
            print (eachOption, loginOptions[eachOption])
        #Obtain the user choice.
        #This is going to set booleans which will control flow access.
        loginMenuSelection = input("Choose an option from above ")
        if loginMenuSelection == '1':
            #print("GO TO USERNAME AND PASSWORD PART!")
            oldUser = True #This user is requesting as an old user!
        if loginMenuSelection == '2':
            #print("GO TO NEW REGISTRATION PAGE!")
            newUser = True #This user is requesting as a new user!
        if loginMenuSelection == '3':
             return(False, userEmail, userPassword, False) #EXIT with placeholders
      
        #USER REGISTRATION SCREEN.
        #This is the dumping zone for all functionalities needed to allow
        #the user to register. 
        if newUser == True:
            print("Please enter information to register.")
            newUserName = input("Email: ")
            newUserPass = getpass.getpass()






            #Place the variables into a string that will be sent through Oracle 
            sqlRegisterString = ("INSERT INTO users (email, pass, last_login) "
                + "VALUES (" +  "'" +newUserName+"'" + ", " +"'" +newUserPass +
                "'" + ", SYSDATE)")
            #DUPLICATE BLOCK.
            #This block is dedicated to seeing if a new registration is 
            #attempting to use a username we ALREADY have in the database.
            #First thing to do is to formulate the string to be sent to Oracle
            sqlDoubleRegistrationString = ("Select count(*) from users where "
                "email = " + "'" + newUserName + "'")
            curs.execute(sqlDoubleRegistrationString)
            rows = curs.fetchall()
            doubleRegistrationError = False #Predefine there to be no error
            #Check and directly compare values here. IS there a duplicate?!
            #If so then I will set a warning flag to reject this registration.
            for row in rows:
                if row[0] == 1:
                    print("\nERROR! We already have THAT email in the "
                        "database!")
                    print("Please try another email!\n")
                    doubleRegistrationError = True #ERROR! Already have email!
            #This block ONLY WORKS if the flag was set that we DO NOT already
            #have that email! 
            if doubleRegistrationError != True:
                curs.execute(sqlRegisterString) #execute SQL command
                connection.commit() #SAVE the database changes!!!!!!!!!!!

                #Set variables to the entered email and password and
                #then send these username and password back to the bulk
                # of the program
                userEmail = newUserName 
                userPassword = newUserPass
                print("Name and password accepted and put into database!")
                print("Putting you into the application itself...")
                loginMenu = False
                return(True, userEmail, userPassword, False) 
        

        #USER LOGIN (OLD / ALREADY EXISTING USER!!!!) SCREEN
        #Obtain username(email) and password from the user.
        #formulate into a string and then funnel string into Oracle
        #check that we HAVE this username and password combination
        #IFFFF we do have the combo then we will return to the main bulk of the
        #program with the given username, password and proceed with the program.
        if oldUser == True:
            print("Please give your log in info:")
            oldUserName = input("Email!: ")
            oldUserPass = getpass.getpass()
            sqlLoginString = ("Select count(*) from users where email = " 
                + "'" + oldUserName + "'" + " and pass = " + "'" + oldUserPass + 
                "'")
            curs.execute(sqlLoginString)
            connection.commit()
            rows = curs.fetchall()
            for row in rows:
                if row[0] == 0:
                    print("\nSorry, you entered EITHER an invalid username " 
                        "OR invalid password. \n Maybe you made a typo?")
                    print("Please try again! :(\n\n")
                if row[0] == 1:
                    print("Login confirmed!")
                    userEmail = oldUserName
                    userPassword = oldUserPass
                    #Now I want to see if the user is an airline agent or not!!!
                    sqlAirlineAgentString = ("Select count(*) from "
            "airline_agents where email = " + "'" + userEmail
                        + "'") 
                    curs.execute (sqlAirlineAgentString)
                    rows = curs.fetchall()
                    for row in rows:
                        if row[0] == 0:
                            airLineAgent = False
                            #print("GAAHHHH!!!!!!!!")
                            return(True, userEmail, userPassword, airLineAgent)
                        if row[0] > 0: 
                            airLineAgent = True
                            #print("!!!!!!!!!!!!!!!")
                            return(True, userEmail, userPassword, airLineAgent)
            

def mainMenu(connection, userEmail, userPassword, airLineAgent):
    #Now we have that main menu of a trillion various options as requested.
    #Initialize all the things. 7 different options.
    mainMenu = True
    mainMenuOptions = {} #empty dict
    isAirlineAgent = False #THIS CAN BE TRUE OPENING MORE OPTIONS!
    mainMenuOptions['1'] = "Search for flights."
    mainMenuOptions['2'] = "Make a booking."
    mainMenuOptions['3'] = "List and delete exiting bookings."
    mainMenuOptions['4'] = "Logout."
    if airLineAgent:
        mainMenuOptions['5'] = "AIRLINE AGENTS ONLY: Record a flight departure."
        mainMenuOptions['6'] = "AIRLINE AGENTS ONLY: Record a flight arrival."
    #Initialize the mainMenu where the user will be looping through until
    #We have a series of menu options to choose from.
    while mainMenu == True:
        print("\n")

        print("Welcome to the main screen. We have various options here to choose from")

        for eachOption in sorted(mainMenuOptions):
            print (eachOption, mainMenuOptions[eachOption])
    
        
        mainMenuSelection = input("Which option do you want?: ")
        if mainMenuSelection == '1':
            searchForFlights(connection, userEmail)
    
            
        if mainMenuSelection == '2':
            makeBookingOption(connection, userEmail)
    
        if mainMenuSelection == '3':
            listAndDeleteExitingBookings(connection, userEmail)
    
            
        if mainMenuSelection == '4':
            logoutConfirm = logoutFunction(connection, userEmail, userPassword)
            return logoutConfirm
            
        if mainMenuSelection == '5' and airLineAgent:
            recordFlightDeparture(airLineAgent, connection)

        
        if mainMenuSelection == '6' and airLineAgent:
            recordFlightArrival(airLineAgent, connection)
    


#All of the functions called upon by the main menu. (All 6 options!) 
def searchForFlights(connection, user_email):
    # prompt user for source, destination and departure date
    curs = connection.cursor()
    print("SEARCH FOR FLIGHTS OPTION")
    
    #sql statements for case insensitivity
    curs.execute("alter session set NLS_COMP=LINGUISTIC")
    curs.execute("alter session set NLS_SORT=BINARY_CI")
    #searching for airports if the user didn't give a 3 letter airport code
    input_source = input("Enter source: ")
    if len(input_source) > 3 :
        curs.execute("SELECT * from AIRPORTS where city ="+"'"+input_source+"'" 
            + " or name LIKE '%"+input_source+"%'" )
        # executing a query
        # get all data and print it
        rows = curs.fetchall()
        for row in rows:
            print("|Airport Code:",row[0],"|Airport Name:",row[1],
                "|City:",row[2],"|Country:",row[3],"|Time Zone:",row[4])
        flight_source = input("\nPlease select and enter the three letter"
            "airport code of your source airport: ")
        print("\n")

    else :
        flight_source = input_source

    #searching for destination airports
    input_destination = input("Enter destination: ")
    if len(input_destination) > 3 :
        curs.execute("SELECT * from AIRPORTS where city ="+"'"+input_destination
            +"'" + " OR name LIKE '%"+input_destination+"%'" )
        # executing a query
        # get all data and print it
        rows = curs.fetchall()
        for row in rows:
            print("|Airport Code:",row[0],"|Airport Name",row[1],"|City:"
                ,row[2],"|Country",row[3],"|Time Zone:",row[4])
        flight_destination = input("\nPlease select and enter the three letter"
            "airport code of your destination airport: ")
        print("\n")

    else:
        flight_destination = input_destination

    #only taking departure date in this format
    flight_departure = input("Enter departure date in DD-Mon-YY format: ")
    print("\n")
    orderCheck = input("How would you like your results to be sorted(CON/PRI): ")
    if orderCheck == "CON":
        #direct flight results
        curs.execute("SELECT flightno, src, dst, dep_date, arr_time, seats,"
           " price, fare FROM AVAILABLE_FLIGHTS WHERE src =" + "'" +flight_source+ "'" +
           " AND dst =" + "'" +flight_destination+ "'" + " and dep_date =" + "'" +
           flight_departure+ "'" + " and seats > 1 ORDER BY price")

        counter=0
        rows = curs.fetchall()
        for row in rows:
            counter=counter+1
            print(str(counter).ljust(4)+"|Flight Number:",row[0],"|Source Airport:",row[1],
                "|Destination Airport:",row[2],"|Departure Date:",
                row[3].strftime('%d-%b-%Y'),"|Arrival Time:",row[4].strftime('%d-%b-%Y') ,"|Seats Available:",row[5],
                "|Seat Price:",row[6],"|number of stops: 0|\n")
        curs.execute("SELECT flightno1, fare1, flightno2, fare2, src, dst, dep_date, arr_time, layover,seats, price from good_connections where src ="+"'" +flight_source+ "'"+" AND dst =" + "'" +flight_destination+ "'" + " and dep_date =" + "'" + flight_departure+ "'")
        rows2 = curs.fetchall()
        for row in rows2:
            counter=counter+1
            print(str(counter).ljust(4)+"|Initial Flight Number:",row[0],"|Initial Fare Type:",row[1],"|Connecting Flight Number:",row[2],"|Connecting Fare Type:",row[3],"|Source Airport:",row[4],"|Destination Airport:",row[5],"|Departure Date:",row[6].strftime('%d-%b-%Y'), "|Arrival Time:", row[7].strftime('%d-%b-%Y'),"|Layover Time:",row[8],"|Seats Available:",row[9],"|Seat Price:",row[10],"|Number of stops: 1|\n")
        

        if counter==0:
            print("There are no flights to show!")
            return
        #merge both rows
        allRows = rows + rows2

        ##ask user if booking is wanted                                                                                                                                                                            

        bookingCheck = input("Would you like to book a flight?(Y/N): ")
        if bookingCheck == "Y":
            userRow = input("What is the corresponding row number?: ")
            selectedRow = allRows[int(userRow)-1]
            if (len(selectedRow)<9):
                makeBookingNoInput(connection,user_email,selectedRow[0],selectedRow[3].strftime('%d-%b-%Y'),selectedRow[7])
            else:
                print("First flight")
                makeBookingNoInput(connection,user_email,selectedRow[0],selectedRow[6].strftime('%d-%b-%Y'),selectedRow[1])
                print("Second flight")
                makeBookingNoInput(connection,user_email,selectedRow[2],(selectedRow[7]-selectedRow[8]+selectedRow[7]).strftime('%d-%b-%Y'),selectedRow[3])
        else:
            pass

    elif orderCheck == "PRI":
                #direct flight results                                                                                                                                                                                  
        curs.execute("SELECT price, flightno, src, dst, dep_date, arr_time, seats, fare"
           " FROM AVAILABLE_FLIGHTS WHERE src =" + "'" +flight_source+ "'" +
           " AND dst =" + "'" +flight_destination+ "'" + " and dep_date =" + "'" +
           flight_departure+ "'" + " and seats > 1 ORDER BY price")

        #store those rows
        rows1 = curs.fetchall()
        
            
        curs.execute("SELECT price, flightno1, fare1, flightno2, fare2, src, dst, dep_date, arr_time, layover, seats from good_connections where src ="+"'" +flight_source+ "'"+" AND dst =" + "'" +flight_destination+ "'" + " and dep_date =" + "'" + flight_departure+ "'")

        #store the other rows
        rows2 = curs.fetchall()

        #merge them because now we have all rows
        allrows = rows1+rows2
        
        #sory them using the imported package (by price)
        sortedrows = sorted(allrows, key=itemgetter(0))
        
        counter=0
        #print appropriate information depending on which table it came from 
        for row in sortedrows:
            
            counter=counter+1
            
            if len(row)<9:
                print(str(counter).ljust(4),"|Seat Price:",row[0],"|Flight Number:",row[1],"|Source Airport:",row[2],"|Destination Airport:",row[3],"|Departure Date:",row[4].strftime('%d-%b-%Y'),"|Arrival Time:",row[5].strftime('%d-%b-%Y') ,"|Seats Available:",row[6],"|number of stops: 0|\n")

            else:

                print("|Seat Price:",row[0],"|Initial Flight Number:",row[1],"|Initial Fare Type:",row[2],"|Connecting Flight Number:",row[3],"|Connecting Fare Type:",row[4],"|Source Airport:",row[5],"|Destination Airport:",row[6],"Departure Date:",row[7].strftime('%d-%b-%Y'), "|Arrival Time:", row[8].strftime('%d-%b-%Y'),"|Layover Time:",row[8],"|Seats Available:",row[10],"|Number of stops: 1|\n")
            

        if counter==0:
            print("There are no flights to show!")
            return

        ##ask user if booking is wanted   def makeBookingNoInput(connection,user_email,user_flightno,user_departure):

        bookingCheck = input("Would you like to book a flight?(Y/N): ")
        if bookingCheck == "Y":
            userRow = input("What is the corresponding row number?: ")
            selectedRow = sortedrows[int(userRow)-1]
            if (len(selectedRow)<9):
                makeBookingNoInput(connection,user_email,selectedRow[1],selectedRow[4].strftime('%d-%b-%Y'),selectedRow[7])  
            else:
                print("First flight:")
                print(selectedRow[6])
                makeBookingNoInput(connection,user_email,selectedRow[1],selectedRow[6].strftime('%d-%b-%Y'),selectedRow[1])

                print("Second flight:")
                makeBookingNoInput(connection,user_email,selectedRow[2],(selectedRow[7]-selectedRow[8]+selectedRow[7]).strftime('%d-%b-%Y'),selectedRow[3])

        else:
            pass

    curs.close()

def listAndDeleteExitingBookings(connection,user_email):
    print("VIEW AND DELETE EXISTING BOOKINGS OPTION")

    #create cursor and get info from user
    curs = connection.cursor()
    #user_email = input("Please enter your email: ")
    user_email = "'"+ user_email + "'"

    #get the required info from the required tables
    curs.execute("SELECT UNIQUE bookings.tno, passengers.name, bookings.dep_date, tickets.paid_price FROM bookings, passengers, tickets WHERE bookings.tno=tickets.tno AND passengers.email=tickets.email AND passengers.name = tickets.name AND passengers.email =" + user_email)

    #get all rows, and initialize counter
    rows = curs.fetchall()
    counter=0


    for row in rows:

        #print top info bar
        if counter==0:
            print("Row number".ljust(25)+"Ticket number".ljust(25)+"Passenger name".ljust(25)+"Departure date".ljust(25)+"Price".ljust(25))
        counter+=1
        
        #print the row number first
        print(str(counter).ljust(25), end="" )

        #then print the rest of the info
        for item in row:
            print(str(item).strip().ljust(25),end="")
        print("")

    #if counter is still 0, there were no rows
    if counter==0:
        print("There are no bookings under than email!")
        return

    #let user decide  what bookings
    print("Type the corresponding row number for more options (or type 'back' to go back)")
    users_row_number = input("Row number: ")

    #go back to menu
    if users_row_number=="back":
        return

    #let user decide what to do with that booking
    users_choice = input("Type 1 to get more details or 2 to cancel that booking: ")
    
    #get all info from the bookings table for that tno
    if users_choice == '1':
        curs.execute("SELECT * FROM bookings WHERE bookings.tno="+str(rows[int(users_row_number)-1][0]))

        rows = curs.fetchall()
        print("Ticket number: "+str(rows[0][0])+"\nFlight number: "+rows[0][1]+"\nFare: "+rows[0][2]+"\nDeparture date: "+str(rows[0][3])+"\nSeat: "+rows[0][4])

    #delete that booking
    if users_choice == '2':

        #remove row from both tables
        curs.execute("DELETE FROM bookings WHERE bookings.tno="+str(rows[int(users_row_number)-1][0]))
        curs.execute("DELETE FROM tickets WHERE tickets.tno="+str(rows[int(users_row_number)-1][0]))

        #commit it
        connection.commit()

        #recreate the views with both new tables
        create_available_view(connection)
        create_good_connections(connection)

        print("DELETE SUCCESSFULL!")
        
    #finally, close the cursor
    curs.close()

#This function is going to be dealing with the functionality of making a booking
#option. This function will 
def makeBookingOption(connection,user_email):
    curs = connection.cursor()
    cursInsert = connection.cursor()
    print("MAKE A BOOKING OPTION")
    user_name = input("Please enter your name: ")
    user_name = "'"+user_name+"'"
    user_email = "'"+user_email+"'"
    curs.execute("SELECT * from passengers where name ="+user_name+" AND email = "+user_email)
    rows = curs.fetchall()

    if rows:
        pass
    else:
        print("\nThe name you've entered was not part of our database")
        #print("Please give us your country")
        #user_name = input("Please enter your name:")
        #user_name = "'"+user_name+"'"
        user_country = input("Please enter your country:")
        user_country = "'"+user_country+"'"

        cursInsert.execute("INSERT INTO PASSENGERS values "+"("+user_email+
            ","+user_name+","+user_country+")");
        connection.commit()
    cursInsert.close()
    print("Please enter the flight number of your booking, fare type, "
        "departure date and the seat number")
    user_flightno = input("Enter flight number:")
    user_flightno = "'"+user_flightno+"'"
    user_fare = input("Enter fare type:")
    user_fare = "'"+user_fare+"'"
    user_departure = input("Enter departure date in DD-Mon-YY format:")
    user_departure = "'"+user_departure+"'"
    user_seat = input("Enter the seat number:")
    user_seat = "'"+user_seat+"'"

    check = connection.cursor()
    check.execute("SELECT * from bookings where flightno = "+user_flightno+
        " and fare = "+user_fare+" and dep_date = "+user_departure+
        " and seat = "+user_seat)
    row = check.fetchall()
    if row:
        print("The seat",user_seat,"you are tring to book on flight"
            ,user_flightno,"is already staken")
    else:
        #PRE INSTERSION CHECK----------------------------------------------------
        curs.execute("SELECT * from available_flights where flightno = "+user_flightno+
        " and fare = "+user_fare+" and dep_date = "+user_departure)
        rows = curs.fetchall()
        #END OF CHECK------------------------------------------------------------
        if rows:
            #INSERTING INTO BOOKINGS AND TICKETS ------------------------------------
            ticket_no = random.randint(1000,999999)
            curs.execute("SELECT * from tickets where tno ="+str(ticket_no))
            rows = curs.fetchall()
            if rows :
                ticket_no = random.randint(1000,999999)
            curs.execute("SELECT name from passengers where email = "+user_email)
            rows = curs.fetchall()
            user_name = rows[0][0]
            user_name = "'"+user_name+"'"
            curs.execute("SELECT distinct price from available_flights where flightno ="+user_flightno+" AND fare ="+user_fare)
            rows = curs.fetchall()
            user_price = rows[0][0]
            cursInsertTicket = connection.cursor()
            cursInsertTicket.execute("INSERT INTO tickets values "+"("+str(ticket_no)+","+user_name+","+user_email+","+str(user_price)+")")
            connection.commit()
            cursInsertTicket.close()
            cursInsertBooking = connection.cursor()
            cursInsertBooking.execute("INSERT INTO BOOKINGS values "+"("+str(ticket_no)+","+user_flightno+","+user_fare+","+user_departure+","+user_seat+")")
            connection.commit()
            cursInsertBooking.close()
        #END OF INSTERTION ------------------------------------------------------
            print("Your flight has been successfully booked, your ticket number is",ticket_no)
        else:
            print("The flight you were trying to book either does not exist in our database or is already full, sorry.")
    check.close()
    curs.close()

def makeBookingNoInput(connection,user_email,user_flightno,user_departure,user_fare):
    curs = connection.cursor()
    cursInsert = connection.cursor()
    #print("MAKE A BOOKING OPTION")
    user_name = input("Please enter your name: ")
    user_name = "'"+user_name+"'"
    user_email = "'"+user_email+"'"
    curs.execute("SELECT * from passengers where name ="+user_name+" AND email = "+user_email)
    rows = curs.fetchall()

    if rows:
        pass
    else:
        print("\nThe name you've entered was not part of our database")
        #print("Please give us your name and your country")
        #user_name = input("Please enter your name:")
        #user_name = "'"+user_name+"'"
        user_country = input("Please enter your country:")
        user_country = "'"+user_country+"'"
        cursInsert.execute("INSERT INTO PASSENGERS values "+"("+user_email+
            ","+user_name+","+user_country+")");
        connection.commit()
    cursInsert.close()
    #print("Please enter the flight number of your booking, fare type, "
     #   "departurce date and the seat number")
    #user_flightno = input("Enter flight number:")
    user_flightno = "'"+user_flightno+"'"
    #user_fare = input("Enter fare type:")
    user_fare = "'"+user_fare+"'"
    #user_departure = input("Enter departure date in DD-Mon-YY format:")
    user_departure = "'"+user_departure+"'"
    user_seat = input("Enter the seat number:")
    user_seat = "'"+user_seat+"'"

    check = connection.cursor()
    check.execute("SELECT * from bookings where flightno = "+user_flightno+
        " and fare = "+user_fare+" and dep_date = "+user_departure+
        " and seat = "+user_seat)
    row = check.fetchall()
    if row:
        print("The seat",user_seat,"you are tring to book on flight"
            ,user_flightno,"is already staken")
    else:
        #PRE INSTERSION CHECK----------------------------------------------------                                                            
        curs.execute("SELECT * from available_flights where flightno = "+user_flightno+
        " and fare = "+user_fare+" and dep_date = "+user_departure)
        rows = curs.fetchall()
        #END OF CHECK------------------------------------------------------------                                                            
        if rows:
            #INSERTING INTO BOOKINGS AND TICKETS ------------------------------------              

                                                       
            ticket_no = random.randint(1000,999999)
            curs.execute("SELECT * from tickets where tno ="+str(ticket_no))
            rows = curs.fetchall()
            if rows :
                ticket_no = random.randint(1000,999999)
            curs.execute("SELECT name from passengers where email = "+user_email)
            rows = curs.fetchall()
            user_name = rows[0][0]
            user_name = "'"+user_name+"'"
            curs.execute("SELECT distinct price from available_flights where flightno ="+user_flightno+" AND fare ="+user_fare)
            rows = curs.fetchall()
            user_price = rows[0][0]
            cursInsertTicket = connection.cursor()
            cursInsertTicket.execute("INSERT INTO tickets values "+"("+str(ticket_no)+","+user_name+","+user_email+","+str(user_price)+")")
            connection.commit()
            cursInsertTicket.close()
            cursInsertBooking = connection.cursor()
            cursInsertBooking.execute("INSERT INTO BOOKINGS values "+"("+str(ticket_no)+","+user_flightno+","+user_fare+","+user_departure+","+user_seat+")")
            connection.commit()
            cursInsertBooking.close()
            #END OF INSTERTION ------------------------------------------------------                                                      
            print("Your flight has been successfully booked, your ticket number is",ticket_no)
        else:
            print("The flight you were trying to book either does not exist in our database or is already full, sorry.")
    check.close()
    curs.close()


#This function is dealing exclusively with handling the logout of the user.
def logoutFunction(connection, userEmail, userPassword):
    curs = connection.cursor()
    #Save to the database the new time, as in when they logged out.
    curs.execute("UPDATE users set last_login = SYSDATE where email = " + "'" + 
        userEmail + "'" + " and pass = " + "'" + userPassword + "'" )
    connection.commit()
    print("LOGGED OUT")
    print("Saved time of logoff into database!")
    return (True)    
    
    
#The arrival time of a flight may be modified from this function.
def recordFlightArrival(airLineAgent, connection):
    #Just in case, block non-airline agents from accessing this.
    if airLineAgent == False:
        print("Only airline agents may use this function!") 
        return

    #Now if they are actually a airline agent they proceed....
    print("RECORD FLIGHT ARRIVAL")      
    print("Please enter the flightnumber you want the value changed!")
    print("EXAMPLE: AC154")
    flightDepartureInputFNo = input("Enter flightnumber here: ") 
    print("Please enter the EXPECTED departure date/time(NOT the actual one!)!")
    print("Please follow the format: ") 
    print("EXAMPLE: 01-OCT-15 ")
    flightDepartureInputDep = input("Enter EXPECTED departure date here: ")
    print("Please enter the ACTUAL ARRIVAL TIME HERE!")
    print("Format day-month-year (FOLLOW IT PLEASE!)")
    print("EXAMPLE: 01-OCT-15") 
    fullTimeStringArrival = input("Please enter here FORMAT PLEASE!")

    curs = connection.cursor()
    #Save to the database the new time, as in when they logged out.
    curs.execute("UPDATE sch_flights set act_arr_time = " + "to_date('" + 
        fullTimeStringArrival + "', 'DD-Mon-YYYY' )" + 
        " where flightno = " + "'" + flightDepartureInputFNo + "'" +
        " and dep_date = " +"to_date('" + flightDepartureInputDep + "', 'DD-Mon-YYYY' )")   

    connection.commit() #save the database state permanently!!!!!!!1
    print("Edited value for DEPARTURE put into database! Thank you! :)")
  
  
#The departure time of a flight may be modified from this function.  
def recordFlightDeparture(airLineAgent, connection):
    #Block non-airline agents from accessing this.
    if airLineAgent == False:
        print("Only airline agents may use this function!")
        return
    
    #Now if they are actually a airline agent they proceed....
    print("RECORD FLIGHT DEPARTURE") 
    print("Please enter the flightnumber you want the value changed!")
    print("EXAMPLE: AC154")
    flightDepartureInputFNo = input("Enter flightnumber here: ") 
    print("Please enter the EXPECTED departure date (NOT the actual one!)!")
    print("Please follow the format: ") 
    print("EXAMPLE: 01-OCT-15")
    flightDepartureInputDep = input("Enter EXPECTED departure date here: ")
    print("Please enter the ACTUAL DEPARTURE TIME HERE!")
    print("Format (FOLLOIW IT PLEASE!!!!!!!!)")
    print("dd-month-year")
    print("EXAMPLE: 01-OCT-15") 
    fullTimeStringDeparture = input("Please enter here FORMAT PLEASE!")

    curs = connection.cursor()
    #Save to the database the new time, as in when they logged out.
    curs.execute("UPDATE sch_flights set act_dep_time = " + "to_date('" + 
        fullTimeStringDeparture + "', 'DD-Mon-YYYY' )" + 
        " where flightno = " + "'" + flightDepartureInputFNo + "'" +
        " and dep_date = " +"to_date('" + flightDepartureInputDep + "', 'DD-Mon-YYYY' )")   

    connection.commit() #save the database state permanently!!!!!!!1
    print("Edited value for DEPARTURE put into database! Thank you! :)")


    

        

#Main method is located HERE!
#The main method is responsible for creating all of the connections and 
#other features of the program.
#The main method is going to coordinate various larger functions
#such as the login screen and the main menu, and it will weave variables
#through them. 
#Furthermore upon completion of the program the main function (this) will be
#reponsible for closing all of the connections! 
def main():
    #Initialize useful boolean flag.
    exitCommand = False

    #Obtain the username using a fancy method.
    user = input("Username [%s]: " % getpass.getuser())
    if not user:
            user=getpass.getuser()
    #Obtain the password using a fancy method.
    pw = getpass.getpass()
    #Create a string to connect to the database! USING the user/pass.
    conString=''+user+'/' + pw +'@gwynne.cs.ualberta.ca:1521/CRS'

    #Try block in order to connect to the database.
    try:
        # Establish a connection in Python
        connection = cx_Oracle.connect(conString)

        #creates the view table of available flights upon connection
        create_available_view(connection)
        create_good_connections(connection)
        #user login stuff here
        (loginSuccess, userEmail, userPassword, 
            airLineAgent) = loginMenu(connection)
        if loginSuccess == False:
            exitCommand = True
            print("Application closed, no successful login attempt.")
        #Allow constant repetition of the main menu for the user.
        while exitCommand != True:
            exitCommand = mainMenu(connection, userEmail, userPassword, 
                airLineAgent)
        connection.close() #We are finished, now end connection.

    #This is an elegant way of handling the errors where we are informed
    #through the terminal screen on what is going on.
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print( sys.stderr, "Oracle code:", error.code)
        print( sys.stderr, "Oracle message:", error.message)
        
#This notation forces the main method to be called.
if __name__ == "__main__":
    main()
