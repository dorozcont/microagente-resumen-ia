#!/usr/bin/env bash
set -e

# Asegura que tenemos las últimas refs/tags
git fetch origin --tags

# 1) Detectar cambios
CHANGED=$(git status --short | awk '{print $2}')
if [ -z "$CHANGED" ]; then
  echo "⚠️ No hay cambios detectados."
  exit 1
fi

# 2) Mensaje de commit
read -rp "📝 Escribe el mensaje de commit: " COMMIT_MSG

# 3) Tomar la ÚLTIMA versión estable desde la rama de desarrollo.
BASE_TAG=$(git describe --tags --abbrev=0 origin/dev 2>/dev/null || echo "v1.0.0")
BASE_NUM=${BASE_TAG#v}
IFS='.' read -r MAJOR MINOR PATCH <<<"$BASE_NUM"

# 4) Nuevo tag en dev = mismo MAJOR.MINOR, PATCH+1
NEW_PATCH=$((PATCH + 1))
NEW_TAG="v${MAJOR}.${MINOR}.${NEW_PATCH}"

# 5) Resumen
echo ""
echo "🚀 Preparando release..."
echo "   Archivos a commitear:"
echo "$CHANGED" | sed 's/^/     • /'
echo "   Branch destino: dev"
echo "   Commit:         $COMMIT_MSG"
echo "   Base (dev):    $BASE_TAG"
echo "   Nuevo tag:      $NEW_TAG"
echo ""
read -rp "❓ ¿Proceder con estos cambios? (y/n): " CONFIRM
[ "$CONFIRM" = "y" ] || { echo "❌ Operación cancelada."; exit 1; }

# 6) Ejecutar pipeline
git add .
git commit -m "$COMMIT_MSG" || echo "⚠️ No hay cambios que commitear"
git push origin dev

git tag "$NEW_TAG"
git push origin "$NEW_TAG"

echo "✅ Commit y tag $NEW_TAG publicados correctamente (branch dev)."