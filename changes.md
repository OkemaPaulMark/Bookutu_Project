# Changes to Bookutu Project Models

### Date: September 2, 2025

## 1. Combining Booking and Payment Models

### Overview

The booking and payment system has been refactored to simplify the data model and improve data integrity. The previously separate `Booking` and `Payment` models have been combined into a single `Booking` model that handles all payment-related information.

## Changes Made

### 1. Combined Models

- **Removed** the `Payment` model entirely
- **Added** payment fields directly to the `Booking` model:
  - `payment_method`: Choice field for payment method (Mobile Money, Card, Cash)
  - `payment_status`: Status of the payment (pending, paid, failed)
  - `amount_paid`: Decimal field for the payment amount
  - `payment_reference`: Reference number for the transaction
  - `paid_at`: Timestamp for when payment was made

### 2. Improved Data Integrity

- **Added** automatic booking confirmation when payment is successful
  ```python
  def save(self, *args, **kwargs):
      # Auto-confirm booking when payment is marked as paid
      if self.payment_status == "paid" and self.status == "pending":
          self.status = "confirmed"
      super().save(*args, **kwargs)
  ```

- **Added** validation to prevent confirming bookings without payment
  ```python
  def clean(self):
      # ... existing validation ...
      # Ensure booking can only be confirmed if payment is successful
      if self.status == "confirmed" and self.payment_status != "paid":
          raise ValidationError("Booking cannot be confirmed until payment is successful.")
  ```

- **Added** database-level constraint to enforce that confirmed bookings must have paid status
  ```python
  class Meta:
      unique_together = ('trip', 'seat_number')
      constraints = [
          models.CheckConstraint(
              check=models.Q(status='confirmed', payment_status='paid') | ~models.Q(status='confirmed'),
              name='booking_confirmed_only_if_paid'
          )
      ]
  ```

### 3. Seat Booking Constraint

- **Fixed** the unique constraint to ensure a seat can only be booked once per trip
  ```python
  class Meta:
      unique_together = ('trip', 'seat_number')
  ```

## Benefits

1. **Simplified Data Model**: No more need to manage two separate but closely related database tables
2. **Eliminated Circular References**: Removed the circular foreign key relationship between Booking and Payment
3. **Improved Data Integrity**: Multi-level validation ensures bookings can only be confirmed with successful payments
4. **Simplified API**: Payment information is directly accessible from a booking object
5. **Streamlined Business Logic**: Payment and booking status are synchronized within a single model

## 2. Bus Models and Seat Management

### Bus System Architecture

The bus reservation system is built on a hierarchical structure that represents real-world bus operations:

#### BusCompany Model
- Represents bus operators/companies that own and operate buses
- Each company has a name, contact information, and address
- Companies are linked to buses, routes, and can receive feedback

#### BusModel Model
- Represents different types of buses with specific characteristics:
  - `name`: Model name/designation
  - `number_of_seats`: Total capacity of the bus
  - `is_three_seater`: Boolean flag for buses with 3-seat rows (vs standard 2-seat rows)
  - `is_electric`: Indicates if the bus uses electric propulsion
  - `year_of_manufacture`: Production year

#### Bus Model
- Represents individual bus vehicles:
  - Each bus belongs to a specific company (ForeignKey to BusCompany)
  - Has a unique `number_plate` for identification
  - Links to a BusModel that defines its physical characteristics
  - `is_active` flag allows decommissioning buses while preserving booking history

#### Route Model
- Represents predefined travel routes between locations
- Routes are associated with specific bus companies
- Contains start and end locations plus distance and duration information
- Each route can have multiple trips scheduled

### Seat Management Logic

The seat management system ensures accurate booking without overbooking through multiple validation layers:

1. **Capacity Validation**
   - Booking model validates that the seat number doesn't exceed bus capacity
   - Uses `BusModel.number_of_seats` to enforce bus capacity limits

2. **Double Booking Prevention**
   - Database-level unique constraint on ('trip', 'seat_number')
   - Application-level validation in the Booking.clean() method checks for duplicate bookings
   - Error raised if attempting to book an already reserved seat

3. **Seat Referencing**
   - Seat numbers are stored as integers for simplicity
   - Validation ensures seat numbers are within the capacity of the specific bus model
   - The clean() method provides descriptive error messages about capacity limits

4. **Seat Availability**
   - When a seat is booked, it becomes unavailable for the specific trip
   - The unique constraint ensures no two bookings can reference the same seat on the same trip

## Required Actions

After deploying these changes, please run the following commands to update the database schema:

```
python manage.py makemigrations
python manage.py migrate
```

## Note

These changes may require updates to any views or serializers that previously worked with the separate Payment model.
