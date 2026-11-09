import argparse
import os
import sys

from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, PyMongoError


DEFAULT_LEGACY_URI = "mongodb://localhost:27017/todolist"
DEFAULT_USERS_URI = "mongodb://localhost:27017/users"
DEFAULT_TASKS_URI = "mongodb://localhost:27017/tasks"


def get_database(client, label):
    try:
        database = client.get_default_database()
    except ConfigurationError as error:
        raise ValueError(f"{label} URI must include a database name") from error
    if database is None:
        raise ValueError(f"{label} URI must include a database name")
    return database


def unique_email_conflicts(source_users, target_users):
    emails = {}
    conflicts = []
    for user in source_users:
        email = user.get("email")
        if not isinstance(email, str) or not email:
            conflicts.append(f"source user {user['_id']} has no valid email")
            continue
        if email in emails and emails[email] != user["_id"]:
            conflicts.append(f"source contains multiple users with email {email}")
        emails[email] = user["_id"]

    target_email_ids = {}
    for user in target_users:
        email = user.get("email")
        if not isinstance(email, str) or not email:
            conflicts.append(f"target user {user['_id']} has no valid email")
            continue
        if email in target_email_ids and target_email_ids[email] != user["_id"]:
            conflicts.append(
                f"target already contains multiple users with email {email}"
            )
        target_email_ids[email] = user["_id"]

    for email, user_id in emails.items():
        target_id = target_email_ids.get(email)
        if target_id is not None and target_id != user_id:
            conflicts.append(
                f"email {email} already belongs to a different target user"
            )
    return conflicts


def migrate(source_db, users_db, tasks_db, apply_changes):
    source_users = list(source_db.users.find())
    source_tasks = list(source_db.tasks.find())
    target_users = list(users_db.users.find({}, {"_id": 1, "email": 1}))
    target_tasks = list(tasks_db.tasks.find({}, {"_id": 1}))

    conflicts = unique_email_conflicts(source_users, target_users)
    if conflicts:
        raise ValueError(
            "Migration preflight found conflicts:\n- " + "\n- ".join(conflicts)
        )

    target_user_ids = {user["_id"] for user in target_users}
    target_task_ids = {task["_id"] for task in target_tasks}
    users_to_insert = [
        user for user in source_users if user["_id"] not in target_user_ids
    ]
    tasks_to_insert = [
        task for task in source_tasks if task["_id"] not in target_task_ids
    ]

    print(f"Legacy database: {source_db.name}")
    print(
        f"Users: {len(source_users)} found, {len(users_to_insert)} to import, "
        f"{len(source_users) - len(users_to_insert)} already present"
    )
    print(
        f"Tasks: {len(source_tasks)} found, {len(tasks_to_insert)} to import, "
        f"{len(source_tasks) - len(tasks_to_insert)} already present"
    )
    if not apply_changes:
        print("Dry run only. Re-run with --apply to import these records.")
        return

    users_db.users.create_index("email", unique=True)
    for user in users_to_insert:
        users_db.users.insert_one(user)

    for task in tasks_to_insert:
        if isinstance(task.get("userId"), ObjectId):
            task["userId"] = str(task["userId"])
        elif task.get("userId") is not None:
            task["userId"] = str(task["userId"])
        tasks_db.tasks.insert_one(task)

    print("Import complete. Existing target records were left unchanged.")


def main():
    parser = argparse.ArgumentParser(
        description="Copy legacy todolist MongoDB users and tasks into the microservice databases."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write records; without this flag, the script only performs a dry run",
    )
    args = parser.parse_args()

    uris = {
        "legacy": os.getenv("LEGACY_MONGO_URI", DEFAULT_LEGACY_URI),
        "users": os.getenv("USERS_MONGO_URI", DEFAULT_USERS_URI),
        "tasks": os.getenv("TASKS_MONGO_URI", DEFAULT_TASKS_URI),
    }
    clients = []
    try:
        databases = {}
        for label, uri in uris.items():
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            clients.append(client)
            databases[label] = get_database(client, label)

        source_name = databases["legacy"].name
        if source_name in (databases["users"].name, databases["tasks"].name):
            raise ValueError(
                "Legacy and destination database names must differ; "
                "check the configured MongoDB URIs before importing."
            )
        if databases["users"].name == databases["tasks"].name:
            raise ValueError(
                "Users and tasks destination URIs must use separate databases."
            )
        extra_collections = set(databases["legacy"].list_collection_names()) - {
            "users",
            "tasks",
        }
        if extra_collections:
            raise ValueError(
                "Legacy database has collections this migration does not handle: "
                + ", ".join(sorted(extra_collections))
            )
        migrate(
            databases["legacy"],
            databases["users"],
            databases["tasks"],
            args.apply,
        )
    except (ValueError, PyMongoError) as error:
        print(f"Migration failed: {error}", file=sys.stderr)
        return 1
    finally:
        for client in clients:
            client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
