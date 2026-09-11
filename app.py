import os
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db_connection

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "cle_secrete_par_defaut")


@app.route("/")
def index():
    """
    Page 1 : Liste globale et recherche sécurisée.
    Affiche la liste des projets agrégés et le détail des affectations.
    """
    query_search = request.args.get("q", "").strip()
    conn, engine = get_db_connection()
    cursor = conn.cursor()

    param_placeholder = "%s" if engine == "postgres" else "?"

    # 1. Récupération synthétique des projets
    sql_projets = """
        SELECT nomProj, mgrProj, budget, dateDebut,
               COUNT(idEmp) AS nb_employes,
               SUM(heures) AS total_heures
        FROM projet
        GROUP BY nomProj, mgrProj, budget, dateDebut
        ORDER BY nomProj;
    """
    cursor.execute(sql_projets)
    projets_summary = cursor.fetchall()

    # 2. Récupération des affectations (avec filtre)
    vulnerable_mode = request.args.get("vulnerable", "false").lower() == "true"

    if query_search:
        if vulnerable_mode:
            # VULNÉRABLE : Concaténation directe de la saisie utilisateur dans la requête SQL !
            sql_affectations = f"""
                SELECT * FROM projet
                WHERE nomProj LIKE '%{query_search}%'
                   OR nomEmp LIKE '%{query_search}%'
                   OR idEmp LIKE '%{query_search}%'
                ORDER BY nomProj, nomEmp;
            """
            cursor.execute(sql_affectations)
        else:
            # SÉCURISÉ : Utilisation de requêtes paramétrées
            sql_affectations = f"""
                SELECT * FROM projet
                WHERE nomProj LIKE {param_placeholder}
                   OR nomEmp LIKE {param_placeholder}
                   OR idEmp LIKE {param_placeholder}
                ORDER BY nomProj, nomEmp;
            """
            search_pattern = f"%{query_search}%"
            cursor.execute(sql_affectations, (search_pattern, search_pattern, search_pattern))
    else:
        sql_affectations = """
            SELECT * FROM projet
            ORDER BY nomProj, nomEmp;
        """
        cursor.execute(sql_affectations)

    affectations = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        projets=projets_summary,
        affectations=affectations,
        search=query_search,
        vulnerable=vulnerable_mode,
        engine=engine
    )


@app.route("/projet/<string:nom_proj>")
def projet_detail(nom_proj):
    """
    Page 2 : Vue détaillée d'un projet spécifique avec ses employés et ses heures.
    """
    conn, engine = get_db_connection()
    cursor = conn.cursor()
    param_placeholder = "%s" if engine == "postgres" else "?"

    # Requête paramétrée sécurisée pour éviter l'injection SQL dans l'URL
    sql = f"""
        SELECT * FROM projet
        WHERE nomProj = {param_placeholder}
        ORDER BY nomEmp;
    """
    cursor.execute(sql, (nom_proj,))
    affectations = cursor.fetchall()

    cursor.close()
    conn.close()

    if not affectations:
        flash(f"Aucun projet trouvé sous le nom '{nom_proj}'.", "warning")
        return redirect(url_for("index"))

    # Informations générales du projet (récupérées depuis le premier enregistrement)
    info_projet = affectations[0]
    total_heures = sum(row["heures"] for row in affectations)

    return render_template(
        "projet_detail.html",
        projet=info_projet,
        affectations=affectations,
        total_heures=total_heures
    )


@app.route("/affectation/nouvelle", methods=["GET", "POST"])
def nouvelle_affectation():
    """
    Page optionnelle d'ajout d'une affectation avec validation stricte des données.
    """
    if request.method == "POST":
        nomProj = request.form.get("nomProj", "").strip()
        mgrProj = request.form.get("mgrProj", "").strip()
        idEmp = request.form.get("idEmp", "").strip()
        nomEmp = request.form.get("nomEmp", "").strip()
        mgrEmp = request.form.get("mgrEmp", "").strip()
        deptEmp = request.form.get("deptEmp", "").strip()
        dateDebut = request.form.get("dateDebut", "").strip()

        # Validation et cast des données numériques
        try:
            heures = int(request.form.get("heures", 0))
            budget = float(request.form.get("budget", 0))
            salEmp = float(request.form.get("salEmp", 0))
            evalEmp_raw = request.form.get("evalEmp", "").strip()
            evalEmp = int(evalEmp_raw) if evalEmp_raw else None
        except ValueError:
            flash("Erreur de saisie : les heures, budget, salaire et évaluation doivent être numériques.", "danger")
            return redirect(url_for("nouvelle_affectation"))

        if not (nomProj and mgrProj and idEmp and nomEmp and dateDebut):
            flash("Veuillez renseigner tous les champs obligatoires.", "danger")
            return redirect(url_for("nouvelle_affectation"))

        conn, engine = get_db_connection()
        cursor = conn.cursor()
        param_placeholder = "%s" if engine == "postgres" else "?"

        insert_sql = f"""
            INSERT INTO projet (nomProj, mgrProj, idEmp, heures, nomEmp, budget, dateDebut, salEmp, mgrEmp, deptEmp, evalEmp)
            VALUES ({', '.join([param_placeholder] * 11)});
        """

        try:
            cursor.execute(
                insert_sql,
                (nomProj, mgrProj, idEmp, heures, nomEmp, budget, dateDebut, salEmp, mgrEmp, deptEmp, evalEmp)
            )
            conn.commit()
            flash("Affectation ajoutée avec succès !", "success")
            return redirect(url_for("projet_detail", nom_proj=nomProj))
        except Exception as e:
            conn.rollback()
            flash(f"Erreur lors de l'insertion (ex: contrainte d'unicité violée) : {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("nouveau.html")


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
