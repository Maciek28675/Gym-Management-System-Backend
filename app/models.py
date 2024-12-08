from . import db
from sqlalchemy import Date

class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    # gym_id
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(50))
    Password = db.Column(db.String(255))


class Customer(db.Model):
    customer_id = db.Column()
    # subsrcitpion_id
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    address = db.Column(db.Text)
    phone_number = db.Column(db.String(12))
    sub_purchase_date = db.Column(Date)


class Subscription(db.Model):
    pass


class Gym(db.Model):
    pass


class Schedule(db.Model):
    pass


class Product(db.Model):
    pass


class GymClass(db.Model):
    pass