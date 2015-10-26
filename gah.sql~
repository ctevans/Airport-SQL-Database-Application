SELECT UNIQUE bookings.tno, passengers.name, bookings.dep_date, 
    tickets.paid_price 
    FROM bookings, passengers, tickets
    WHERE bookings.tno=tickets.tno AND passengers.email=tickets.email
    AND passengers.name = tickets.name;
