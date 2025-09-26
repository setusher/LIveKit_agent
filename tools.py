import pandas as pd
from livekit.agents import function_tool, RunContext
import logging
from datetime import datetime

EXCEL_FILE = "hotel_db.xlsx"


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")



@function_tool()
async def find_available_rooms(
    context: RunContext,  
    room_type: str,
    checkin_date: str,
    checkout_date: str,
    guests: int,
    excel_file: str = EXCEL_FILE
) -> str:  
    logging.debug("🔍 find_available_rooms CALLED")
    logging.debug(f"Inputs => room_type={room_type}, checkin={checkin_date}, checkout={checkout_date}, guests={guests}")
    try:
        df_rooms = pd.read_excel(excel_file, sheet_name="Rooms")
        df_bookings = pd.read_excel(excel_file, sheet_name="Bookings_Reservations")
        logging.debug(f"Loaded {len(df_rooms)} rooms and {len(df_bookings)} bookings from {excel_file}")

        checkin = pd.to_datetime(checkin_date)
        checkout = pd.to_datetime(checkout_date)

        candidate_rooms = df_rooms[
            (df_rooms["Room_Type"].str.lower() == room_type.lower()) &
            (df_rooms["Capacity"] >= guests)
        ]
        logging.debug(f"Candidate rooms count: {len(candidate_rooms)}")

        available = []
        for _, room in candidate_rooms.iterrows():
            room_id = room["Room_ID"]
            overlap = df_bookings[
                (df_bookings["Room_ID"] == room_id) &
                (df_bookings["Check_Out_Date"] > checkin) &
                (df_bookings["Check_In_Date"] < checkout)
            ]
            if overlap.empty:
                available.append(room_id)
                logging.debug(f"Room {room_id} is available")
            else:
                logging.debug(f"Room {room_id} is NOT available")

        if available:
            result = f"Available {room_type} rooms: {', '.join(available)}"
        else:
            result = f"No {room_type} rooms available between {checkin_date} and {checkout_date}."

        logging.info(result)
        return result
    except Exception as e:
        logging.error(f"Error finding rooms: {e}")
        return f"Error: {str(e)}"



@function_tool()
async def book_room(
    context: RunContext, 
    room_id: str,
    guest_name: str,
    room_type: str,
    checkin_date: str,
    checkout_date: str,
    guests: int,
    excel_file: str = EXCEL_FILE
) -> str:
    logging.debug("📖 book_room CALLED")
    logging.debug(f"Inputs => room_id={room_id}, guest_name={guest_name}, room_type={room_type}, dates={checkin_date}-{checkout_date}, guests={guests}")
    try:
        df_bookings = pd.read_excel(excel_file, sheet_name="Bookings_Reservations")

        checkin = pd.to_datetime(checkin_date)
        checkout = pd.to_datetime(checkout_date)

        overlap = df_bookings[
            (df_bookings["Room_ID"] == room_id) &
            (df_bookings["Check_Out_Date"] > checkin) &
            (df_bookings["Check_In_Date"] < checkout)
        ]
        if not overlap.empty:
            logging.warning(f"Room {room_id} already booked for {checkin_date}–{checkout_date}")
            return f"Room {room_id} is not available for the given dates."

        new_booking = {
            "Room_ID": room_id,
            "Guest_Name": guest_name,
            "Room_Type": room_type,
            "Check_In_Date": checkin,
            "Check_Out_Date": checkout,
            "Guests": guests
        }
        df_bookings = pd.concat([df_bookings, pd.DataFrame([new_booking])], ignore_index=True)
        df_bookings.to_excel(excel_file, sheet_name="Bookings_Reservations", index=False)

        result = f"Booking confirmed for {guest_name} in room {room_id} from {checkin_date} to {checkout_date}."
        logging.info(result)
        return result
    except Exception as e:
        logging.error(f"Error booking room: {e}")
        return f"Error: {str(e)}"


