import razorpay

client = razorpay.Client(auth=("KEY", "SECRET"))

def create_order(amount):
    return client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "payment_capture": 1
    })