# HotelIQ — AI Smart Hotel Management System

A premium full-stack Smart Hotel Management System with a polished animated frontend, rich demo data, role-based login and AI-style hotel intelligence features. Built for final-year project demos and product-style hotel presentations.

## Created By

**Chinmay and Krutick**

## Highlights

- Premium animated dashboard UI
- Secure demo login system
- Role-based access demo: Admin, Receptionist and Housekeeping
- AI Command Center
- Dynamic room pricing suggestions
- No-show risk prediction
- Guest sentiment analysis
- Predictive maintenance risk
- Smart hotel alerts
- Room, booking, customer, housekeeping, payment, food order, service and staff modules
- Rich seed data for realistic demo
- Responsive design for laptop/projector/mobile

## Tech Stack

- Frontend: React + Vite + Recharts + Lucide Icons
- Backend: Node.js + Express
- Database: JSON file database for easy demo
- API: REST API

## Project Structure

```txt
smart-hotel-fullstack/
├── backend/
│   ├── data/db.json
│   ├── ai.js
│   ├── db.js
│   ├── server.js
│   └── package.json
├── frontend/
│   ├── src/main.jsx
│   ├── src/style.css
│   ├── index.html
│   └── package.json
├── README.md
└── .gitignore
```

## Run Locally

### 1. Start Backend

```bash
cd backend
npm install
npm start
```

Backend runs on:

```txt
http://localhost:5000
```

### 2. Start Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm start
```

Frontend runs on:

```txt
http://localhost:5173
```

## Demo Login Credentials

Use any of these accounts. The password is the same for all demo users.

```txt
Admin:        admin@hoteliq.com
Reception:    reception@hoteliq.com
Housekeeping: housekeeping@hoteliq.com
Password:     admin123
```

## Demo Flow

1. Open the login page and show the creator credit: Chinmay and Krutick.
2. Login as Admin.
3. Open Dashboard and explain live KPIs.
4. Show animated revenue and occupancy charts.
5. Open Rooms and show premium room cards.
6. Open AI Command Center.
7. Explain dynamic pricing, no-show risk, sentiment analysis and maintenance alerts.
8. Show bookings, customers, housekeeping, payments and food orders.
9. Logout and briefly show role-based login options.
10. End with future scope: real ML model, cloud database, payment gateway and mobile app.

## API Modules

- `/api/login`
- `/api/dashboard`
- `/api/ai/command-center`
- `/api/ai/assistant`
- `/api/rooms`
- `/api/customers`
- `/api/bookings`
- `/api/housekeeping`
- `/api/payments`
- `/api/feedback`
- `/api/foodOrders`
- `/api/services`
- `/api/staff`

## Future Scope

- Real authentication with JWT and encrypted passwords
- Cloud database such as MongoDB Atlas or PostgreSQL
- Online payment gateway
- QR-based check-in and check-out
- Mobile app for guests and staff
- Real machine learning model for pricing and guest behavior
- Multi-hotel / multi-branch support


## Login Credentials

- Chinmay Admin: `chinmay@hoteliq.com` / `chinmay123`
- Krutick Manager: `krutick@hoteliq.com` / `krutick123`
- Hotel Team: `team@hoteliq.com` / `team123`

## Credits

Created by **Chinmay** and **Krutick**.
