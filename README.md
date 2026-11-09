# ToDo App - Microservices Example

- `gateway/`: single API entry point on port 5000.
- `services/auth-service/`: users and authentication on port 5001; MongoDB database `users`.
- `services/task-service/`: tasks on port 5002; MongoDB database `tasks`.
- `frontend/`: existing React app, served on port 3000.

The auth service provides registration, login, profile, and token refresh endpoints, with registration validation. The task service provides authenticated task CRUD, status/priority filtering and validation, and due-date handling.

Copy `.env.example` to `.env`, then run `docker compose up --build`.
Open `http://localhost:3000`; the frontend calls the gateway at port 5000.

## Importing legacy MongoDB data

The old backend stored `users` and `tasks` in the `todolist` database. The migration copies those collections into the microservices' `users` and `tasks` databases, preserves document IDs and password hashes, and converts task `userId` values to strings to match the task service. It does not delete or overwrite source or existing destination records.

Back up MongoDB first. Set `LEGACY_MONGO_URI` in `.env` to the old database (default: `mongodb://mongo:27017/todolist`). Run a dry run, then apply:

```powershell
docker compose --profile migration run --rm data-migration
docker compose --profile migration run --rm data-migration --apply
```

The commands connect to the MongoDB service in this Compose project by default. If the old database is on MongoDB running directly on the Windows host, set `LEGACY_MONGO_URI=mongodb://host.docker.internal:27017/todolist` in `.env`; for another server, use its reachable MongoDB URI. The destination URIs default to the new `users` and `tasks` databases. Run the migration again safely to import records added later; records already present by ID are left unchanged. If the legacy database contains collections other than `users` and `tasks`, the script stops rather than silently skipping them.

The old folder contained application code, not database files. Keep each service's existing `app.py` as its startup entry point; the imported data retains the legacy collection and field names, with only task `userId` normalized for the service schema.

The relevant legacy module names are also retained within their owning service: the auth service has `app/models/user.py`, `app/services/auth_service.py`, `app/controllers/user_controller.py`, and `app/routes/users.py`; the task service has the matching `task.py`, `task_service.py`, `task_controller.py`, and `tasks.py` modules. Shared monolith modules are not copied where they would couple the two services.

If existing JWTs must remain valid, configure `JWT_SECRET_KEY` to the same secret used by the old backend. Otherwise, migrated users can still log in with their existing passwords, but they will need fresh tokens.
