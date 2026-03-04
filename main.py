from fastapi import FastAPI
from typing import List
from datetime import date


# ---------- Base Class ----------
class Space:
    def __init__(self, space_id: int, capacity: int, price: float):
        self.space_id = space_id
        self.capacity = capacity
        self.price = price


class Table(Space):
    pass


class Room(Space):
    pass


# ---------- Reservation ----------
class Reservation:
    def __init__(self, user: str, space: Space, reserve_date: date):
        self.user = user
        self.space = space
        self.reserve_date = reserve_date


# ---------- Bar ----------
class Bar:
    def __init__(self):
        self.tables = [
            Table(1, 2, 500),
            Table(2, 4, 1000),
            Table(3, 6, 1500)
        ]

        self.rooms = [
            Room(101, 10, 5000),
            Room(102, 10, 5000),
            Room(103, 10, 5000),
        ]

        self.reservations: List[Reservation] = []

    # ---------- Check Availability ----------
    def check_availability(self, space: Space, reserve_date: date):
        for r in self.reservations:
            if r.space.space_id == space.space_id and r.reserve_date == reserve_date:
                return False
        return True

    # ---------- Search ----------
    def search_tables(self, reserve_date: date, guests: int):
        return [
            table for table in self.tables
            if table.capacity >= guests and self.check_availability(table, reserve_date)
        ]

    def search_rooms(self, reserve_date: date, guests: int):
        return [
            room for room in self.rooms
            if room.capacity >= guests and self.check_availability(room, reserve_date)
        ]

    # ---------- Create Reservation ----------
    def create_reservation(self, user: str, space_id: int, reserve_date: date):
        all_spaces = self.tables + self.rooms

        for space in all_spaces:
            if space.space_id == space_id:
                if self.check_availability(space, reserve_date):
                    reservation = Reservation(user, space, reserve_date)
                    self.reservations.append(reservation)
                    return reservation
        return None


# ------------------ FASTAPI ------------------

app = FastAPI()
bar = Bar()


@app.get("/tables/search")
def search_tables(guests: int, reserve_date: date):
    available = bar.search_tables(reserve_date, guests)
    return {
        "available_tables": [
            {"id": t.space_id, "capacity": t.capacity, "price": t.price}
            for t in available
        ]
    }


@app.get("/rooms/search")
def search_rooms(guests: int, reserve_date: date):
    available = bar.search_rooms(reserve_date, guests)
    return {
        "available_rooms": [
            {"id": r.space_id, "capacity": r.capacity, "price": r.price}
            for r in available
        ]
    }


@app.post("/reservation")
def reserve(user: str, space_id: int, reserve_date: date):
    reservation = bar.create_reservation(user, space_id, reserve_date)
    if reservation:
        return {"message": "Reservation successful"}
    return {"message": "Space not available"}