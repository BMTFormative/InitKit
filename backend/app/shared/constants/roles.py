"""
Role and status constants
"""

# User roles
class UserRoles:
    ADMIN = "admin"
    USER = "user"

# Subscription statuses
class SubscriptionStatus:
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

# Transaction types
class TransactionTypes:
    ADD = "add"
    DEDUCT = "deduct"
    REFUND = "refund"
