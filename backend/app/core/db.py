from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, SubscriptionPlan, SubscriptionPlanCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    # Create first superuser
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
    
    # Create default subscription plans
    existing_plans = session.exec(select(SubscriptionPlan)).all()
    if not existing_plans:
        # Basic Plan
        basic_plan = SubscriptionPlanCreate(
            name="Basic",
            description="Perfect for getting started",
            price=9.99,
            duration_days=30,
            features=[
                "Up to 100 items",
                "Basic support",
                "API access"
            ],
            is_active=True
        )
        crud.create_subscription_plan(session=session, plan_create=basic_plan)
        
        # Pro Plan
        pro_plan = SubscriptionPlanCreate(
            name="Pro",
            description="For professional use",
            price=29.99,
            duration_days=30,
            features=[
                "Unlimited items",
                "Priority support",
                "API access",
                "Advanced analytics",
                "Custom integrations"
            ],
            is_active=True
        )
        crud.create_subscription_plan(session=session, plan_create=pro_plan)
        
        # Enterprise Plan
        enterprise_plan = SubscriptionPlanCreate(
            name="Enterprise",
            description="For large teams and organizations",
            price=99.99,
            duration_days=30,
            features=[
                "Unlimited everything",
                "24/7 support",
                "API access",
                "Advanced analytics",
                "Custom integrations",
                "SSO/SAML authentication",
                "Dedicated account manager"
            ],
            is_active=True
        )
        crud.create_subscription_plan(session=session, plan_create=enterprise_plan)
        
        print("Created default subscription plans")