"""
 Apache Airlines - Seat Booking System (PART A)
Module      : FC723 - Programming Theory
Assignment  : Project 1 - Part A, Task 4 & 5
Author      : P489993

DESCRIPTION
-----------
This program manages seat bookings for a Burak757 aircraft. The aircraft
layout is 80 rows (1-80) and 6 columns (A-F). Column layout per row:

    A  B  C   X   D  E  F
    (seats)  (aisle)  (seats)

Rows 77-78 in columns D and E are reserved for STORAGE ("S") and cannot
be booked. Column "X" is not a real seat column. it represents the
aisle and is skipped when the seat map is built.

Each seat can be in one of the following states, stored in a dictionary
keyed by seat id (e.g. "12A"):
    "F"  -> Free        (available to book)
    "R"  -> Reserved     (already booked)
    "X"  -> Aisle        (never booked)
    "S"  -> Storage area (never booked)

The program presents a text menu that stays on screen until the user
chooses to exit (Task 4). Task 5 adds one extra feature not requested
in the original brief: searching for a booking by seat, and a simple
"free-seat count" summary, to demonstrate an enhancement a real airline
booking system would need. All functions are documented with docstrings
so that this file can later be used to auto-generate documentation
(e.g. with pydoc / Sphinx).

"""

import string

# Configuration constants
 
TOTAL_ROWS = 80                       # Rows 1 - 80
SEAT_COLUMNS = ["A", "B", "C", "D", "E", "F"]   # Real seat columns
STORAGE_ROWS = {77, 78}               # Rows where D & E are storage
STORAGE_COLUMNS = {"D", "E"}          # Columns affected by storage rows


def build_seat_map():
    """
    Build and return the initial seat map as a dictionary.

    Returns
    -------
    dict[str, str]
        Keys are seat identifiers such as "1A", "45C", "80F".
        Values are one of "F" (free) or "S" (storage - never bookable).

    Notes
    -----
    The aisle ("X") is a visual/layout marker only. Because it does not
    correspond to a bookable location, it is not stored as a dictionary
    entry, it is instead inserted only when the map is printed to the
    screen (see display_seat_map()).
    """
    seat_map = {}
    for row in range(1, TOTAL_ROWS + 1):
        for col in SEAT_COLUMNS:
            seat_id = f"{row}{col}"
            if row in STORAGE_ROWS and col in STORAGE_COLUMNS:
                seat_map[seat_id] = "S"      # storage - not bookable
            else:
                seat_map[seat_id] = "F"      # free - bookable
    return seat_map


def parse_seat_input(raw_input):
    """
    Validate and normalise a seat identifier typed by the user.

    Parameters
    ----------
    raw_input : str
        Raw text entered by the user, e.g. "12a", " 45C ".

    Returns
    -------
    str or None
        The normalised seat id (e.g. "12A") if the input has a valid
        format (1-80 followed by A-F), otherwise None.
    """
    raw_input = raw_input.strip().upper()
    if len(raw_input) < 2:
        return None

    # Split into the numeric row part and the trailing letter column part
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


def check_availability(seat_map):
    """
    Task 4, Option 1: Check whether a specific seat is available.

    Prompts the user for a seat, validates it, then reports whether the
    seat is Free, Reserved, or unavailable (aisle/storage/out of range).
    """
    raw = input("Enter seat to check (e.g. 12A): ")
    seat_id = parse_seat_input(raw)

    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get(seat_id)
    if status == "F":
        print(f"Seat {seat_id} is FREE.\n")
    elif status == "R":
        print(f"Seat {seat_id} is already RESERVED.\n")
    elif status == "S":
        print(f"Seat {seat_id} is a STORAGE AREA and cannot be booked.\n")
    else:
        print(f"Seat {seat_id} does not exist.\n")


def book_seat(seat_map):
    """
    Task 4, Option 2: Book a seat.

    A seat can only be booked if its current status is "F" (free).
    On success the seat status is changed to "R" (reserved).
    """
    raw = input("Enter seat to book (e.g. 12A): ")
    seat_id = parse_seat_input(raw)

    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get(seat_id)
    if status == "F":
        seat_map[seat_id] = "R"
        print(f"Seat {seat_id} has been successfully booked.\n")
    elif status == "R":
        print(f"Sorry, seat {seat_id} is already reserved.\n")
    elif status == "S":
        print(f"Seat {seat_id} is a storage area and cannot be booked.\n")
    else:
        print(f"Seat {seat_id} does not exist.\n")


def free_seat(seat_map):
    """
    Task 4, Option 3: Free (cancel) a previously booked seat.

    A seat can only be freed if its current status is "R" (reserved).
    On success the seat status is changed back to "F" (free).
    """
    raw = input("Enter seat to free (e.g. 12A): ")
    seat_id = parse_seat_input(raw)

    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get(seat_id)
    if status == "R":
        seat_map[seat_id] = "F"
        print(f"Seat {seat_id} has been freed.\n")
    elif status == "F":
        print(f"Seat {seat_id} is not currently booked.\n")
    elif status == "S":
        print(f"Seat {seat_id} is a storage area.\n")
    else:
        print(f"Seat {seat_id} does not exist.\n")


def display_seat_map(seat_map):
    """
    Task 4, Option 4: Show the booking status of the whole aircraft.

    Prints a grid of the entire aircraft. Columns A-C, aisle (X),
    then D-F, exactly as described in the assignment brief.
    """
    print("\n--- Apache Airlines / Burak757 Seat Map ---")
    header = "Row  A  B  C  X  D  E  F"
    print(header)
    for row in range(1, TOTAL_ROWS + 1):
        cells = []
        for col in ["A", "B", "C"]:
            cells.append(seat_map[f"{row}{col}"])
        cells.append("X")  # aisle marker
        for col in ["D", "E", "F"]:
            cells.append(seat_map[f"{row}{col}"])
        row_label = str(row).rjust(3)
        print(f"{row_label}  " + "  ".join(cells))
    print()


def count_free_seats(seat_map):
    """
    Additional feature (Task 5): count how many seats are currently free.

    This is a small but genuinely useful feature real booking systems
    provide (e.g. to show "12 seats left on this flight").
    """
    free_count = sum(1 for status in seat_map.values() if status == "F")
    reserved_count = sum(1 for status in seat_map.values() if status == "R")
    print(f"\nSeats free: {free_count}   |   Seats reserved: {reserved_count}\n")


def print_menu():
    """Display the main menu options to the user."""
    print("=" * 45)
    print(" APACHE AIRLINES - SEAT BOOKING SYSTEM")
    print("=" * 45)
    print("1. Check availability of seat")
    print("2. Book a seat")
    print("3. Free a seat")
    print("4. Show booking status")
    print("5. Show free/reserved seat count (extra feature)")
    print("6. Exit program")
    print("=" * 45)


def main():
    """
    Main program loop.

    Builds the initial seat map once, then repeatedly displays the menu
    and dispatches to the relevant function until the user chooses to
    exit (option 6).
    """
    seat_map = build_seat_map()

    while True:
        print_menu()
        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            check_availability(seat_map)
        elif choice == "2":
            book_seat(seat_map)
        elif choice == "3":
            free_seat(seat_map)
        elif choice == "4":
            display_seat_map(seat_map)
        elif choice == "5":
            count_free_seats(seat_map)
        elif choice == "6":
            print("Thank you for using Apache Airlines Seat Booking System.")
            break
        else:
            print("Invalid option, please choose a number between 1 and 6.\n")


if __name__ == "__main__":
    main()# TODO: Write tests for your package using pytest
