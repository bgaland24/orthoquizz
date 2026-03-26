import csv
import os
from models import Phrase
from app import db


def calculer_points(phrase: Phrase, reponse_correcte: bool, temps_restant: int) -> int:
    """
    Calcule les points marqués pour une question.

    Args:
        phrase           : la Phrase posée (contient difficulte et temps_limite)
        reponse_correcte : True si l'enfant a cliqué sur le bon mot
        temps_restant    : secondes restantes quand l'enfant a répondu (0 si timeout)

    Returns:
        int : points marqués pour cette question

    Formule :
        - Mauvaise réponse ou timeout → 0 point
        - Bonne réponse → difficulte * (1 + temps_restant / temps_limite)
          ex: difficulte=6, temps_limite=12, temps_restant=9
              → 6 * (1 + 9/12) = 6 * 1.75 = 10.5 → arrondi à 10
    """
    if not reponse_correcte:
        return 0
    bonus_temps = temps_restant / phrase.temps_limite
    points = phrase.difficulte * (1 + bonus_temps)
    return round(points)


def recharger_phrases(csv_path: str) -> tuple[bool, str]:
    """
    Vide la table Phrase et la recharge depuis le CSV.

    Returns:
        (True, message_succes) ou (False, message_erreur)
    """
    if not os.path.exists(csv_path):
        return False, f'Fichier introuvable : {csv_path}'

    colonnes_attendues = {'texte', 'mot_errone', 'position_mot', 'difficulte', 'temps_limite'}
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

                if not row['texte'].strip() or not row['mot_errone'].strip():
                    errors.append(f'Ligne {i} : texte ou mot_errone vide.')
                    continue

                phrases.append(Phrase(
                    texte        = row['texte'].strip(),
                    mot_errone   = row['mot_errone'].strip(),
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