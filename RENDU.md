## Question 1

**Réponse :**

C’est un monolithe. Il a 2 parties :

- `backend/` : API Flask
- `frontend/` : app React

Le backend est organisé en couches :

- `backend/app/routes/` : routes
- `backend/app/controllers/` : contrôleurs
- `backend/app/services/` : logique métier
- `backend/app/models/` : accès aux données
- `backend/app/config.py` : configuration

La base de données est MongoDB. On le voit dans :

- `backend/app/config.py` → `mongodb://localhost:27017/todolist`
- `backend/app/extensions.py` → `from flask_pymongo import PyMongo`
- `backend/requirements.txt` → `flask-pymongo` et `pymongo`

---

## Question 2

**Réponse :**

Le projet ne peut pas tourner avec Docker tel quel, car il n’y a pas de `Dockerfile` ni de `docker-compose.yml`.

Il se lance aujourd’hui en local :

- Backend : `python run.py` dans `backend/`
- Frontend : `npm start` dans `frontend/`

Deux éléments empêchent un bon lancement en conteneur :

1. `backend/app/config.py` utilise `localhost` pour MongoDB :

```python
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/todolist')
```

Dans Docker, `localhost` = le conteneur lui-même, pas la base.

2. `frontend/src/services/api.js` utilise `localhost` pour l’API :

```js
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

