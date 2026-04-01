"""
Script de migration sans perte de données.

"""

import os
import sys

# ── 1. Migration Alembic ──────────────────────────────────────────────────────
print("=== Étape 1 : migration de la base de données ===")
exit_code = os.system("flask db upgrade")
if exit_code != 0:
    print("ERREUR : flask db upgrade a échoué. Abandon.")
    sys.exit(1)
print("Migration appliquée.\n")
