# Hotel Reservation System

## **Overview**

This is a **database-connected hotel reservation system** built using **Python** and **MySQL**.
It allows users to **view available rooms, make reservations, cancel bookings, and generate revenue reports**

---

## Features

- **View room availability and rates** (sorted by popularity)
- **Make new reservations** with **smart recommendations** for alternative rooms/dates if fully booked
- **Cancel reservations** by providing a reservation code
- **Search for existing reservations** using flexible filters (name, date, room code, etc.)
- **Generate revenue reports** (monthly and yearly breakdown of room earnings)
- **Prevent SQL injection attacks** with safe query execution

---

## Setup Instructions

### 1) Clone the Repository

Run the following command in your terminal:

```sh
git clone https://github.com/jhueyy/hotel-reservation.git
cd hotel-reservation
```

### 2) Install Dependencies

This project requires Python 3 and mysql-connector-python. Install dependencies using:

```sh
pip install -r requirements.txt
```

### 3) Configure Database Credentials

#### **For Mac/Linux (Terminal)**

Run these commands in your terminal **before running the application**:

```sh
export DB_HOST="your_host"
export DB_USER="your_user"
export DB_PASS="your_password"
export DB_NAME="hotel_reservation"
```

#### **For Windows (Command Prompt)**

```sh
set DB_HOST=your_host
set DB_USER=your_user
set DB_PASS=your_password
set DB_NAME=hotel_reservation
```

### 4) Start the application

```sh
python main.py
```

## Usage Instructions

Run the program (python main.py).
Select from the menu:

#### **[1] View Rooms & Rates**

- Displays all rooms, sorted by **popularity (days occupied in the last 180 days)**.
- Shows **base price, max occupancy, and decor**.

#### **[2] Make a Reservation**

- Enter guest details, room preference, and check-in/check-out dates.
- **If the preferred room is unavailable, the system suggests 5 alternative rooms** based on **similar features and closest available dates**.

#### **[3] Cancel a Reservation**

- Enter a **reservation code** to cancel a booking.
- Removes the record from the database.

#### **[4] Search for Reservations**

- Search by **name, date range, room code, or reservation code**.
- **Overlapping reservations** are included in search results.

#### **[5] Generate Revenue Report**

- Displays **monthly revenue per room**, with **total yearly earnings**.
- Revenue for **multi-month reservations is computed per day** to ensure accurate monthly distribution.

## Contact

- **Jake Huey** – [jahuey@calpoly.edu](mailto:jahuey@calpoly.edu)
