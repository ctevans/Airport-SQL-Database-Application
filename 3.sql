print("LIST EXITING BOOKINGS")
    curs = connection.cursor()
    cursInsert = connection.cursor()
    user_email = input("Please enter your email: ")
    user_email = "'"+user_email+"'"
    #SQL STATEMENT?                                                                                                                                                                                                
    #SELECT UNIQUE bookings.tno, passengers.name, bookings.dep_date, tickets.paid_price FROM #bookings, passengers, tickets WHERE bookings.tno=tickets.tno AND passengers.email=tickets.email AND passengers.name=t\
ickets.name;                                                                                                                                                                                                       
    #Im not sure if it is correct, is it really is this simple...?
