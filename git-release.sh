#!/usr/bin/env bash
set -e

# Asegura que tenemos las últimas refs/tags
git fetch origin --tags

# ----------------------------------------------------
# FASE 1: CREAR NUEVA VERSIÓN EN 'dev'
# ----------------------------------------------------
echo "=== FASE 1: CREACIÓN DE NUEVO RELEASE EN 'dev' ==="

# 1) Detectar cambios
CHANGED=$(git status --short | awk '{print $2}')
if [ -z "$CHANGED" ]; then
  echo "⚠️ No hay cambios detectados para el commit."
  # Añadimos un paso para preguntar si desea saltarse el commit y pasar a Prod
  read -rp "❓ ¿Desea continuar e intentar promocionar la ÚLTIMA versión de 'dev' a 'prod'? (y/n): " SKIP_COMMIT
  if [ "$SKIP_COMMIT" = "y" ]; then
    COMMIT_MSG="[Salto de commit]"
    BASE_TAG=$(git describe --tags --abbrev=0 origin/dev 2>/dev/null || echo "v1.0.0")
    NEW_TAG=$BASE_TAG
    echo "Saltando commit. La versión a promocionar será $BASE_TAG."
    # Ir directamente a la fase de promoción
    goto_promotion=true
  else
    echo "❌ Operación cancelada."
    exit 1
  fi
fi

if [ -z "$goto_promotion" ]; then
  # 2) Mensaje de commit
  read -rp "📝 Escribe el mensaje de commit para 'dev': " COMMIT_MSG

  # 3) Tomar la ÚLTIMA versión estable desde la rama de desarrollo.
  BASE_TAG=$(git describe --tags --abbrev=0 origin/dev 2>/dev/null || echo "v1.0.0")
  BASE_NUM=${BASE_TAG#v}
  IFS='.' read -r MAJOR MINOR PATCH <<<"$BASE_NUM"

  # 4) Preguntar por el tipo de incremento
  echo ""
  echo "Tipo de incremento actual (base: $BASE_TAG):"
  echo "  1) Patch (vX.Y.Z+1) - Correcciones de errores pequeñas"
  echo "  2) Minor (vX.Y+1.0) - Nuevas funcionalidades"
  echo "  3) Major (vX+1.0.0) - Cambios incompatibles"
  echo ""
  read -rp "❓ Selecciona el tipo de incremento (1, 2, o 3): " INCREMENT_TYPE

  # 5) Calcular el nuevo tag
  NEW_MAJOR=$MAJOR
  NEW_MINOR=$MINOR
  NEW_PATCH=$PATCH

  case "$INCREMENT_TYPE" in
      1)
          NEW_PATCH=$((PATCH + 1))
          ;;
      2)
          NEW_MINOR=$((MINOR + 1))
          NEW_PATCH=0
          ;;
      3)
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

  # 6) Resumen y Confirmación de la Fase 1
  echo ""
  echo "🚀 Resumen de Release en 'dev':"
  echo "   Archivos a commitear:"
  echo "$CHANGED" | sed 's/^/     • /'
  echo "   Branch destino: dev"
  echo "   Commit:         $COMMIT_MSG"
  echo "   Base (dev):    $BASE_TAG"
  echo "   Nuevo tag:      $NEW_TAG"
  echo ""
  read -rp "❓ ¿Proceder con el COMMIT y TAG en 'dev'? (y/n): " CONFIRM_DEV
  [ "$CONFIRM_DEV" = "y" ] || { echo "❌ Operación cancelada."; exit 1; }

  # 7) Ejecutar pipeline de DEV
  git add .
  git commit -m "$COMMIT_MSG" || echo "⚠️ No hay cambios que commitear"
  git push origin dev

  git tag "$NEW_TAG"
  git push origin "$NEW_TAG"

  echo "✅ Commit y tag $NEW_TAG publicados correctamente (branch dev)."
  echo ""
fi

# ---
## ---
## ---

# ----------------------------------------------------
# FASE 2: PROMOCIÓN DE 'dev' A 'prod'
# ----------------------------------------------------
echo "=== FASE 2: PROMOCIÓN A PRODUCCIÓN ==="
read -rp "⭐ ¿Desea promocionar la versión $NEW_TAG (de 'dev') a la rama 'prod'? (y/n): " PROMOTE_PROD

if [ "$PROMOTE_PROD" = "y" ]; then
    echo "Procesando promoción de $NEW_TAG a 'prod'..."

    # Asegura estar en 'dev' para el merge y tener las últimas versiones
    git checkout dev
    git pull origin dev

    # 1) Checkout a prod
    git checkout prod

    # 2) Pull para tener la última versión de prod (fundamental para evitar conflictos)
    git pull origin prod

    # 3) Merge de dev a prod
    if git merge --no-ff dev -m "Merge branch 'dev' for Production Release $NEW_TAG"; then
        echo "✅ Merge de 'dev' a 'prod' completado."

        # 4) Crear un tag de producción (opcional, pero buena práctica)
        PROD_TAG="prod-$NEW_TAG"
        
        echo "   Nuevo tag de Producción: $PROD_TAG"
        git tag "$PROD_TAG"

        # 5) Push a prod y el nuevo tag de producción
        git push origin prod
        git push origin "$PROD_TAG"

        echo "🎉 ¡Éxito! La versión $NEW_TAG ha sido promocionada a 'prod' y etiquetada como $PROD_TAG."
    else
        echo "❌ Falló el merge de 'dev' a 'prod'. Revise y resuelva los conflictos manualmente."
        # Deja al usuario en la rama 'prod' para resolver el conflicto
        exit 1
    fi

    # 6) Volver a la rama 'dev' (por si acaso)
    git checkout dev

else
    echo "▶️ No se solicitó la promoción a 'prod'. Proceso de release finalizado en 'dev'."
fi