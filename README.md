# Airport-SQL-Database-Application

Languages: Python 3, SQL
 
##Goals, Relevance, Purpose:

Using Python 3 and SQL the goal of this project was to create an application that can interact with an SQL database and allow a user to perform various actions with it, actions include:
-Searching for flights
-Making a booking
-List all current leaving bookings
-Cancel a booking
-A complete login system for users.
-Recording of flight arrival and departure
-Search and booking of round-trips
-Support search and booking of three connecting flight trips
-Support search and booking for parties larger than one individual.

(For detailed descriptions of what our application was expected to do, please refer to the bottom of this readme in the action named "Expected functionalities".) 

##General overview of the system:

This application is based upon the usage of the terminal window and command line within UNIX systems. This application is written in python (3.4x). To interact with the system, a user must type in a response when prompted into the command line, and then hit the enter key to submit their answer to the prompt. The application will give details to the user through statements on the terminal window. 

Image of the flow of the application
![](https://github.com/ctevans/Airport-SQL-Database-Application/blob/master/Project%201%20DIA!.png)

Part 1 – Initialization Block:
Where we initialize all the things to connect to the database. When run will connect to the database Gwynne.

Part 2 – Login, Register or Exit decision
Show in the terminal window display commands that a user can input into the terminal window for the login screen. These commands are as follows:

1 – Already registered user, proceed to login page

2 – New user, proceed to registration page

3 – Exit from the application

Entering the number, representing the decision, and then hitting enter will cause the program to accept the answer and then to move on from that point to the next step.

Part 3 – Login (for an old user / a registered user):
A registered user is going to be prompted to enter their username, and then password. 
Upon hitting the enter key at this point we will then have the database process their username and password and if they match what we have currently stored for them then we will allow them to proceed, if not they will get an error message and be returned to the login prompt.
Part 4 – Exit (from the application, before login):
This will exit the application without performing any other action. It is assumed at this point we need not maintain the data of people that are not logged in. 

Part 5 – Registration (For new users):
On this screen the user will be prompted to enter a username and a password. These (once we have the pair) will then be placed into the database. We then allow the user entry to the main menu screen.  However if the username already is in the database then we will warn the user that this is not allowed and return them to the options for login, register or exit screen.

Part 6 – Main Menu (The major part!):
After a successful login. This is going to be the part where the user is granted the ability to select what actions they desire to actually perform. The terminal window will print the list of options and then the user selects the number of the action they desire and then put it into the terminal window and hit enter and then the action is processed and has an action taken in accordance to this! This will take the user to the various functions we are specified to have.

Part 7 – The various unique functions:
This part is dedicated to all of the various functions that the user can select. From the main menu they selected an option and whatever option is selected, they will have the same similar effect. The user in any one of these options will be prompted for various series’ of information that they must supply by making a choice from a list of options or entering in information to the console and then submitting the information by hitting enter. Upon completion the system will return the desired information and then send the user back to the main menu. 
Please note: The Record a flight departure and the record a flight arrival are for airline agents ONLY. Users without the airline agent privileges will be denied access to these functions and told so upon attempt. 


## Detailed Design

Python 3.4 was used, with the intent to make the application text based. So whenever something was desired to be printed on the screen basic print statements were used. Whenever we wanted to gain user input we used the “input” python command, aside from the passwords because we used the more defensive getpass.getpass() command. 

When commanding to the databases we created a connection to gwynne.cs.ualberta.ca and then passed this connection around the program. When we actually wanted to perform some sort of action on the database we would create a cursor with it using the connection.cursor() command and evoke SQL commands using it. 

Please refer to the functional flowchart for the way that the functions interact in this program. It will help make this make more sense.

THE main function, this will initialize a host of variables such as the connection to the database and useful Booleans that will manage if the user exits the program, and if we run into a cx_Oracle error we have a block dedicated purely towards creating proper output from the terminal screen. This function evokes other functions (big ones) such as the loginMenu and then the mainMenu functions. It will shuffle essential variables like username and userpassword around through these functions as well. But the bulk of the responsibility is transferred to other functions.

loginMenu function is going to be dedicated purely towards the login screen (trapping the user in a while loop) passed the connection this will display the options the user has to login, register or exit and then through a series of Booleans dictated by the user input will then cascade down to the desired functions. Throughout the login, registration or exit process the user has a series of prompts that then interact with the database to check if the user is valid or not or if the user is actually trying to register an account that does not exist. 

Upon successful completion this function then throws the username, password and a successful or not flag to the main function. 

mainMenu: This function is going to present the user with a series of options (trapping them in yet another while loop) however this mainMenu function acts moreso as if it were a massive launchpad to other functions that handle their respective functionalities. 

## Database Schema:
You are given the following relational schema.

airports(acode, name, city, country, tzone)
flights(flightno, src, dst, dep_time, est_dur)
sch_flights(flightno, dep_date, act_dep_time, act_arr_time)
fares(fare, descr)
flight_fares(flightno, fare, limit, price, bag_allow)
users(email, pass, last_login)
passengers(email, name, country)
tickets(tno, name, email, paid_price)
bookings(tno, flightno, fare, dep_date, seat)
airline_agents(email, name)

## Expected functionalities:

1: Search for flights. A user should be able to search for flights. Your system should prompt the user for a source, a destination and a departure date. For source and destination, the user may enter an airport code or a text that can be used to find an airport code. If the entered text is not a valid airport code, your system should search for airports that have the entered text in their city or name fields (partial match is allowed) and display a list of candidates from which an airport can be selected by the user. Your search for source and destination must be case-insensitive. Your system should search for flights between the source and the destination on the given date(s) and return all those that have a seat available. The search result will include both direct flights and flights with one connection (i.e. two flights with a stop between). The result will include flight details (including flight number, source and destination airport codes, departure and arrival times), the number of stops, the layover time for non-direct flights, the price, and the number of seats at that price. The result should be sorted based on price (from the lowest to the highest); the user should also have the option to sort the result based on the number of connections (with direct flights listed first) as the primary sort criterion and the price as the secondary sort criterion.

2: Make a booking. A user should be able to select a flight (or flights when there are connections) from those returned for a search and book it. The system should get the name of the passenger and check if the name is listed in the passenger table with the user email. If not, the name and the country of the passenger should be added to the passenger table with the user email. Your system should add rows to tables bookings and tickets to indicate that the booking is done (a unique ticket number should be generated by the system). Your system can be used by multiple users at the same time and overbooking is not allowed. Therefore, before your update statements, you probably want to check if the seat is still available and place this checking and your update statements within a transaction. Finally the system should return the ticket number and a confirmation message if a ticket is issued or a descriptive message if a ticket cannot be issued for any reason.

3: List exiting bookings. A user should be able to list all his/her existing bookings. The result will be given in a list form and will include for each booking, the ticket number, the passenger name, the departure date and the price. The user should be able to select a row and get more detailed information about the booking.

4: Cancel a booking. The user should be able to select a booking from those listed under "list existing bookings" and cancel it. The proper tables should be updated to reflect the cancelation and the cancelled seat should be returned to the system and is made available for future bookings.

5: Logout. There must be an option to log out of the system. At logout, the field last_login in users is set to the current system date.
Airline agents should be able to perform all the tasks listed above and the following additional tasks:

6: Record a flight departure. After a plane takes off, the user may want to record the departure. Your system should support the task and make necessary updates such as updating the act_dep_time.

7: Record a flight arrival. After a landing, the user may want to record the arrival and your system should support the task.

8: Support search and booking of round-trips. The system should offer an option for round-trips. If this option is selected, your system will get a return date from the user, and will list the flights in both directions, sorted by the sum of the price (from lowest to the highest). The user should be able to select an option and book it.

9: Support search and booking of flights with three connecting flights. In its default setting, your system will search for flights with two connections at most. In implementing this functionality, your system should offer an option to raise this maximum to three connections. Again this is an option to be set by user when running your system and cannot be the default setting of your application.

10: Support search and booking for parties of size larger than one. There should be an option for the user to state the number of passengers. The search component of your system will only list flights that have enough seats for all party members. Both the seat pricing and the booking will be based on filling the lowest fare seats first before moving to the next fare. For example, suppose there are 2 seats available in the lowest fare and 5 seats in some higher-priced fare. For a party of size 4, your system will book those 2 lowest fare seats and another 2 seats in the next fare type that is available.
