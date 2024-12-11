from . import db
from sqlalchemy import Date

class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gym.gym_id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    Password = db.Column(db.String(255), nullable=False)

    # Relations
    gym = db.relationship('Gym', back_populates='employees')
    schedules = db.relationship('Schedule', back_populates='employee')
    gym_classes = db.relationship('GymClass', back_populates='employee')


class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.subscription_id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text)
    phone_number = db.Column(db.String(12))
    sub_purchase_date = db.Column(Date)

    # Relations
    subscription = db.relationship('Subscription', back_populates='customers')


class Subscription(db.Model):
    subscription_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)
    period = db.Column(db.String(20), nullable=False)

    # Relations
    customers = db.relationship('Customer', back_populates='subscription')


class Gym(db.Model):
    gym_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text)

    # Relations
    employees = db.relationship('Employee', back_populates='gym')
    products = db.relationship('Product', back_populates='gym')
    schedules = db.relationship('Schedule', back_populates='gym')
    gym_classes = db.relationship('GymClass', back_populates='gym')


class Schedule(db.Model):
    schedule_id = db.Column(db.Integer, primary_key=True)
    gymclass_id = db.Column(db.Integer, db.ForeignKey('gym_class.gymclass_id'), nullable=False)
    gym_id = db.Column(db.Integer, db.ForeignKey('gym.gym_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    day_otw = db.Column(db.String(15), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Relations
    gym_class = db.relationship('GymClass', back_populates='schedules')
    gym = db.relationship('Gym', back_populates='schedules')
    employee = db.relationship('Employee', back_populates='schedules')


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gym.gym_id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(5, 2), nullable=False)
    total_revenue = db.Column(db.Numeric(12, 2))

    # Relations
    gym = db.relationship('Gym', back_populates='products')


class GymClass(db.Model):
    gymclass_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    gym_id = db.Column(db.Integer, db.ForeignKey('gym.gym_id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    max_people = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Time, nullable=False)
    day_otw = db.Column(db.String(15), nullable=False)
    signed_people = db.Column(db.Integer, nullable=False)

    # Relations
    employee = db.relationship('Employee', back_populates='gym_classes')
    gym = db.relationship('Gym', back_populates='gym_classes')
    schedules = db.relationship('Schedule', back_populates='gym_class')
