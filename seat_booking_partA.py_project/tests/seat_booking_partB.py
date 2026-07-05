"""
==============================================================================
 Apache Airlines - Seat Booking System (PART B - Refactored)
==============================================================================
Module      : FC723 - Programming Theory
Assignment  : Project 1 - Part B, Task 1, 2 & 3
Author      : [Student GUID]

WHAT CHANGED FROM PART A
-------------------------
1. Instead of storing the letter "R" for a reserved seat, the seat map
   now stores an 8-character alphanumeric BOOKING REFERENCE.
2. Traveller details (passport number, first name, last name, seat row,
   seat column) are stored in an SQLite database table ("bookings")
   rather than only in memory.
3. A new function, generate_booking_reference(), creates a random,
   GUARANTEED-UNIQUE 8-character alphanumeric reference every time a
   booking is made.
4. Freeing a seat now also DELETES the corresponding row from the
   database and resets the seat back to "F".
5. A new menu option lets staff search for a booking using its
   reference number.

IMPLEMENTATION LOGIC OF THE BOOKING REFERENCE ALGORITHM
---------------------------------------------------------
generate_booking_reference() builds an 8-character string using
`random.choices()` drawn from the pool of uppercase letters A-Z and
digits 0-9 (36 possible characters per position, so 36^8 ~= 2.8 x 10^12
possible combinations -- collisions are already extremely unlikely).
To make uniqueness a GUARANTEE rather than just "very likely", the
function checks the newly generated code against every reference
already stored in the database (via `is_reference_taken()`) and, in
the rare case of a collision, discards it and generates a new one.
This loop is bounded by MAX_ATTEMPTS purely as a safety net against an
almost-full reference space, which will never realistically occur here.

DATABASE
--------
SQLite is used because it requires no server installation and stores
the whole database in a single local file (bookings.db), which is
ideal for a coursework project. The table schema is:

    CREATE TABLE bookings (
        reference       TEXT PRIMARY KEY,
        passport_number TEXT NOT NULL,
        first_name      TEXT NOT NULL,
        last_name       TEXT NOT NULL,
        seat_row        INTEGER NOT NULL,
        seat_column     TEXT NOT NULL
    );
==============================================================================
"""

import random
import sqlite3
import string

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
TOTAL_ROWS = 80
SEAT_COLUMNS = ["A", "B", "C", "D", "E", "F"]
STORAGE_ROWS = {77, 78}
STORAGE_COLUMNS = {"D", "E"}

DB_FILE = "bookings.db"
REFERENCE_LENGTH = 8
REFERENCE_ALPHABET = string.ascii_uppercase + string.digits
MAX_ATTEMPTS = 1000   # safety limit for the uniqueness-retry loop


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def init_database():
    """
    Create the SQLite database file and the 'bookings' table if they do
    not already exist. Returns an open sqlite3 connection.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            reference       TEXT PRIMARY KEY,
            passport_number TEXT NOT NULL,
            first_name      TEXT NOT NULL,
            last_name       TEXT NOT NULL,
            seat_row        INTEGER NOT NULL,
            seat_column     TEXT NOT NULL
        )
    """)
    connection.commit()
    return connection


def is_reference_taken(connection, reference):
    """Return True if `reference` already exists in the bookings table."""
    cursor = connection.cursor()
    cursor.execute("SELECT 1 FROM bookings WHERE reference = ?", (reference,))
    return cursor.fetchone() is not None


def save_booking_to_db(connection, reference, passport_number,
                        first_name, last_name, row, column):
    """Insert a new booking row into the database."""
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO bookings
            (reference, passport_number, first_name, last_name,
             seat_row, seat_column)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (reference, passport_number, first_name, last_name, row, column))
    connection.commit()


def delete_booking_from_db(connection, reference):
    """Delete a booking row from the database by its reference."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM bookings WHERE reference = ?", (reference,))
    connection.commit()


def find_booking_by_reference(connection, reference):
    """
    Look up a booking by its reference number.

    Returns
    -------
    tuple or None
        (reference, passport_number, first_name, last_name,
         seat_row, seat_column) if found, otherwise None.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM bookings WHERE reference = ?", (reference,))
    return cursor.fetchone()


# ---------------------------------------------------------------------------
# Booking reference algorithm  (Part B, Task 1)
# ---------------------------------------------------------------------------
def generate_booking_reference(connection):
    """
    Generate a random, unique 8-character alphanumeric booking reference.

    Algorithm
    ---------
    1. Randomly choose 8 characters from A-Z and 0-9 using
       random.choices() (uniform distribution, with replacement).
    2. Join them into a single 8-character string.
    3. Check the database: if this exact reference already exists,
       discard it and try again (step 1).
    4. Repeat until a reference that is NOT already in the database
       is produced, or until MAX_ATTEMPTS is reached (safety net).

    Returns
    -------
    str
        A unique 8-character alphanumeric booking reference.

    Raises
    ------
    RuntimeError
        If a unique reference could not be produced after MAX_ATTEMPTS
        tries (would only happen if the reference space were almost
        entirely exhausted, which is not realistic for this system).
    """
    for _ in range(MAX_ATTEMPTS):
        candidate = "".join(random.choices(REFERENCE_ALPHABET, k=REFERENCE_LENGTH))
        if not is_reference_taken(connection, candidate):
            return candidate
    raise RuntimeError("Unable to generate a unique booking reference.")


# ---------------------------------------------------------------------------
# Seat map helpers  (unchanged logic from Part A, reused here)
# ---------------------------------------------------------------------------
def build_seat_map():
    """Build and return the initial in-memory seat map."""
    seat_map = {}
    for row in range(1, TOTAL_ROWS + 1):
        for col in SEAT_COLUMNS:
            seat_id = f"{row}{col}"
            if row in STORAGE_ROWS and col in STORAGE_COLUMNS:
                seat_map[seat_id] = "S"
            else:
                seat_map[seat_id] = "F"
    return seat_map


def parse_seat_input(raw_input):
    """Validate and normalise a seat identifier typed by the user."""
    raw_input = raw_input.strip().upper()
    if len(raw_input) < 2:
        return None
    col = raw_input[-1]
    row_part = raw_input[:-1]
    if col not in SEAT_COLUMNS:
        return None
    if not row_part.isdigit():
        return None
    row = int(row_part)
    if row < 1 or row > TOTAL_ROWS:
        return None
    return f"{row}{col}"


def is_reserved(status):
    """
    Return True if `status` represents a reserved seat.

    In Part B, a reserved seat no longer stores the letter "R" -- it
    stores an 8-character booking reference instead. A seat is
    therefore considered reserved if its status is neither "F"
    (free), "S" (storage) nor "X" (aisle).
    """
    return status not in ("F", "S", "X")


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def check_availability(seat_map):
    """Option 1: Check whether a specific seat is available."""
    raw = input("Enter seat to check (e.g. 12A): ")
    seat_id = parse_seat_input(raw)
    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get(seat_id)
    if status == "F":
        print(f"Seat {seat_id} is FREE.\n")
    elif status == "S":
        print(f"Seat {seat_id} is a STORAGE AREA and cannot be booked.\n")
    elif is_reserved(status):
        print(f"Seat {seat_id} is RESERVED (reference: {status}).\n")
    else:
        print(f"Seat {seat_id} does not exist.\n")


def book_seat(seat_map, connection):
    """
    Option 2: Book a seat.

    Refactored for Part B: on a successful booking, a unique booking
    reference is generated and stored in the seat map (instead of
    "R"), and the traveller's details are saved to the database.
    """
    raw = input("Enter seat to book (e.g. 12A): ")
    seat_id = parse_seat_input(raw)
    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get(seat_id)
    if status == "S":
        print(f"Seat {seat_id} is a storage area and cannot be booked.\n")
        return
    if status is None:
        print(f"Seat {seat_id} does not exist.\n")
        return
    if is_reserved(status):
        print(f"Sorry, seat {seat_id} is already reserved.\n")
        return

    # Seat is free -- collect traveller details
    passport_number = input("Passport number: ").strip()
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()

    reference = generate_booking_reference(connection)
    row = int("".join(ch for ch in seat_id if ch.isdigit()))
    column = seat_id[-1]

    save_booking_to_db(connection, reference, passport_number,
                        first_name, last_name, row, column)
    seat_map[seat_id] = reference

    print(f"Seat {seat_id} booked successfully. "
          f"Your booking reference is: {reference}\n")


def free_seat(seat_map, connection):
    """
    Option 3: Free a previously booked seat.

    Refactored for Part B: the booking record is also deleted from
    the database, and the seat map entry is reset to "F".
    """
    raw = input("Enter seat to free (e.g. 12A): ")
    seat_id = parse_seat_input(raw)
    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get(seat_id)
    if status == "F":
        print(f"Seat {seat_id} is not currently booked.\n")
    elif status == "S":
        print(f"Seat {seat_id} is a storage area.\n")
    elif is_reserved(status):
        delete_booking_from_db(connection, status)
        seat_map[seat_id] = "F"
        print(f"Seat {seat_id} (reference {status}) has been freed and "
              f"the booking record has been removed from the database.\n")
    else:
        print(f"Seat {seat_id} does not exist.\n")


def display_seat_map(seat_map):
    """Option 4: Show the booking status of the whole aircraft."""
    print("\n--- Apache Airlines / Burak757 Seat Map ---")
    print("Row  A  B  C  X  D  E  F   (numbers/letters other than")
    print("                            F/X/S = booking reference)")
    for row in range(1, TOTAL_ROWS + 1):
        cells = []
        for col in ["A", "B", "C"]:
            status = seat_map[f"{row}{col}"]
            cells.append(status if status in ("F", "S") else "R")
        cells.append("X")
        for col in ["D", "E", "F"]:
            status = seat_map[f"{row}{col}"]
            cells.append(status if status in ("F", "S") else "R")
        row_label = str(row).rjust(3)
        print(f"{row_label}  " + "  ".join(cells))
    print("\n(Note: 'R' shown above stands for any seat holding a unique "
          "booking reference; use option 5 to look up the actual reference.)\n")


def search_by_reference(connection):
    """
    Option 5 (extra feature from Part A, retained in Part B): search
    for a booking using its reference number and display the
    traveller's details from the database.
    """
    reference = input("Enter booking reference: ").strip().upper()
    result = find_booking_by_reference(connection, reference)
    if result is None:
        print(f"No booking found with reference {reference}.\n")
        return

    ref, passport_number, first_name, last_name, row, column = result
    print(f"\nBooking found: {ref}")
    print(f"  Passenger : {first_name} {last_name}")
    print(f"  Passport  : {passport_number}")
    print(f"  Seat      : {row}{column}\n")


def print_menu():
    """Display the main menu options to the user."""
    print("=" * 50)
    print(" APACHE AIRLINES - SEAT BOOKING SYSTEM (Part B)")
    print("=" * 50)
    print("1. Check availability of seat")
    print("2. Book a seat")
    print("3. Free a seat")
    print("4. Show booking status")
    print("5. Search booking by reference")
    print("6. Exit program")
    print("=" * 50)


def main():
    """
    Main program loop for the refactored (Part B) system.

    Builds the in-memory seat map, opens/creates the SQLite database,
    then loops over the menu until the user exits. The database
    connection is closed cleanly on exit.
    """
    seat_map = build_seat_map()
    connection = init_database()

    try:
        while True:
            print_menu()
            choice = input("Select an option (1-6): ").strip()

            if choice == "1":
                check_availability(seat_map)
            elif choice == "2":
                book_seat(seat_map, connection)
            elif choice == "3":
                free_seat(seat_map, connection)
            elif choice == "4":
                display_seat_map(seat_map)
            elif choice == "5":
                search_by_reference(connection)
            elif choice == "6":
                print("Thank you for using Apache Airlines Seat Booking System.")
                break
            else:
                print("Invalid option, please choose a number between 1 and 6.\n")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
