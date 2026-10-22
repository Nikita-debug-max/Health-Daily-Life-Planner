
import requests

BASE_URL = "http://127.0.0.1:5000"

# Use the same test account as test_auth.py
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
        print("Login failed. Check your test account details.")
        raise SystemExit

    # 2. Add a task
    print("\n--- ADD TASK ---")
    response = client.post(
        f"{BASE_URL}/api/tasks",
        json={
            "title": "Complete Python assignment",
            "description": "Test task for my project",
            "due_date": "2026-10-25",
            "priority": "high"
        }
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    if response.status_code != 201:
        print("Task creation failed. Stopping the test.")
        raise SystemExit

    task_id = response.json()["id"]

    # 3. View tasks
    print("\n--- VIEW TASKS ---")
    response = client.get(f"{BASE_URL}/api/tasks")
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 4. Mark the task complete
    print("\n--- COMPLETE TASK ---")
    response = client.patch(
        f"{BASE_URL}/api/tasks/{task_id}/complete",
        json={"is_completed": True}
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 5. Delete the test task
    print("\n--- DELETE TASK ---")
    response = client.delete(
        f"{BASE_URL}/api/tasks/{task_id}"
    )
    print("Status:", response.status_code)
    print("Response:", response.json())

    # 6. Confirm the task was deleted
    print("\n--- VERIFY TASK DELETION ---")
    response = client.get(f"{BASE_URL}/api/tasks")
    print("Status:", response.status_code)
    print("Response:", response.json())

    print("\n--- TASK TEST FINISHED ---")
