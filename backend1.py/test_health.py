
import requests

BASE_URL = "http://127.0.0.1:5000"

EMAIL = "testuser2026@example.com"
PASSWORD = "TestPass123!"

with requests.Session() as client:

    # 1. Log in
    print("\n--- LOGIN ---")
    response = client.post(
        f"{BASE_URL}/api/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    if response.status_code != 200:
        print("Login failed. Check your test account.")
        raise SystemExit

    # 2. Save a health record
    print("\n--- SAVE HEALTH RECORD ---")
    response = client.post(
        f"{BASE_URL}/api/health",
        json={
            "record_date": "2026-10-22",
            "water_ml": 1800,
            "sleep_hours": 8,
            "exercise_minutes": 30,
            "steps": 5000
        }
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    if response.status_code not in (200, 201):
        print("Saving health data failed.")
        raise SystemExit

    # 3. View all health records
    print("\n--- VIEW HEALTH RECORDS ---")
    response = client.get(f"{BASE_URL}/api/health")
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 4. View the specific test date
    print("\n--- VIEW ONE DAY ---")
    response = client.get(
        f"{BASE_URL}/api/health",
        params={"date": "2026-10-22"}
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 5. Log out
    print("\n--- LOGOUT ---")
    response = client.post(f"{BASE_URL}/api/logout")
    print("Status:", response.status_code)
    print("Response:", response.json())

print("\n--- HEALTH TEST FINISHED ---")
