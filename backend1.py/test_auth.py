
import requests

BASE_URL = "http://127.0.0.1:5000"

# Use a fresh email each time you run this test
email = "testuser2026@example.com"
password = "TestPass123!"
name = "Test User"

with requests.Session() as client:

    # 1. Test registration
    print("\n--- REGISTER ---")
    response = client.post(
        f"{BASE_URL}/api/register",
        json={
            "name": name,
            "email": email,
            "password": password
        }
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 2. Test login
    print("\n--- LOGIN ---")
    response = client.post(
        f"{BASE_URL}/api/login",
        json={
            "email": email,
            "password": password
        }
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 3. Check the current session
    print("\n--- CURRENT USER ---")
    response = client.get(f"{BASE_URL}/api/me")
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 4. Test logout
    print("\n--- LOGOUT ---")
    response = client.post(f"{BASE_URL}/api/logout")
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 5. Verify logout
    print("\n--- CHECK AFTER LOGOUT ---")
    response = client.get(f"{BASE_URL}/api/me")
    print("Status:", response.status_code)
    print("Response:", response.json())
