#!/usr/bin/env bash
set -e

# Asegura que tenemos las últimas refs/tags
git fetch origin --tags

# 1) Detectar cambios
CHANGED=$(git status --short | awk '{print $2}')
if [ -z "$CHANGED" ]; then
  echo "⚠️ No hay cambios detectados para el commit."
  exit 1
fi

# 2) Mensaje de commit
read -rp "📝 Escribe el mensaje de commit: " COMMIT_MSG

# 3) Tomar la ÚLTIMA versión estable desde la rama de desarrollo.
#    Usamos 'origin/dev' para obtener el tag más reciente de esa rama remota.
BASE_TAG=$(git describe --tags --abbrev=0 origin/dev 2>/dev/null || echo "v1.0.0")
BASE_NUM=${BASE_TAG#v}
IFS='.' read -r MAJOR MINOR PATCH <<<"$BASE_NUM"

# 4) Preguntar por el tipo de incremento
echo ""
echo "Tipo de incremento actual (base: $BASE_TAG):"
echo "  1) Patch (vX.Y.Z+1) - Correcciones de errores pequeñas"
echo "  2) Minor (vX.Y+1.0) - Nuevas funcionalidades compatibles con versiones anteriores"
echo "  3) Major (vX+1.0.0) - Cambios incompatibles con versiones anteriores (breaking changes)"
echo ""
read -rp "❓ Selecciona el tipo de incremento (1, 2, o 3): " INCREMENT_TYPE

# 5) Calcular el nuevo tag
NEW_MAJOR=$MAJOR
NEW_MINOR=$MINOR
NEW_PATCH=$PATCH

case "$INCREMENT_TYPE" in
    1)
        # Patch: incrementa PATCH, mantiene MAJOR y MINOR
        NEW_PATCH=$((PATCH + 1))
        ;;
    2)
        # Minor: incrementa MINOR, resetea PATCH a 0
        NEW_MINOR=$((MINOR + 1))
        NEW_PATCH=0
        ;;
    3)
        # Major: incrementa MAJOR, resetea MINOR y PATCH a 0
        NEW_MAJOR=$((MAJOR + 1))
        NEW_MINOR=0
        NEW_PATCH=0
        ;;
    *)
        echo "❌ Tipo de incremento no válido. Operación cancelada."
        exit 1
        ;;
esac

NEW_TAG="v${NEW_MAJOR}.${NEW_MINOR}.${NEW_PATCH}"

# 6) Resumen
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

# 7) Ejecutar pipeline
git add .
git commit -m "$COMMIT_MSG" || echo "⚠️ No hay cambios que commitear"
git push origin dev

git tag "$NEW_TAG"
git push origin "$NEW_TAG"

echo "✅ Commit y tag $NEW_TAG publicados correctamente (branch dev)."