Parcel Tracking API

Simple Django REST Framework API for creating parcels, tracking parcel status, and viewing parcel movement history by tracking number.

1. Tech Stack

- Python 3.12
- Django
- Django REST Framework
- SQLite
- Docker / Docker Compose

2. Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
````

Base URL:

```text
http://127.0.0.1:8000/api/
```

3. Run with Docker

```bash
docker compose up --build
```

Base URL with Docker:

```text
http://127.0.0.1:8002/api/
```

4. Tests

```bash
python manage.py test
```

5. API Endpoints

5.1. Post Offices

Create post office:

```http
POST /api/offices/
```

```json
{
  "number": 1,
  "city": "Kyiv",
  "address": "Khreshchatyk 1",
  "postal_code": "01001"
}
```

Get post offices:

```http
GET /api/offices/
```

5.2. Parcels

Create parcel:

```http
POST /api/parcels/
```

```json
{
  "sender_full_name": "Alice Johnson",
  "sender_phone": "+380991112233",
  "receiver_full_name": "Bob Smith",
  "receiver_phone": "+380991234567",
  "sender_office": 1,
  "destination_office": 2,
  "weight": "2.50",
  "declared_value": "100.00"
}
```

The tracking number is generated automatically and returned in the response.

Get parcels:

```http
GET /api/parcels/
```

Filter parcels:

```http
GET /api/parcels/?status=in_transit&from_city=Kyiv
```

Get parcel details with status history:

```http
GET /api/parcels/{tracking_number}/
```

Example:

```http
GET /api/parcels/TRK77C8FE2E45/
```

5.3 Update parcel status

```http
POST /api/parcels/{tracking_number}/status/
```

```json
{
  "status": "accepted",
  "office": 1,
  "comment": "Parcel accepted at sender office"
}
```

Allowed statuses:

```text
created, accepted, in_transit, arrived, delivered, returned
```

Example status flow:

```text
created -> accepted -> in_transit -> arrived -> delivered
```

Alternative flow:

```text
created -> accepted -> in_transit -> returned
```

5.4. Parcels in post office

Returns parcels that are currently in a specific destination office with `arrived` status.

```http
GET /api/offices/{id}/parcels/
```

Example:

```http
GET /api/offices/2/parcels/
```

6. Business Rules

* A parcel cannot be delivered before it has arrived at the destination office.
* Terminal statuses `delivered` and `returned` cannot be changed.
* Weight must be greater than `0` and not more than `30` kg.
* Declared value cannot be negative.
* Sender office and destination office must be different.
* Every status change automatically creates a history record.

6.1. Admin

Django admin is available at:

```text
http://127.0.0.1:8000/admin/
```
