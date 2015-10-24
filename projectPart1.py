import sys
import cx_Oracle # the package used for accessing Oracle in Python
import getpass # the package for getting password from user without displaying it

def loginMenu():
    #INITIAL SCREEN FOR SCREENING NEW OR OLD USERS.
    loginMenu = True
    oldUser = False
    newUser = False
    loginOptions = {}
    loginOptions['1'] = "Already Registered"
    loginOptions['2'] = "Not Already Registered"
    
    while loginMenu == True:
    
        print("~~~LOGGIN SCREEN:~~~\nAre you registered yet or not?\n")
        for eachOption in loginOptions:
            print (eachOption, loginOptions[eachOption])
    
        loginMenuSelection = input("Choose your path: ")
        
        if loginMenuSelection == '1':
            print("GO TO USERNAME AND PASSWORD PART!")
            oldUser = True
        if loginMenuSelection == '2':
            print("GO TO NEW REGISTRATION PAGE!")
            newUser = True
            
            #THIS IS GOING TO BE THE NEW USER SCREEN!
        if newUser == True:
            print("YOU ARE A PEASANT. REGISTER.")
            newUserName = input("Give me your username!: ")
            newUserPass = input("Give me your password!: ")
            print("CONGRATS ON JOINING THE FUN!")
            loginMenu = False
            return
        
        if oldUser == True:
            print("Okay we've got you, now give me your username!")
            oldUserName = input("Give me your username!: ")
            oldUserPass = input("Give me your password!: ")
            print("Welcome back!")
            loginMenu = False     
            return
        
    print("K so we broke out of that shit")

def mainMenu(connection):
    #Now we have that main menu of a trillion various options as requested.
    #Initialize all the things.

    mainMenu = True
    mainMenuOptions = {} #empty dict
    isAirlineAgent = False #THIS CAN BE TRUE OPENING MORE OPTIONS!
    mainMenuOptions['1'] = "Search for flights."
    mainMenuOptions['2'] = "Make a booking."
    mainMenuOptions['3'] = "List exiting bookings."
    mainMenuOptions['4'] = "Cancel a booking."
    mainMenuOptions['5'] = "Logout."
    mainMenuOptions['6'] = "AIRLINE AGENTS ONLY: Record a flight departure."
    mainMenuOptions['7'] = "AIRLINE AGENTS ONLY: Record a flight arrival."
    while mainMenu == True:
        print("\n")
        print("Welcome to the main screen that will decide your fates")
        for eachOption in mainMenuOptions:
            print (eachOption, mainMenuOptions[eachOption])
    
        
        mainMenuSelection = input("Tell me which option you want: ")
        if mainMenuSelection == '1':
            searchForFlights(connection)
    
            
        if mainMenuSelection == '2':
            makeBookingOption(user,pw)
    
        if mainMenuSelection == '3':
            listExitingBookings(user,pw)
    
            
        if mainMenuSelection == '4':
            cancelABooking(user,pw)
    
            
        if mainMenuSelection == '5':
            logoutConfirm = logoutFunction()
            return logoutConfirm
            
        if mainMenuSelection == '6':
            recordFlightDeparture(isAirlineAgent)

        
        if mainMenuSelection == '7':
            recordFlightArrival(isAirlineAgent)
    


#All of the functions called upon by the main menu. (All 7 options!) 
def searchForFlights(connection):
    # prompt user for source, destination and departure date
    curs = connection.cursor()
    print("SEARCH FOR FLIGHTS OPTION BEGIN")
    input_source = input("Enter source: ")
    input_destination = input("Enter destination: ")
    flight_departure = input("Enter departure date: ")
    #sql statements for case insensitivity
    curs.execute("alter session set NLS_COMP=LINGUISTIC")
    curs.execute("alter session set NLS_SORT=BINARY_CI")

    #searching for airports if the user didn't give a 3 letter airport code
    if len(input_source) > 3 :
        curs.execute("SELECT * from AIRPORTS where city ="+"'"+input_source+"'" + " or name LIKE '%"+input_source+"%'" )
        # executing a query
        # get all data and print it
        rows = curs.fetchall()
        for row in rows:
            print(row)

    curs.close()

def listExitingBookings():
    print("LIST EXITING BOOKINGS")  
    
def cancelABooking():
    print("CANCEL A BOOKING") 
    
def makeBookingOption():
    print("MAKE A BOOKING OPTION")
    

def logoutFunction():
    print("LOG OUT")
    print("Saved time of logoff!")
    return (True)    
    
    
    
def recordFlightArrival(isAirlineAgent):
    #Block non-airline agents from accessing this.
    if isAirlineAgent == False:
        print("You do NOT get to use this option! Sorry, not sorry!") 
        return

    #Now if they are actually a airline agent they proceed....
    print("RECORD FLIGHT ARRIVAL")        
    
def recordFlightDeparture(isAirlineAgent):
    #Block non-airline agents from accessing this.
    if isAirlineAgent == False:
        print("You do NOT get to use this option! Sorry, not sorry!")
        return
    
    #Now if they are actually a airline agent they proceed....
    print("RECORD FLIGHT DEPARTURE")  
        

#Main method is located HERE!
def main():

    exitCommand = False

    #takes and stores sql info from user
    # get username
    user = input("Username [%s]: " % getpass.getuser())
    if not user:
            user=getpass.getuser()
    
    # get password
    pw = getpass.getpass()
    conString=''+user+'/' + pw +'@gwynne.cs.ualberta.ca:1521/CRS'

    try:
        # Establish a connection in Python
        connection = cx_Oracle.connect(conString)
        #user login stuff here
        loginMenu()
        #Allow constant repetition of the main menu for the user.
        while exitCommand != True:
            exitCommand = mainMenu(connection)
        connection.close()

    #if sql id or pw is incorrect it breaks
    except cx_Oracle.DatabaseError as exc:
        error, = exc.args
        print( sys.stderr, "Oracle code:", error.code)
        print( sys.stderr, "Oracle message:", error.message)



        

if __name__ == "__main__":
    main()
    
    