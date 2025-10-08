# Group Integration Guide

This repository vendors the group repo `Bookutu_Project` under `external/Bookutu_Project/` via git subtree. We port API shapes in a `group_compat` app instead of adopting their models/migrations/settings.

## Branch

- Work branch: `integrate/group-project`

## Endpoints

- `GET /api/group-compat/companies/`
- `GET /api/group-compat/buses/`
- `GET /api/group-compat/routes/`
- `GET /api/group-compat/trips/`
- `POST /api/group-compat/trips/{id}/book/`
- `GET /api/group-compat/bookings/`, `GET /api/group-compat/bookings/{id}/`

## Field Mappings

- BusCompany → `companies.Company`
- Bus.number_plate ↔ `companies.Bus.license_plate`
- Route.start_location/end_location ↔ `trips.Route.origin_city/destination_city`
- Trip datetime ↔ `trips.Trip.departure_date+departure_time/arrival_time`
- Booking.seat_number ↔ `companies.BusSeat.seat_number`

## Tenancy & Auth

- Requires auth. Company staff scoped to `request.user.company`.

## Update vendored repo

```bash
git fetch group
git subtree pull --prefix=external/Bookutu_Project group master --squash
```

## Example cURL

```bash
# list trips
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/group-compat/trips/

# book seat
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"seat_number":"1A","passenger_name":"John","passenger_phone":"077...","payment_method":"cash","payment_status":"paid","amount_paid":"50000"}' \
  http://localhost:8000/api/group-compat/trips/1/book/
```


