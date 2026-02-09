from fastapi import FastAPI, HTTPException
from datetime import date, time
from typing import List, Dict

app = FastAPI()

class Table:
    def __init__(self, table_id: int, capacity: int, price: float):
        self.table_id = table_id
        self.capacity = capacity
        self.price = price

class Place:
    def __init__(self):
        self.tables = [
            Table(1, 2, 500),
            Table(2, 4, 1000),
            Table(3, 6, 1500)
        ]

    def checkAvailability(self, guests: int) -> List[Table]:
        return [t for t in self.tables if t.capacity >= guests]

class Cart:
    def __init__(self):
        self.carts: Dict[int, dict] = {} 

    def previewCost(self, user_id: int, table: Table):
        total = table.price

        cost_info = {
            "table_id": table.table_id,
            "table_price": table.price,
            "total_price": total
        }

        self.carts[user_id] = cost_info
        return cost_info

    def getCart(self, user_id: int):
        return self.carts.get(user_id)

    def clearCart(self, user_id: int):
        if user_id in self.carts:
            del self.carts[user_id]

class RoomReservation:
    def __init__(self):
        self.reservations = []

    def isTableBooked(self, table_id: int, reserve_date: date, reserve_time: time) -> bool:
        return any(
            r for r in self.reservations
            if r["table_id"] == table_id
            and r["date"] == reserve_date
            and r["time"] == reserve_time
        )

    def createReservation(self, user_id: int, table_id: int, reserve_date: date, reserve_time: time, cost_info: dict):
        reservation = {
            "reservation_id": len(self.reservations) + 1,
            "customer_id": user_id,
            "table_id": table_id,
            "date": reserve_date,
            "time": reserve_time,
            "cost": cost_info
        }
        self.reservations.append(reservation)
        return reservation

class Bar:
    def __init__(self):
        self.place = Place()
        self.room_reservation = RoomReservation()
        self.cart = Cart()

    def searchTable(self, guests: int, reserve_date: date, reserve_time: time):
        suitable_tables = self.place.checkAvailability(guests)
        return [
            t for t in suitable_tables
            if not self.room_reservation.isTableBooked(t.table_id, reserve_date, reserve_time)
        ]

    def previewReservationCost(self, user_id: int, table_id: int):
        table = next((t for t in self.place.tables if t.table_id == table_id), None)
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        return self.cart.previewCost(user_id, table)

    def reserveTable(self, user_id: int, table_id: int, reserve_date: date, reserve_time: time):
        if self.room_reservation.isTableBooked(table_id, reserve_date, reserve_time):
            raise HTTPException(status_code=400, detail="Table already booked")

        cost_info = self.cart.getCart(user_id)
        if not cost_info:
            raise HTTPException(status_code=400, detail="Cart is empty. Preview cost first.")

        reservation = self.room_reservation.createReservation(
            user_id, table_id, reserve_date, reserve_time, cost_info
        )

        self.cart.clearCart(user_id)
        return reservation


bar = Bar()

@app.get("/tables/search")
def search_table(guests: int, date: date, time: time):
    available = bar.searchTable(guests, date, time)
    return {
        "available_tables": [
            {"table_id": t.table_id, "capacity": t.capacity, "price": t.price}
            for t in available
        ]
    }

@app.post("/cart/preview")
def preview_cart(user_id: int, table_id: int):
    cost = bar.previewReservationCost(user_id, table_id)
    return {"cart_preview": cost}

@app.get("/cart")
def get_cart(user_id: int):
    cart = bar.cart.getCart(user_id)
    if not cart:
        return {"message": "Cart is empty"}
    return {"cart": cart}

@app.post("/tables/reserve")
def reserve_table(user_id: int, table_id: int, date: date, time: time):
    reservation = bar.reserveTable(user_id, table_id, date, time)
    return {"message": "Reservation successful", "data": reservation}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
