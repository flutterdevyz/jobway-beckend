from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_admin_user
from app.models.user import User, UserRole

# Mock the admin dependency
def mock_admin_user():
    return User(id=1, phone_number="Muhammadsodiq", role=UserRole.admin, is_active=True)

app.dependency_overrides[get_current_admin_user] = mock_admin_user

client = TestClient(app)

def test_admin_notifications():
    print("Testing GET /api/admin/notifications...")
    try:
        response = client.get("/api/admin/notifications")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error during request: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_notifications()
