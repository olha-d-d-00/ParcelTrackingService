Parcel Tracking API
Simple Django REST Framework API for creating parcels, updating parcel statuses, and tracking parcel delivery history by tracking number.

1. Tech Stack

- Python 3.12
- Django
- Django REST Framework
- SQLite
- Docker
- Docker Compose


2. Run Locally
Create virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

Apply migrations:

```bash
python manage.py migrate
```

Run development server:

```bash
python manage.py runserver 8001
```

Local Base URL:

```text
http://127.0.0.1:8001/api/
```

3. Run with Docker
Build and start containers:
```bash
docker compose up --build
```

Docker Base URL:
```text
http://127.0.0.1:8002/api/
```

Stop containers:
```bash
docker compose down
```



4. Run Tests

```bash
python manage.py test
```

---

5. API Endpoints

5.1 Post Offices
Create post office
```http
POST /api/offices/
```
Request example:
```json
{
  "number": 1,
  "city": "Kyiv",
  "address": "Khreshchatyk 1",
  "postal_code": "01001"
}
```
Get all post offices
```http
GET /api/offices/
```

---

5.2 Parcels

Create parcel
```http
POST /api/parcels/
```

Request example:

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

---

Get all parcels

```http
GET /api/parcels/
```

---

Filter parcels

Filter by status and sender city:
GET /api/parcels/?status=in_transit&from_city=Kyiv


Get parcel details by tracking number
GET /api/parcels/{tracking_number}/


Example:
GET /api/parcels/TRK77C8FE2E45/
The response contains parcel details and full status history.


5.3 Update Parcel Status
Update parcel status
POST /api/parcels/{tracking_number}/status/

Request example:
{
  "status": "accepted",
  "office": 1,
  "comment": "Parcel accepted at sender office"
}




Allowed statuses:
created
accepted
in_transit
arrived
delivered
returned


Example status flow
created -> accepted -> in_transit -> arrived -> delivered


Alternative flow:
created -> accepted -> in_transit -> returned



5.4 Parcels in Post Office
Returns parcels that are currently located in a specific destination office.
Conditions:
- parcel status must be `arrived`
- destination office must match requested office id
GET /api/offices/{id}/parcels/

Example:
GET /api/offices/2/parcels/



6. Business Rules

- A parcel cannot be delivered before it has arrived at the destination office.
- Terminal statuses `delivered` and `returned` cannot be changed.
- Weight must be greater than `0` and not more than `30` kg.
- Declared value cannot be negative.
- Sender office and destination office must be different. 
- Every status change automatically creates a history record.



7. Django Admin

Django admin is available at:

Local:
http://127.0.0.1:8001/admin/


Docker:
http://127.0.0.1:8002/admin/


---

8. Project Structure

```text
ParcelTrackingService/
│
├── config/
├── parcels/
├── SQL_ANSWERS
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── README.md
```

Additional SQL tasks:
SQL_ANSWERS/sql_tasks_answers.docx
