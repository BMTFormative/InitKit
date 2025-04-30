# backend/app/tests/api/routes/test_subscriptions.py (new file)

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.subscription import create_random_subscription


def test_create_subscription(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Premium Plan", "description": "Monthly subscription", "price": 19.99}
    response = client.post(
        f"{settings.API_V1_STR}/subscriptions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["price"] == data["price"]
    assert "id" in content
    assert "owner_id" in content


def test_read_subscription(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    subscription = create_random_subscription(db)
    response = client.get(
        f"{settings.API_V1_STR}/subscriptions/{subscription.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == subscription.name
    assert content["description"] == subscription.description
    assert content["price"] == subscription.price
    assert content["id"] == str(subscription.id)
    assert content["owner_id"] == str(subscription.owner_id)


def test_read_subscription_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/subscriptions/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Subscription not found"


def test_read_subscription_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    subscription = create_random_subscription(db)
    response = client.get(
        f"{settings.API_V1_STR}/subscriptions/{subscription.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_subscriptions(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_subscription(db)
    create_random_subscription(db)
    response = client.get(
        f"{settings.API_V1_STR}/subscriptions/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_subscription(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    subscription = create_random_subscription(db)
    data = {"name": "Updated Plan", "description": "Updated description", "price": 29.99}
    response = client.put(
        f"{settings.API_V1_STR}/subscriptions/{subscription.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert content["price"] == data["price"]
    assert content["id"] == str(subscription.id)
    assert content["owner_id"] == str(subscription.owner_id)


def test_update_subscription_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"name": "Updated Plan", "description": "Updated description", "price": 29.99}
    response = client.put(
        f"{settings.API_V1_STR}/subscriptions/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Subscription not found"


def test_update_subscription_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    subscription = create_random_subscription(db)
    data = {"name": "Updated Plan", "description": "Updated description", "price": 29.99}
    response = client.put(
        f"{settings.API_V1_STR}/subscriptions/{subscription.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_subscription(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    subscription = create_random_subscription(db)
    response = client.delete(
        f"{settings.API_V1_STR}/subscriptions/{subscription.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Subscription deleted successfully"


def test_delete_subscription_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/subscriptions/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Subscription not found"


def test_delete_subscription_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    subscription = create_random_subscription(db)
    response = client.delete(
        f"{settings.API_V1_STR}/subscriptions/{subscription.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"