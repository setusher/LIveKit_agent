from livekit.agents import function_tool, Agent, RunContext
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

EXCEL_FILE = "hotel_db.xlsx"

class HotelAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a hotel booking assistant.",
            tools=[
                self.find_available_rooms, self.book_room
            ]
        )
        self.excel_file = EXCEL_FILE

    @function_tool()
    async def find_available_rooms(
        self,
        context: RunContext,
        room_type: str,
        checkin_date: str,
        checkout_date: str,
        guests: int,
        excel_file: str = EXCEL_FILE
    ) -> str:
        """
        Look up available hotel rooms by type, date, and guest count.

        Args:
            room_type: The type of room to look for (e.g., "Deluxe").
            checkin_date: The check-in date in YYYY-MM-DD format.
            checkout_date: The check-out date in YYYY-MM-DD format.
            guests: The number of guests for the booking.
            excel_file: Path to the hotel database Excel file.

        Returns:
            A string indicating available rooms or a suitable message.
        """
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
                    available.append(str(room_id))
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
        self,
        context: RunContext,
        room_id: str,
        guest_name: str,
        room_type: str,
        checkin_date: str,
        checkout_date: str,
        guests: int,
        excel_file: str = EXCEL_FILE
    ) -> str:
        """
        Book a specific hotel room for a guest if available.

        Args:
            room_id: The ID of the room to book.
            guest_name: Name of the booking guest.
            room_type: The type of room.
            checkin_date: The check-in date in YYYY-MM-DD format.
            checkout_date: The check-out date in YYYY-MM-DD format.
            guests: Number of guests.
            excel_file: Path to hotel database Excel file.

        Returns:
            A string confirming the booking status.
        """
        logging.debug("📖 book_room CALLED")
        logging.debug(
            f"Inputs => room_id={room_id}, guest_name={guest_name}, room_type={room_type}, dates={checkin_date}-{checkout_date}, guests={guests}")
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
            with pd.ExcelWriter(excel_file, mode='a', if_sheet_exists='replace') as writer:
                df_bookings.to_excel(writer, sheet_name="Bookings_Reservations", index=False)

            result = f"Booking confirmed for {guest_name} in room {room_id} from {checkin_date} to {checkout_date}."
            logging.info(result)
            return result
        except Exception as e:
            logging.error(f"Error booking room: {e}")
            return f"Error: {str(e)}"
