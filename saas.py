from datetime import datetime, timedelta

plans = {
    "free": 1,
    "pro": 30,
    "business": 365
}

def is_subscription_active(user):
    if user.plan == "free":
        return True

    if user.expiry_date > datetime.utcnow():
        return True

    return False