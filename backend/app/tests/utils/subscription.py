# backend/app/tests/utils/subscription.py (new file)

from sqlmodel import Session

from app import crud
from app.models import Subscription, SubscriptionCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_subscription(db: Session) -> Subscription:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    name = random_lower_string()
    description = random_lower_string()
    price = 9.99  # Example price
    subscription_in = SubscriptionCreate(name=name, description=description, price=price)
    return crud.create_subscription(session=db, subscription_in=subscription_in, owner_id=owner_id)