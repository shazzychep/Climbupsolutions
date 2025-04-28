from locust import HttpUser, task, between
import random
import json

class ClimbupUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        # Login and get JWT token
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def view_availability(self):
        self.client.get("/api/availability", headers=self.headers)
    
    @task(2)
    def create_booking(self):
        booking_data = {
            "consultant_id": random.randint(1, 10),
            "slot_time": "2024-04-01T10:00:00Z",
            "service_type": "consultation"
        }
        self.client.post("/api/booking", 
                        json=booking_data,
                        headers=self.headers)
    
    @task(1)
    def process_payment(self):
        payment_data = {
            "booking_id": random.randint(1, 100),
            "amount": 100.00,
            "payment_method": "card"
        }
        self.client.post("/api/payment", 
                        json=payment_data,
                        headers=self.headers)
    
    @task(1)
    def view_bookings(self):
        self.client.get("/api/booking", headers=self.headers) 