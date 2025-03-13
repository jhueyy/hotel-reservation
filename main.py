import datetime
from queries import generate_revenue_report, get_all_rooms, check_room_availability, get_room_details, make_reservation, cancel_reservation, search_reservations, check_reservation_exists, cancel_reservation, find_alternative_rooms, get_room_price

# Lists all available rooms along with their details
def display_menu():
    print("\n Hotel Reservation System")
    print("[1] View Rooms & Rates")
    print("[2] Make a Reservation")
    print("[3] Cancel a Reservation")
    print("[4] Search Reservations") 
    print("[5] Revenue Report") 
    print("[6] Exit")

# Lists all available rooms along with their details
def list_rooms():
    rooms = get_all_rooms()
    if rooms:
        print("\nAvailable Rooms (Sorted by Popularity):")
        for room in rooms:
            print(f"\n{room['RoomCode']} - {room['RoomName']}")
            print(f"- Beds: {room['Beds']}")
            print(f"- Type: {room['bedType']}")
            print(f"- Price: ${room['basePrice']}")
            print(f"- Popularity: {room['popularity_score']:.2f}")
            print(f"- Next Check-in: {room['next_available_checkin']}")
            print(f"- Last Stay: {room['last_stay_length']} days (Checked out on {room['last_checkout_date']})")
    else:
        print("No rooms available!")




# Handles the booking process, including finding available rooms and making a reservation
def book_room():
    print("\nBooking a Room")
    
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    room_code = input("Enter room code (or 'Any' for no preference): ").strip()
    bed_type = input("Desired bed type (or 'Any' for no preference): ").strip()
    check_in = input("Enter check-in date (YYYY-MM-DD): ")
    check_out = input("Enter check-out date (YYYY-MM-DD): ")
    
    adults = input("Number of adults: ")
    while not adults.isdigit():
        print("Invalid input. Please enter a valid number.")
        adults = input("Number of adults: ")
    adults = int(adults)

    children = input("Number of children: ")
    while not children.isdigit():
        print("Invalid input. Please enter a valid number.")
        children = input("Number of children: ")
    children = int(children)

    total_guests = adults + children

    # If the user chose "Any" for room preference, find an available room
    if room_code.lower() == "any":
        available_rooms = get_all_rooms()
        matching_rooms = []

        for room in available_rooms:
            if bed_type.lower() == "any" or room["bedType"].lower() == bed_type.lower():
                if room["maxOcc"] >= total_guests:
                    matching_rooms.append(room)

        if len(matching_rooms) == 0:
            print("No rooms available matching your preference.")
            return

        print("\nMatching Available Rooms:")
        count = 0
        for room in matching_rooms:
            print(f"{count + 1}. {room['RoomCode']} - {room['RoomName']} | Beds: {room['Beds']} | Type: {room['bedType']} | Max Occupancy: {room['maxOcc']} | Price: ${room['basePrice']}")
            count += 1
            if count == 5:  # Show up to 5 options
                break

        choice = input("Enter the option number to book (or press Enter to cancel): ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(matching_rooms):
                room_code = matching_rooms[choice - 1]["RoomCode"]
            else:
                print("Invalid choice. Booking cancelled.")
                return
        else:
            print("Booking cancelled.")
            return

    # Check availability of selected room
    if not check_room_availability(room_code, check_in, check_out):
        print(f"Room {room_code} is not available for the selected dates.")

        # Suggest alternative rooms
        alternatives = find_alternative_rooms(check_in, check_out, total_guests, bed_type)

        if len(alternatives) > 0:
            print("\nSuggested Alternative Rooms:")

            for alt in alternatives:
                if 'RoomName' in alt: 
                    next_available = alt.get('NextAvailableFrom', 'Available Now')
                    print(f"{alt['RoomCode']} - {alt['RoomName']} | {alt['bedType']} | Max: {alt['maxOcc']} | ${alt['basePrice']} (Next Available: {next_available})")
                else:  # Next available room (fetch full details)
                    room_details = get_room_details(alt['Room'])  # Fetch room details
                    if room_details:
                        print(f"{room_details['RoomCode']} - {room_details['RoomName']} | {room_details['bedType']} | Max: {room_details['maxOcc']} | ${room_details['basePrice']} (Next Available: {alt['NextAvailableFrom']})")

        return  # Stop function execution if room isn't available

    # Fetch room details and price
    room_details = get_room_details(room_code)
    rate = get_room_price(room_code)

    # Calculate total cost
    total_cost = calculate_total_cost(check_in, check_out, rate)

    # Make the reservation
    success = make_reservation(room_code, check_in, check_out, first_name, last_name, adults, children, rate)
    
    if success:
        # Display confirmation screen
        print("\nReservation Confirmed!")
        print(f"Guest Name: {first_name} {last_name}")
        print(f"Room: {room_details['RoomCode']} - {room_details['RoomName']}")
        print(f"Bed Type: {room_details['bedType']}")
        print(f"Check-in Date: {check_in}")
        print(f"Check-out Date: {check_out}")
        print(f"Number of Adults: {adults}")
        print(f"Number of Children: {children}")
        print(f"Total Cost: ${total_cost:.2f}")
    else:
        print("Reservation failed.")


# Function to calculate total cost based on weekdays and weekends
def calculate_total_cost(check_in, check_out, base_rate):
    check_in_date = datetime.datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.datetime.strptime(check_out, "%Y-%m-%d")
    
    total_cost = 0
    current_date = check_in_date

    while current_date < check_out_date:
        if current_date.weekday() in [5, 6]:  # Saturday (5) or Sunday (6)
            total_cost += base_rate * 1.10  # 110% for weekends
        else:
            total_cost += base_rate  # Base rate for weekdays
        current_date += datetime.timedelta(days=1)

    return total_cost





# Cancels an existing reservation based on the reservation code
def cancel_booking():
    reservation_code = input("Enter your reservation code: ").strip()

    # Verify reservation exists
    if not check_reservation_exists(reservation_code):
        print("No reservation found with that code.")
        return
    
    # Confirm cancellation
    confirm = input(f"Are you sure you want to cancel reservation {reservation_code}? (Y/N): ").strip().lower()
    
    if confirm == "y":
        if cancel_reservation(reservation_code):  # Step 3: Delete reservation
            print(f"Reservation {reservation_code} has been canceled!")
        else:
            print("Cancellation failed. Please try again.")
    else:
        print("Cancellation aborted.")




# Searches for reservations based on user-provided criteria
def search_bookings():
    print("\nSearch Reservations (Leave blank to skip a field)")
    reservation_code = input("Reservation Code: ").strip()
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    start_date = input("Start Date (YYYY-MM-DD): ").strip() or None
    end_date = input("End Date (YYYY-MM-DD): ").strip() or None
    room_code = input("Room Code: ").strip()

    results = search_reservations(reservation_code, first_name, last_name, start_date, end_date, room_code)

    if results:
        print("\nMatching Reservations:")
        print("-" * 100)
        for res in results:
            print(f"Reservation Code: {res['CODE']} | Guest: {res['FirstName']} {res['LastName']} | Room: {res['Room']} ({res['RoomName']})")
            print(f"Check-in: {res['CheckIn']} | Check-out: {res['Checkout']} | Rate: ${res['Rate']}")
            print(f"Guests: {res['Adults']} adults, {res['Kids']} children")
            print("-" * 100)
    else:
        print("No reservations found.")


        

# Generates and displays a revenue report for each room, grouped by month
def show_revenue_report():
    revenue_data = generate_revenue_report()
    if revenue_data:
        revenue_data.sort(key=lambda x: x["Total"], reverse=True)
        print("\nRevenue Report (Per Room)")
        
        # Column Headers
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        header = f"{'Room': <6} | " + " | ".join(f"{month:^8}" for month in months) + " |   Total"
        print(header)
        print("-" * len(header))  

        # Initialize total values
        total_monthly = [0] * 12
        total_yearly = 0

        for room in revenue_data:
            # Round monthly revenue and total
            monthly_revenue = [round(room.get(month, 0)) for month in range(1, 13)]
            yearly_revenue = round(room["Total"])

            print(f"{room['Room']: <6} | " + " | ".join(f"$ {rev:>6}" for rev in monthly_revenue) + f" | $ {yearly_revenue:>6}")

            # Accumulate totals
            total_monthly = [sum(x) for x in zip(total_monthly, monthly_revenue)]
            total_yearly += yearly_revenue

        # Print totals row
        print("-" * len(header))
        print(f"{'Total': <6} | " + " | ".join(f"$ {rev:>6}" for rev in total_monthly) + f" | $ {total_yearly:>6}")

    else:
        print("No revenue data available.")





def main():
    print("Starting Hotel Reservation System...")
    while True:
        display_menu()
        choice = input("\nEnter choice: ")
        if choice == "1": # FR1
            list_rooms()
        elif choice == "2": # FR2
            book_room()
        elif choice == "3": # FR3
            cancel_booking()
        elif choice == "4":
            search_bookings() # FR4
        elif choice == "5":
            show_revenue_report() # FR5
        elif choice == "6":
            print("Exiting Hotel Reservation System. Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
