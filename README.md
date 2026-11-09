# ToDo App - Microservice Example

A small example with an API gateway and two independent services.

## Structure

- `gateway/` forwards API requests to the services.
- `services/auth-service/` provides example login and registration endpoints.
- `services/task-service/` provides example task endpoints.
- `docker-compose.yml` starts the three containers.

## Run

Run `docker compose up --build`, then use `http://localhost:8080/api/users/login`
or `http://localhost:8080/api/tasks`.

The service responses are examples only: they use no database and do not
implement real authentication or persistent task storage.
