
# AquaCare – Water Authority Management System

AquaCare is a web-based Water Authority Management System developed using Python and Django. It is designed to simplify water service administration by providing dedicated functionalities for customers, water authority staff, and department managers.

## Project Overview

The system digitizes important water authority operations, including customer water connections, meter readings, billing, payments, complaint management, and staff task monitoring.

## Objectives

- Digitize water authority management operations.
- Simplify customer service and billing processes.
- Provide role-based access to different users.
- Improve complaint handling and tracking.
- Support staff coordination and management.

## User Roles

1. **Customer**
   - View dashboard and water connections.
   - Access meter readings and bills.
   - View payment history and receipts.
   - Submit and track complaints.

2. **Water Authority Staff**
   - Manage assigned complaints and service activities.
   - Update complaint progress.
   - Monitor assigned work.

3. **Department Manager**
   - Monitor department activities.
   - Assign work to staff.
   - Track staff progress.
   - Monitor applications and operational reports.

## Key Features

- Custom user authentication and role-based access control.
- Customer and water connection management.
- Meter reading management.
- Tariff-based bill generation and bill details.
- Payment records and payment history.
- Complaint submission and management.
- Staff task assignment and progress tracking.
- Role-specific dashboards.
- Notifications and reports.
- Django administration support.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| HTML5 | Page structure |
| CSS3 | Styling |
| Bootstrap | Responsive UI |
| JavaScript | Interactive functionality |
| SQLite | Database |
| Django Authentication | User authentication |

## Project Architecture

The project follows Django's MVT (Model-View-Template) architecture.

- **Models:** Manage database structure and relationships.
- **Views:** Handle business logic and requests.
- **Templates:** Display the user interface.
- **URLs:** Route requests to the appropriate views.

### Django Applications

- `accounts` – User authentication and role management.
- `customers` – Customer and water connection operations.
- `billing` – Meter readings, bills and payments.
- `complaints` – Complaint handling and staff workflows.
- `dashboard` – Dashboard and reporting functionality.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Aminafaiza/Water-Authority-Management-System-.git
```

### 2. Navigate to the project folder

```bash
cd Water-Authority-Management-System-
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Create an administrator account if required

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

Open the application:

http://127.0.0.1:8000/

## Project Screenshots

Screenshots of the application will be added here.

## Learning Outcomes

Through this project, I gained practical experience in:

- Django MVT architecture.
- Custom user models and authentication.
- Role-based authorization.
- Database relationships and ORM operations.
- CRUD operations.
- Business logic implementation.
- Form handling and validation.
- Developing responsive web applications.

## Developer

**Amina Faiza HS**

Python Full Stack Developer

GitHub: https://github.com/Aminafaiza

---

This project was developed as a practical full-stack web development project using Python and Django.
