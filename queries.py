from db import connect_db
from collections import defaultdict

# FR1: Get all rooms and their details, including popularity score, next available check-in, and last stay length
def get_all_rooms():
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
        WITH RoomUsage AS (
            SELECT
                Room AS RoomID,
                SUM(DATEDIFF(Checkout,
                    CASE 
                        WHEN CheckIn >= CURRENT_DATE - INTERVAL 180 DAY 
                        THEN CheckIn
                        ELSE CURRENT_DATE - INTERVAL 180 DAY
                    END
                )) AS TotalDaysBooked
            FROM lab7_reservations
            WHERE Checkout > CURRENT_DATE - INTERVAL 180 DAY
            GROUP BY Room
        ),
        RecentStays AS (
            SELECT 
                res1.Room AS RoomID, 
                res1.CheckIn AS LatestCheckIn, 
                res1.Checkout AS LatestCheckOut,
                DATEDIFF(res1.Checkout, res1.CheckIn) AS StayDuration
            FROM lab7_reservations res1
            WHERE res1.Checkout < CURRENT_DATE
              AND res1.Checkout = (
                  SELECT MAX(res2.Checkout)
                  FROM lab7_reservations res2
                  WHERE res2.Room = res1.Room
                    AND res2.Checkout < CURRENT_DATE
              )
        ),
        NextAvailable AS (
            SELECT 
                Room AS RoomID,
                MIN(CheckIn) AS NextCheckIn
            FROM lab7_reservations
            WHERE CheckIn > CURRENT_DATE
            GROUP BY Room
        )
        SELECT 
            r.*, 
            ROUND(IFNULL(ru.TotalDaysBooked, 0) / 180, 2) AS popularity_score,
            IFNULL(na.NextCheckIn, CURRENT_DATE) AS next_available_checkin,
            IFNULL(rs.StayDuration, 0) AS last_stay_length,
            rs.LatestCheckOut AS last_checkout_date  -- Added this field
        FROM lab7_rooms r
        LEFT JOIN RoomUsage ru ON r.RoomCode = ru.RoomID
        LEFT JOIN RecentStays rs ON r.RoomCode = rs.RoomID
        LEFT JOIN NextAvailable na ON r.RoomCode = na.RoomID
        ORDER BY popularity_score DESC;
        """
        cursor.execute(query)
        rooms = cursor.fetchall()
        conn.close()
        return rooms
    return []



# FR2: Make a reservation
def get_room_details(room_code):
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT RoomCode, RoomName, Beds, bedType, maxOcc, basePrice
        FROM lab7_rooms
        WHERE RoomCode = %s
        """
        cursor.execute(query, (room_code,))
        result = cursor.fetchone()
        conn.close()
        return result
    return None  # Return None if no details found

# FR2: Make a reservation
def make_reservation(room_code, check_in, check_out, first_name, last_name, adults, kids, rate):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        
        # Generate a unique reservation CODE
        cursor.execute("SELECT MAX(CAST(CODE AS UNSIGNED)) FROM lab7_reservations")
        max_code = cursor.fetchone()[0]
        new_code = max_code + 1 if max_code is not None else 1  # Start from 1 if empty
        
        query = """
        INSERT INTO lab7_reservations (CODE, Room, CheckIn, Checkout, Rate, LastName, FirstName, Adults, Kids)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (new_code, room_code, check_in, check_out, rate, last_name, first_name, adults, kids))
        conn.commit()
        conn.close()
        return new_code  # Return the new reservation code
    return None  # Return None if failed




# FR2: Check room availability for given dates
def check_room_availability(room_code, check_in, check_out):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT 1 FROM lab7_reservations
        WHERE Room = %s
        AND (CheckIn <= %s AND Checkout > %s)  -- Ensures no overlapping reservation
        """
        cursor.execute(query, (room_code, check_out, check_in))
        result = cursor.fetchone()
        conn.close()
        return result is None  # Returns True if available, False if occupied
    return False



# FR2: Find alternative rooms if requested room is unavailable
def find_alternative_rooms(check_in, check_out, total_guests, bed_type):
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)

        # Step 1: Try finding fully available rooms (most likely empty set)
        query = """
        SELECT r.RoomCode, r.RoomName, r.Beds, r.bedType, r.maxOcc, r.basePrice
        FROM lab7_rooms r
        LEFT JOIN lab7_reservations res 
            ON r.RoomCode = res.Room 
            AND res.CheckIn < %s 
            AND res.CheckOut > %s
        WHERE r.maxOcc >= %s  
        AND res.Room IS NULL  
        ORDER BY ABS(r.maxOcc - %s), r.basePrice ASC
        """
        cursor.execute(query, (check_out, check_in, total_guests, total_guests))
        available_rooms = cursor.fetchall()

        if available_rooms:
            conn.close()
            return available_rooms  # Step 1: Fully available rooms

        # Step 2: If no exact matches, find next available rooms
        query = """
        SELECT DISTINCT res.Room, MIN(res.CheckOut) AS NextAvailableFrom, 
        r.RoomName, r.bedType, r.maxOcc, r.basePrice
        FROM lab7_reservations res
        JOIN lab7_rooms r ON r.RoomCode = res.Room
        WHERE r.bedType = %s
        AND res.CheckOut > %s  
        GROUP BY res.Room, r.RoomName, r.bedType, r.maxOcc, r.basePrice
        ORDER BY NextAvailableFrom ASC
        LIMIT 5;

        """
        cursor.execute(query, (bed_type, check_out))
        alternative_rooms = cursor.fetchall()

        conn.close()
        return alternative_rooms  # Step 2: Show next available rooms

    return []





# FR2: Fetch the base price of a given room
def get_room_price(room_code):
    """Fetch the base price of a given room."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT basePrice FROM lab7_rooms WHERE RoomCode = %s"
        cursor.execute(query, (room_code,))
        result = cursor.fetchone()
        conn.close()
        return result["basePrice"] if result else None
    return None





# FR3: Cancel a reservation by removing it from the database
def cancel_reservation(reservation_code):
    """Deletes a reservation from the database."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = "DELETE FROM lab7_reservations WHERE CODE = %s"
        cursor.execute(query, (reservation_code,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0  # Returns True if a reservation was deleted
    return False


# FR3: Check if a reservation exists before attempting to cancel it
def check_reservation_exists(reservation_code):
    """Check if a reservation exists before attempting to cancel it."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM lab7_reservations WHERE CODE = %s"
        cursor.execute(query, (reservation_code,))
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0  # Returns True if reservation exists, False otherwise
    return False




# FR4: Search reservations based on user input criteria
def search_reservations(reservation_code="", first_name="", last_name="", start_date=None, end_date=None, room_code=""):
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT r.RoomName, res.*
        FROM lab7_reservations res
        JOIN lab7_rooms r ON res.Room = r.RoomCode
        WHERE (%s = '' OR res.CODE = %s)
        AND (%s = '' OR res.FirstName LIKE %s)
        AND (%s = '' OR res.LastName LIKE %s)
        AND (%s = '' OR res.Room LIKE %s)
        """

        params = [
            reservation_code, reservation_code,
            first_name, f"%{first_name}%",
            last_name, f"%{last_name}%",
            room_code, f"%{room_code}%"
        ]

 
        if start_date and end_date:
            query += " AND (res.CheckIn < %s AND res.Checkout > %s)"  # Overlap logic
            params.extend([end_date, start_date])  

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    return []



# FR5: Generate revenue report for each month

def generate_revenue_report():
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)

        query = """
        WITH reservations_per_month AS (
            SELECT 
                r.CODE, 
                r.Room, 
                r.Rate, 
                r.CheckIn, 
                MONTH(r.CheckIn) AS CheckInMonth, 
                r.CheckOut, 
                MONTH(r.CheckOut) AS CheckOutMonth, 
                DATEDIFF(r.CheckOut, r.CheckIn) AS NightsStayed
            FROM lab7_reservations r
            WHERE YEAR(r.CheckIn) = YEAR(CURRENT_DATE())
        ),

        same_month_stays AS (
            SELECT 
                CODE, 
                Room, 
                CheckInMonth AS Month, 
                NightsStayed, 
                Rate, 
                NightsStayed * Rate AS Revenue
            FROM reservations_per_month
            WHERE CheckInMonth = CheckOutMonth
        ),

        multi_month_stays AS (
            SELECT 
                CODE, 
                Room, 
                CheckInMonth, 
                CheckOutMonth, 
                NightsStayed, 
                Rate,
                NightsStayed - (DAYOFMONTH(CheckOut) - 1) AS CheckInMonthNights,
                (DAYOFMONTH(CheckOut) - 1) AS CheckOutMonthNights
            FROM reservations_per_month
            WHERE CheckInMonth != CheckOutMonth
        ),

        same_month_revenue AS (
            SELECT 
                Room, 
                Month, 
                SUM(Revenue) AS TotalRevenue
            FROM same_month_stays
            GROUP BY Room, Month
        ),

        multi_month_revenue AS (
            SELECT 
                Room, 
                CheckInMonth AS Month, 
                SUM(CheckInMonthNights * Rate) AS Revenue
            FROM multi_month_stays
            GROUP BY Room, CheckInMonth

            UNION ALL

            SELECT 
                Room, 
                CheckOutMonth AS Month, 
                SUM(CheckOutMonthNights * Rate) AS Revenue
            FROM multi_month_stays
            GROUP BY Room, CheckOutMonth
        ),

        final_revenue_per_room AS (
            SELECT Room, Month, SUM(TotalRevenue) AS MonthRevenue
            FROM same_month_revenue
            GROUP BY Room, Month

            UNION ALL

            SELECT Room, Month, SUM(Revenue) AS MonthRevenue
            FROM multi_month_revenue
            GROUP BY Room, Month
        )

        SELECT * 
        FROM final_revenue_per_room
        ORDER BY Room, Month;
        """

        cursor.execute(query)
        reservations = cursor.fetchall()
        conn.close()

        revenue_per_room = defaultdict(lambda: defaultdict(float))  

        for res in reservations:
            room = res["Room"]
            month = res["Month"]
            revenue = float(res["MonthRevenue"])

            revenue_per_room[room][month] += revenue  

        revenue_report = []
        for room, revenue in sorted(revenue_per_room.items()):
            room_data = {
                "Room": room,
                **{month: revenue.get(month, 0) for month in range(1, 13)},
                "Total": sum(revenue.values())
            }
            revenue_report.append(room_data)

        return revenue_report
    return []





