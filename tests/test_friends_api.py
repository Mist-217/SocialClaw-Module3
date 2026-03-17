"""测试好友 API 接口"""
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.core.auth import create_access_token
from app.core.database import get_db

client = TestClient(app)


def get_auth_headers(user: User) -> dict:
    """获取认证头"""
    token = create_access_token(data={"user_id": user.user_id})
    return {"Authorization": f"Bearer {token}"}


def test_send_friend_request_api(test_db, test_user1, test_user2, test_agent1, test_agent2):
    """测试发送好友请求 API"""
    # 覆盖依赖使用测试数据库
    app.dependency_overrides[get_db] = lambda: test_db

    headers = get_auth_headers(test_user1)

    response = client.post(
        "/api/v1/friends/request",
        json={"target_agent_id": "test_agent_2"},
        headers=headers
    )

    # 清除覆盖
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "data" in data
    assert data["data"]["status"] == "pending"


def test_list_friends_api(test_db, test_user1, test_user2, test_agent1, test_agent2):
    """测试获取好友列表 API"""
    # 覆盖依赖使用测试数据库
    app.dependency_overrides[get_db] = lambda: test_db

    headers = get_auth_headers(test_user1)

    # 先发送好友请求
    client.post(
        "/api/v1/friends/request",
        json={"target_agent_id": "test_agent_2"},
        headers=headers
    )

    response = client.get("/api/v1/friends", headers=headers)

    # 清除覆盖
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert isinstance(data["data"], list)


def test_pending_requests_api(test_db, test_user1, test_user2, test_agent1, test_agent2):
    """测试获取待处理请求 API"""
    # 覆盖依赖使用测试数据库
    app.dependency_overrides[get_db] = lambda: test_db

    # user1 发送请求给 user2
    headers1 = get_auth_headers(test_user1)
    client.post(
        "/api/v1/friends/request",
        json={"target_agent_id": "test_agent_2"},
        headers=headers1
    )

    # user2 查看待处理请求
    headers2 = get_auth_headers(test_user2)
    response = client.get("/api/v1/friends/pending", headers=headers2)

    # 清除覆盖
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]) >= 1
