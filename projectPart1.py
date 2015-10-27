import sys
import cx_Oracle # the package used for accessing Oracle in Python
import getpass # the package for getting password from user without displaying it
import random


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
        for eachOption in loginOptions:
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
    mainMenuOptions['5'] = "AIRLINE AGENTS ONLY: Record a flight departure."
    mainMenuOptions['6'] = "AIRLINE AGENTS ONLY: Record a flight arrival."
    #Initialize the mainMenu where the user will be looping through until
    #We have a series of menu options to choose from.
    while mainMenu == True:
        print("\n")

        print("Welcome to the main screen. We have various options here to choose from")

        for eachOption in mainMenuOptions:
            print (eachOption, mainMenuOptions[eachOption])
    
        
        mainMenuSelection = input("Which option do you want?: ")
        if mainMenuSelection == '1':
            searchForFlights(connection)
    
            
        if mainMenuSelection == '2':
            makeBookingOption(connection)
    
        if mainMenuSelection == '3':
            listAndDeleteExitingBookings(connection)
    
            
        if mainMenuSelection == '4':
            logoutConfirm = logoutFunction(connection, userEmail, userPassword)
            return logoutConfirm
            
        if mainMenuSelection == '5':
            recordFlightDeparture(airLineAgent, connection)

        
        if mainMenuSelection == '6':
            recordFlightArrival(airLineAgent, connection)
    


#All of the functions called upon by the main menu. (All 7 options!) 
def searchForFlights(connection):
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

    #direct flight results
    curs.execute("SELECT flightno, src, dst, dep_date, seats,"
       " price FROM AVAILABLE_FLIGHTS WHERE src =" + "'" +flight_source+ "'" +
       " AND dst =" + "'" +flight_destination+ "'" + " and dep_date =" + "'" +
       flight_departure+ "'" + " and seats > 1 ORDER BY price")
    rows = curs.fetchall()
    for row in rows:
        print("|Flight Number:",row[0],"|Source Airport:",row[1],
            "|Destination Airport:",row[2],"|Departure Date:",
            row[3].strftime('%d-%b-%Y'), "|Seats Available:",row[4],
            "|Seat Price",row[5])

    curs.close()

def listAndDeleteExitingBookings(connection):
    print("VIEW AND DELETE EXISTING BOOKINGS OPTION")

    #create cursor and get info from user
    curs = connection.cursor()
    user_email = input("Please enter your email: ")
    user_email = "'"+ user_email + "'"

    #get the required info from the required tables
    curs.execute("SELECT UNIQUE bookings.tno, passengers.name, bookings.dep_date, tickets.paid_price FROM bookings, passengers, tickets WHERE bookings.tno=tickets.tno AND passengers.email=tickets.email AND passengers.name = tickets.name AND passengers.email =" + user_email)

    #get all rows, and initialize counter
    rows = curs.fetchall()
    counter=0


    for row in rows:

        #print top info bar
        if counter==0:
            print("Row number".ljust(25)+"Ticket number".ljust(25)+"Passenger name".ljust(25)+"Department date".ljust(25)+"Price".ljust(25))
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

        #recreate the view with both new tables
        create_available_view(connection)
        print("DELETE SUCCESSFULL!")
        
    #finally, close the cursor
    curs.close()

#This function is going to be dealing with the functionality of making a booking
#option. This function will 
def makeBookingOption(connection):
    curs = connection.cursor()
    cursInsert = connection.cursor()
    print("MAKE A BOOKING OPTION")
    user_email = input("Please enter your email: ")
    user_email = "'"+user_email+"'"
    curs.execute("SELECT * from passengers where email ="+user_email)
    rows = curs.fetchall()

    if rows:
        pass
    else:
        print("\nThe Email address you've entered was not part of our database")
        print("Please give us your name and your country")
        user_name = input("Please enter your name:")
        user_name = "'"+user_name+"'"
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
    user_departure = input("Enter departure date:")
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
        #INSERTING INTO BOOKINGS AND TICKETS ------------------------------------
        ticket_no = random.randint(1000,999999)
        curs.execute("SELECT * from tickets where tno ="+str(ticket_no))
        rows = curs.fetchall()
        if rows :
            ticket_no = random.randint(1000,999999)
        #curs.execute("SELECT * from available_flights where flightno = "
            #+user_flightno+" and fare = "+user_fare+" and dep_date = "
            #+user_departure)
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
        cursInsertBooking = connection.cursor()
        #print("INSERT INTO BOOKINGS values "+"("+str(ticket_no)+","+user_flightno+","+user_fare+","+user_departure+","+user_seat+")")
        cursInsertBooking.execute("INSERT INTO BOOKINGS values "+"("+str(ticket_no)+","+user_flightno+","+user_fare+","+user_departure+","+user_seat+")")
        connection.commit()
        cursInsertBooking.close()
        #END OF INSTERTION ------------------------------------------------------
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
    #Block non-airline agents from accessing this.
    if airLineAgent == False:
        print("Only airline agents may use this function!") 
        return

    #Now if they are actually a airline agent they proceed....
    print("RECORD FLIGHT ARRIVAL")        
  
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
    print("EXAMPLE: 01-OCT-15")
    flightDepartureInputDep = input("Enter expected departure date here: ")
    print("Please enter the ACTUAL DEPARTURE TIME HERE!")
    print("Format (FOLLOIW IT PLEASE!!!!!!!!)")
    print("yyyy/mm/dd hh24:mi:ss where y = year, m = month, d = day h = hour")
    print(" mi = minutes and s = seconds") 
    fullTimeStringDeparture = input("Please enter here FORMAT PLEASE!")

    curs = connection.cursor()
    #Save to the database the new time, as in when they logged out.
    curs.execute("UPDATE sch_flights set act_dep_time = " + "'" + 
        fullTimeStringDeparture + "'" + 
        " where flightno = " + "'" + flightDepartureInputFNo + "'" +
        " and dep_date = " +"'" + flightDepartureInputDep + "'")   
    print("Edited value for DEPARTURE put into database! Thank you! :)")

    connection.commit() #save the database state permanently!!!!!!!1
 

    

        

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
