
from eve import Eve
from concurrent.futures import ThreadPoolExecutor
import logging
import time


logging.basicConfig(level=logging.INFO)
executor = ThreadPoolExecutor(max_workers=10)

app = Eve()


def _insert_booking(booking):
    time.sleep(3)
    logging.info(f"booking: {booking}", flush=True)
    booking["status"] = "PROCESSED"


def insert_bookings(bookings):
    for booking in bookings:
        booking["status"] = "CREATED"
        executor.submit(_insert_booking, booking=booking)


app.on_insert_bookings += insert_bookings

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
