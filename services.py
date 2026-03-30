import csv
import os
import random
from collections import defaultdict
from models import Phrase, Score
from app import db


# ---------------------------------------------------------------------------
# Quiz — sélection des phrases
# ---------------------------------------------------------------------------

def _un_par_groupe(phrases: list) -> list:
    """
    À partir d'une liste de phrases, retourne une liste où chaque groupe
    n'est représenté qu'une seule fois (choix aléatoire dans le groupe).
    Les phrases sans groupe sont toutes conservées.
    """
    groupes = defaultdict(list)
    sans_groupe = []
    for p in phrases:
        if p.groupe:
            groupes[p.groupe].append(p)
        else:
            sans_groupe.append(p)
    return sans_groupe + [random.choice(g) for g in groupes.values()]


def selectionner_phrases(n: int = 10, user_id: int = None) -> list:
    """
    Sélectionne n phrases adaptées au niveau du joueur, sans jamais
    proposer deux variantes d'une même phrase dans la même session.

    Règles (basées sur le score max du joueur) :
      - >= 700 pts  → phrases de difficulté >= 7
      - 400–699 pts → phrases de difficulté >= 4
      - < 400 pts   → phrases de difficulté <= 3
    Si la sélection ciblée est insuffisante, on complète avec d'autres
    phrases (en respectant toujours la contrainte de groupe).
    """
    if not Phrase.query.count():
        return []

    # Détermine la difficulté cible selon le score max du joueur
    score_max = 0
    if user_id is not None:
        top = (Score.query
                    .filter_by(user_id=user_id)
                    .order_by(Score.valeur.desc())
                    .first())
        if top:
            score_max = top.valeur

    if score_max >= 700:
        pool_cible = Phrase.query.filter(Phrase.difficulte >= 7).all()
    elif score_max >= 400:
        pool_cible = Phrase.query.filter(Phrase.difficulte >= 4).all()
    else:
        pool_cible = Phrase.query.filter(Phrase.difficulte <= 3).all()

    # Un seul représentant par groupe dans le pool ciblé
    pool_reduit = _un_par_groupe(pool_cible)
    random.shuffle(pool_reduit)
    selection = pool_reduit[:n]

    # Complète si nécessaire en respectant les groupes déjà représentés
    if len(selection) < n:
        ids_selectionnes  = {p.id for p in selection}
        groupes_deja      = {p.groupe for p in selection if p.groupe}
        reste             = Phrase.query.filter(Phrase.id.notin_(ids_selectionnes)).all()
        # Exclure les groupes déjà présents dans la sélection
        reste_filtre      = [p for p in reste if not p.groupe or p.groupe not in groupes_deja]
        pool_complement   = _un_par_groupe(reste_filtre)
        manquants         = n - len(selection)
        selection        += random.sample(pool_complement, min(manquants, len(pool_complement)))

    return selection


# ---------------------------------------------------------------------------
# Quiz — calcul des points
# ---------------------------------------------------------------------------

def calculer_points(phrase: Phrase, reponse_correcte: bool, temps_restant: int) -> int:
    """
    Calcule les points pour une question.
    - Mauvaise réponse ou timeout → 0 point
    - Bonne réponse → difficulte * (1 + temps_restant / temps_limite)
    """
    if not reponse_correcte or temps_restant < 0:
        return 0
    bonus_temps = min(0.90, temps_restant / phrase.temps_limite)
    return round(phrase.difficulte * (1 + bonus_temps))*10


# ---------------------------------------------------------------------------
# Quiz — informations visuelles selon la difficulté (style carte Pokémon)
# ---------------------------------------------------------------------------

POKEMON_NOMS = {
    1:   'Bulbizarre',
    4:   'Salamèche',
    7:   'Carapuce',
    37:  'Goupix',
    43:  'Mystherbe',
    54:  'Psykokwak',
    58:  'Caninos',
    63:  'Abra',
    69:  'Chétiflor',
    79:  'Ramoloss',
    132: 'Métamorph',
    133: 'Évoli',
    143: 'Ronflex',
    151: 'Mew',
    152: 'Germignon',
    155: 'Héricendre',
    158: 'Kaiminus',
    174: 'Toudoudou',
    175: 'Togepi',
    183: 'Marill',
    187: 'Houin',
    196: 'Mentali',
    218: 'Limagma',
    234: 'Cerfrousse',
}


def get_type_info(difficulte: int) -> dict:
    """Retourne le thème visuel de la carte selon la difficulté."""
    if difficulte <= 2:
        return {
            'nom': 'Normal',
            'gradient': 'linear-gradient(160deg, #E8E8D0 0%, #C6C6A7 50%, #A8A878 100%)',
            'couleur': '#A8A878',
            'emoji': '⭐',
            'faiblesse': '⚔️',
            'pokemon_ids': [133, 143, 132, 174, 234],   # Evoli, Ronflex, Métamorph, Toudoudou, Cerfrousse
        }
    elif difficulte <= 4:
        return {
            'nom': 'Plante',
            'gradient': 'linear-gradient(160deg, #D4F0B8 0%, #A7DB8D 50%, #78C850 100%)',
            'couleur': '#4a8f20',
            'emoji': '🌿',
            'faiblesse': '🔥',
            'pokemon_ids': [1, 43, 69, 152, 187],       # Bulbizarre, Mystherbe, Chétiflor, Germignon, Houin
        }
    elif difficulte <= 6:
        return {
            'nom': 'Eau',
            'gradient': 'linear-gradient(160deg, #C8D8F8 0%, #9DB7F5 50%, #6890F0 100%)',
            'couleur': '#2255c0',
            'emoji': '💧',
            'faiblesse': '⚡',
            'pokemon_ids': [7, 54, 79, 158, 183],       # Carapuce, Psykokwak, Ramoloss, Kaiminus, Marill
        }
    elif difficulte <= 8:
        return {
            'nom': 'Feu',
            'gradient': 'linear-gradient(160deg, #FAD0A0 0%, #F5AC78 50%, #F08030 100%)',
            'couleur': '#c05010',
            'emoji': '🔥',
            'faiblesse': '💧',
            'pokemon_ids': [4, 37, 58, 155, 218],       # Salamèche, Goupix, Caninos, Héricendre, Limagma
        }
    else:
        return {
            'nom': 'Psychique',
            'gradient': 'linear-gradient(160deg, #FAD0E0 0%, #FA92B2 50%, #F85888 100%)',
            'couleur': '#c01060',
            'emoji': '✨',
            'faiblesse': '👻',
            'pokemon_ids': [63, 79, 151, 175, 196],     # Abra, Ramoloss, Mew, Togepi, Mentali
        }


# ---------------------------------------------------------------------------
# Scores — sauvegarde et lecture
# ---------------------------------------------------------------------------

def sauvegarder_score(user_id: int, valeur: int) -> Score:
    """Enregistre un score en base et retourne l'objet créé."""
    score = Score(user_id=user_id, valeur=valeur)
    db.session.add(score)
    db.session.commit()
    return score


def get_derniers_scores(user_id: int, n: int = 5) -> list:
    """Retourne les n derniers scores d'un utilisateur, du plus récent au plus ancien."""
    return (Score.query
                 .filter_by(user_id=user_id)
                 .order_by(Score.date.desc())
                 .limit(n)
                 .all())


def get_top_scores(user_id: int, n: int = 3) -> list:
    """Retourne les n meilleurs scores d'un utilisateur, du plus élevé au plus bas."""
    return (Score.query
                 .filter_by(user_id=user_id)
                 .order_by(Score.valeur.desc())
                 .limit(n)
                 .all())


def get_rang_score(user_id: int, score_valeur: int) -> dict:
    """
    Retourne le rang du score parmi les scores du joueur et parmi tous les scores.
    rang_perso  : position du score parmi tous les scores du joueur (1 = meilleur)
    total_perso : nombre total de scores du joueur
    rang_global : position du score parmi tous les scores de tous les joueurs
    total_global: nombre total de scores en base
    """
    from sqlalchemy import func
    perso = db.session.query(
        func.count(Score.id).label('total'),
        func.sum((Score.valeur > score_valeur).cast(db.Integer)).label('mieux'),
    ).filter(Score.user_id == user_id).one()
    global_ = db.session.query(
        func.count(Score.id).label('total'),
        func.sum((Score.valeur > score_valeur).cast(db.Integer)).label('mieux'),
    ).one()
    total_perso  = perso.total
    rang_perso   = (perso.mieux  or 0) + 1
    total_global = global_.total
    rang_global  = (global_.mieux or 0) + 1
    return {
        'rang_perso':   rang_perso,
        'total_perso':  total_perso,
        'rang_global':  rang_global,
        'total_global': total_global,
    }


def get_voisins_classement(user_id: int, n: int = 2) -> list:
    """
    Retourne un classement autour du top score du joueur connecté :
    les n joueurs dont le top score est juste au-dessus, le joueur lui-même,
    et les n joueurs dont le top score est juste en-dessous.
    Chaque entrée : {'login': str, 'top_score': int, 'is_current': bool}
    """
    from models import User
    from sqlalchemy import func

    # Top score par joueur
    top_scores = (
        db.session.query(User.id, User.login, func.max(Score.valeur).label('top_score'))
        .join(Score, Score.user_id == User.id)
        .group_by(User.id)
        .order_by(func.max(Score.valeur).desc())
        .all()
    )

    # Trouver la position du joueur courant
    current_idx = next((i for i, row in enumerate(top_scores) if row.id == user_id), None)
    if current_idx is None:
        return []

    start = max(0, current_idx - n)
    end   = min(len(top_scores), current_idx + n + 1)
    return [
        {
            'login':      row.login,
            'top_score':  row.top_score,
            'is_current': row.id == user_id,
        }
        for row in top_scores[start:end]
    ]


def get_top10_classement(user_id: int) -> list:
    """
    Retourne le top 10 des joueurs par meilleur score.
    Chaque entrée : {'rang': int, 'login': str, 'top_score': int, 'is_current': bool}
    """
    from models import User
    from sqlalchemy import func

    top_scores = (
        db.session.query(User.id, User.login, func.max(Score.valeur).label('top_score'))
        .join(Score, Score.user_id == User.id)
        .group_by(User.id)
        .order_by(func.max(Score.valeur).desc())
        .limit(10)
        .all()
    )
    return [
        {
            'rang':       i + 1,
            'login':      row.login,
            'top_score':  row.top_score,
            'is_current': row.id == user_id,
        }
        for i, row in enumerate(top_scores)
    ]


# ---------------------------------------------------------------------------
# Admin — rechargement du CSV
# ---------------------------------------------------------------------------

def recharger_phrases(csv_path: str) -> tuple[bool, str]:
    """
    Vide la table Phrase et la recharge depuis le CSV.
    Valide toutes les lignes avant de toucher à la base.
    Returns: (True, message_succes) ou (False, message_erreur)
    """
    if not os.path.exists(csv_path):
        return False, f'Fichier introuvable : {csv_path}'

    colonnes_attendues = {'texte', 'mot_errone', 'mot_corrige',
                          'position_mot', 'difficulte', 'temps_limite'}
    errors  = []
    phrases = []

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)

        if not colonnes_attendues.issubset(set(reader.fieldnames or [])):
            return False, f'Colonnes manquantes. Attendues : {colonnes_attendues}'

        for i, row in enumerate(reader, start=2):
            try:
                difficulte   = int(row['difficulte'])
                temps_limite = int(row['temps_limite'])
                position_mot = int(row['position_mot'])

                if not (1 <= difficulte <= 10):
                    errors.append(f'Ligne {i} : difficulté hors intervalle (1-10).')
                    continue
                if temps_limite <= 0:
                    errors.append(f'Ligne {i} : temps_limite doit être positif.')
                    continue
                if not row['texte'].strip() or not row['mot_errone'].strip() or not row['mot_corrige'].strip():
                    errors.append(f'Ligne {i} : texte, mot_errone ou mot_corrige vide.')
                    continue

                phrases.append(Phrase(
                    texte        = row['texte'].strip(),
                    mot_errone   = row['mot_errone'].strip(),
                    mot_corrige  = row['mot_corrige'].strip(),
                    position_mot = position_mot,
                    difficulte   = difficulte,
                    temps_limite = temps_limite,
                    groupe       = row.get('groupe', '').strip() or None,
                ))

            except (ValueError, KeyError) as e:
                errors.append(f'Ligne {i} : valeur invalide ({e}).')

    if errors:
        return False, ' | '.join(errors)

    Phrase.query.delete()
    db.session.bulk_save_objects(phrases)
    db.session.commit()
    return True, f'{len(phrases)} phrases chargées avec succès.'