from models import Phrase


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