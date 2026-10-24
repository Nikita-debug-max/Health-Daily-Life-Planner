
import requests

BASE_URL = "http://127.0.0.1:5000"

EMAIL = "testuser2026@example.com"
PASSWORD = "TestPass123!"

with requests.Session() as client:

    # 1. Login
    print("\n--- LOGIN ---")
    response = client.post(
        f"{BASE_URL}/api/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    if response.status_code != 200:
        print("Login failed. Check your test account details.")
        raise SystemExit

    # 2. Add a test meal
    print("\n--- ADD MEAL ---")
    response = client.post(
        f"{BASE_URL}/api/meals",
        json={
            "meal_type": "breakfast",
            "meal_name": "Oats and banana",
            "meal_date": "2026-10-24",
            "notes": "Test meal"
        }
    )
    print("Status:", response.status_code)
    print("Response text:", response.text)

    if response.status_code != 201:
        print("Meal creation failed. Stopping the test.")
        raise SystemExit

    meal_id = response.json()["id"]

    # 3. View meals
    print("\n--- VIEW MEALS ---")
    response = client.get(f"{BASE_URL}/api/meals")
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 4. Edit the test meal
    print("\n--- UPDATE MEAL ---")
    response = client.put(
        f"{BASE_URL}/api/meals/{meal_id}",
        json={
            "meal_name": "Oats, banana and milk",
            "notes": "Updated test meal"
        }
    )
    print("Status:", response.status_code)
    print("Response text:", response.text)

    # 5. Delete the test meal
    print("\n--- DELETE MEAL ---")
    response = client.delete(
        f"{BASE_URL}/api/meals/{meal_id}"
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 6. Verify deletion
    print("\n--- VERIFY DELETION ---")

    response = client.get(
        f"{BASE_URL}/api/meals",
        params={"date": "2026-10-24"}
    )

    print("Status:", response.status_code)
    print("Response text:", response.text)