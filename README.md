# ToDo App - Microservices Example

- `gateway/`: single API entry point on port 5000.
- `services/auth-service/`: users and authentication on port 5001; MongoDB database `users`.
- `services/task-service/`: tasks on port 5002; MongoDB database `tasks`.
- `frontend/`: existing React app, served on port 3000.

Copy `.env.example` to `.env`, then run `docker compose up --build`.
Open `http://localhost:3000`; the frontend calls the gateway at port 5000.
