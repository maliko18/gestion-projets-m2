from datetime import datetime
from database import get_db_connection


def create_and_seed_database():
    conn, engine = get_db_connection()
    cursor = conn.cursor()

    print(f"[*] Initialisation de la base de données ({engine})...")

    # Schéma SQL pour PostgreSQL ou SQLite
    if engine == "postgres":
        create_table_sql = """
        DROP TABLE IF EXISTS projet;
        CREATE TABLE projet (
            id SERIAL PRIMARY KEY,
            nomProj VARCHAR(50) NOT NULL,
            mgrProj VARCHAR(50) NOT NULL,
            idEmp VARCHAR(10) NOT NULL,
            heures INTEGER NOT NULL,
            nomEmp VARCHAR(50) NOT NULL,
            budget NUMERIC(12, 2) NOT NULL,
            dateDebut DATE NOT NULL,
            salEmp NUMERIC(10, 2) NOT NULL,
            mgrEmp VARCHAR(50) NOT NULL,
            deptEmp VARCHAR(50) NOT NULL,
            evalEmp INTEGER,
            CONSTRAINT uq_proj_emp UNIQUE (nomProj, idEmp)
        );
        """
        insert_sql = """
        INSERT INTO projet (nomProj, mgrProj, idEmp, heures, nomEmp, budget, dateDebut, salEmp, mgrEmp, deptEmp, evalEmp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
    else:
        create_table_sql = """
        DROP TABLE IF EXISTS projet;
        CREATE TABLE projet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomProj TEXT NOT NULL,
            mgrProj TEXT NOT NULL,
            idEmp TEXT NOT NULL,
            heures INTEGER NOT NULL,
            nomEmp TEXT NOT NULL,
            budget REAL NOT NULL,
            dateDebut TEXT NOT NULL,
            salEmp REAL NOT NULL,
            mgrEmp TEXT NOT NULL,
            deptEmp TEXT NOT NULL,
            evalEmp INTEGER,
            UNIQUE(nomProj, idEmp)
        );
        """
        insert_sql = """
        INSERT INTO projet (nomProj, mgrProj, idEmp, heures, nomEmp, budget, dateDebut, salEmp, mgrEmp, deptEmp, evalEmp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

    # Exécution de la création de la table
    if engine == "postgres":
        cursor.execute(create_table_sql)
    else:
        cursor.executescript(create_table_sql)

    # Données issues de l'énoncé du TP :
    # ILO Dupont E101 25 Durand 100000 15/11/2011 45000 Holmes 10 9
    # ILO Dupont E105 39 Adam   100000 15/11/2011 43000 Lupin  12 NULL
    # ILO Dupont E110 10 Rivera 100000 15/11/2011 41000 Holmes 10 8
    # MAXI Jones E110 29 Rivera 200000 03/01/2012 41000 Holmes 10 NULL
    records = [
        ("ILO", "Dupont", "E101", 25, "Durand", 100000.00, "2011-11-15", 45000.00, "Holmes", "10", 9),
        ("ILO", "Dupont", "E105", 39, "Adam", 100000.00, "2011-11-15", 43000.00, "Lupin", "12", None),
        ("ILO", "Dupont", "E110", 10, "Rivera", 100000.00, "2011-11-15", 41000.00, "Holmes", "10", 8),
        ("MAXI", "Jones", "E110", 29, "Rivera", 200000.00, "2012-01-03", 41000.00, "Holmes", "10", None),
    ]

    # Utilisation STRICTE de requêtes paramétrées (Sécurisation des applications : prévention des injections SQL)
    cursor.executemany(insert_sql, records)
    conn.commit()

    print(f"[✓] {len(records)} enregistrements injectés avec succès dans la table 'projet'.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    create_and_seed_database()
