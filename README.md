# ToDo App - Microservice Example

This project is a simple example of a microservice architecture.

## Structure

- `gateway/` : API gateway for external requests
- `services/auth-service/` : user authentication service
- `services/task-service/` : task management service
- `docker-compose.yml` : runs all services together

## Services

- `gateway` exposes the app to clients
- `auth-service` handles login/register
- `task-service` handles task CRUD

This is only an example architecture, not a production-ready system.
