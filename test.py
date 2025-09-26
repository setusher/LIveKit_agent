from tools import find_available_rooms, book_room

print(find_available_rooms("Suite", "2025-10-01", "2025-10-05", 2, "hotel_db.xlsx"))
print(book_room("G011", "Aarav Sharma", "Suite", "2025-10-01", "2025-10-05", 2, "hotel_db.xlsx"))
