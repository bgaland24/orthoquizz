import csv
import os
import random
from models import Phrase, Score
from app import db


# ---------------------------------------------------------------------------
# Quiz — sélection des phrases
# ---------------------------------------------------------------------------

def selectionner_phrases(n: int = 10) -> list:
    """
    Sélectionne n phrases au hasard dans la base.
    Fonctionne même avec une seule phrase disponible.
    """
    phrases = Phrase.query.all()
    if not phrases:
        return []
    return random.sample(phrases, min(n, len(phrases)))


# ---------------------------------------------------------------------------
# Quiz — calcul des points
# ---------------------------------------------------------------------------

def calculer_points(phrase: Phrase, reponse_correcte: bool, temps_restant: int) -> int:
    """
    Calcule les points pour une question.
    - Mauvaise réponse ou timeout → 0 point
    - Bonne réponse → difficulte * (1 + temps_restant / temps_limite)
    """
    if not reponse_correcte:
        return 0
    bonus_temps = temps_restant / phrase.temps_limite
    return round(phrase.difficulte * (1 + bonus_temps))


# ---------------------------------------------------------------------------
# Quiz — informations visuelles selon la difficulté (style carte Pokémon)
# ---------------------------------------------------------------------------

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
                ))

            except (ValueError, KeyError) as e:
                errors.append(f'Ligne {i} : valeur invalide ({e}).')

    if errors:
        return False, ' | '.join(errors)

    Phrase.query.delete()
    db.session.bulk_save_objects(phrases)
    db.session.commit()
    return True, f'{len(phrases)} phrases chargées avec succès.'