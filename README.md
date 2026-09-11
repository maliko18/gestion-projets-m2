# Guide TP - Gestion des Projets

Ce projet contient l'application Python/Flask et la base de données SQL développées pour le TP.

---

## 🚀 1. Lancement Rapide (Quick Start)

### Option A : Avec SQLite (Rien à installer de plus que Python)

1. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

2. Créez et remplissez la base de données avec les données du TP :

   ```bash
   python init_db.py
   ```

3. Lancez l'application Web :
   ```bash
   python app.py
   ```
4. Ouvrez votre navigateur sur : **`http://127.0.0.1:5000`**

---

### Option B : Avec PostgreSQL

1. Démarrez votre serveur PostgreSQL et créez la base de données :
   ```sql
   CREATE DATABASE gestion_projets;
   ```
2. Configurez le fichier `.env` avec vos identifiants PostgreSQL (`DB_USER`, `DB_PASSWORD`, etc.).
3. Assurez-vous que `USE_SQLITE=false` dans le fichier `.env`.
4. Initialisez la base de données et lancez l'application :
   ```bash
   python init_db.py
   python app.py
   ```
