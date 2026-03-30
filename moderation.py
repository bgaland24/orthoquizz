# ---------------------------------------------------------------------------
# Modération des pseudos à l'inscription
# ---------------------------------------------------------------------------
# Ajouter ici tout mot à interdire. La vérification est insensible à la casse
# et détecte les mots inclus dans le pseudo (ex: "connard123" est refusé).

MOTS_INTERDITS = {
    # Insultes courantes
    "con", "conne", "connard", "connasse", "conasse",
    "couille", "couilles", "couillon",
    "enculé", "encule", "enculer","encul",
    "fdp",
    "merde", "merdes", "merdique",
    "putain", "pute", "putes",
    "salope", "salaud",
    "connerie", "conneries",
    "enfoiré", "enfoiree",
    "ordure", "ordures",
    "salopard",
    "branle", "branleur", "branleuse",
    "baisé", "baiser", "baise",
    "niquer", "nique","ntm","niquetamere"
    "bite", "bites",
    "chier", "chie", "chieur",
    "trouducul",
    "pénis", "penis", "zizi", "zob",
    "vagin", "vulve","clito", "clitoris",
    "porn", "porno",
    "pipi", "caca",
    "abruti", "abrutie",
    "bouffon", "bouffonne",
    "débile", "debile",
    "idiot", "idiote",
    "imbécile", "imbecile",
    "negro", "nègre", "negre",
    "nazi", "hitler",
    "pd", "pédé", "pede",
    "travelo",
    "tapette",
    "fumier",
    "bâtard", "batard",
    "gogol",
    "mongol",
    "attardé", "attarde",
    "chiotte", "chiottes",
    "fion",
    "teubé", "teube",
    "poufiasse",
    "pétasse", "petasse",
    "crevard",
    "naze",
    "bouffeur",
    "suce", "sucer",
    "suicide",
    "weed", "cannabis",
    "cocaine", "cocaïne",
    "heroine", "héroïne",
}


def login_est_autorise(login: str) -> bool:
    """Retourne False si le login contient un mot interdit (insensible à la casse)."""
    login_lower = login.lower()
    return not any(mot in login_lower for mot in MOTS_INTERDITS)
