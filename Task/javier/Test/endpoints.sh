#!/bin/bash

# ============================================
# TusSalonesEventos API - Endpoints en Curl
# ============================================

# Puerto por defecto de Laravel Sail es 80
# Si tienes APP_PORT configurado diferente, cámbialo aquí
BASE_URL="${BASE_URL:-http://localhost:80}"
APP_ID="${APP_ID:-app-a}"
USERAUTH_ID="${USERAUTH_ID:-user-a}"

echo "============================================"
echo "TusSalonesEventos API - Comandos Curl"
echo "============================================"
echo ""

# ============================================
# 1. List Event Types
# ============================================
echo "1. GET /api/event-types - Listar tipos de eventos"
echo "-------------------------------------------"
echo "curl -X GET \"$BASE_URL/api/event-types\""
curl -X GET "$BASE_URL/api/event-types"
echo ""
echo ""

# ============================================
# 2. List Events
# ============================================
echo "2. GET /api/events - Listar eventos"
echo "-------------------------------------------"
echo "curl -X GET \"$BASE_URL/api/events?app_id=$APP_ID&userauth_id=$USERAUTH_ID\""
curl -X GET "$BASE_URL/api/events?app_id=$APP_ID&userauth_id=$USERAUTH_ID"
echo ""
echo ""

# ============================================
# 3. Create Event
# ============================================
echo "3. POST /api/events - Crear evento"
echo "-------------------------------------------"
echo 'curl -X POST "$BASE_URL/api/events" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"'$APP_ID'\",
    \"userauth_id\": \"'$USERAUTH_ID'\",
    \"event_type_id\": 1,
    \"title\": \"Cumpleaños de Juan\",
    \"description\": \"Celebración de cumpleaños\",
    \"start_time\": \"2026-06-15T18:00:00\",
    \"end_time\": \"2026-06-15T22:00:00\"
  }"'
curl -X POST "$BASE_URL/api/events" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"userauth_id\": \"$USERAUTH_ID\",
    \"event_type_id\": 1,
    \"title\": \"Cumpleaños de Juan\",
    \"description\": \"Celebración de cumpleaños\",
    \"start_time\": \"2026-06-15T18:00:00\",
    \"end_time\": \"2026-06-15T22:00:00\"
  }"
echo ""
echo ""

# ============================================
# 4. Get Event
# ============================================
EVENT_ID=1
echo "4. GET /api/events/$EVENT_ID - Obtener evento específico"
echo "-------------------------------------------"
echo "curl -X GET \"$BASE_URL/api/events/$EVENT_ID?app_id=$APP_ID&userauth_id=$USERAUTH_ID\""
curl -X GET "$BASE_URL/api/events/$EVENT_ID?app_id=$APP_ID&userauth_id=$USERAUTH_ID"
echo ""
echo ""

# ============================================
# 5. Update Event
# ============================================
EVENT_ID=1
echo "5. PUT /api/events/$EVENT_ID - Actualizar evento"
echo "-------------------------------------------"
echo 'curl -X PUT "$BASE_URL/api/events/'$EVENT_ID'" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"'$APP_ID'\",
    \"userauth_id\": \"'$USERAUTH_ID'\",
    \"title\": \"Cumpleaños de Juan - Actualizado\",
    \"description\": \"Celebración actualizada\",
    \"start_time\": \"2026-06-15T19:00:00\",
    \"end_time\": \"2026-06-15T23:00:00\"
  }"'
curl -X PUT "$BASE_URL/api/events/$EVENT_ID" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"userauth_id\": \"$USERAUTH_ID\",
    \"title\": \"Cumpleaños de Juan - Actualizado\",
    \"description\": \"Celebración actualizada\",
    \"start_time\": \"2026-06-15T19:00:00\",
    \"end_time\": \"2026-06-15T23:00:00\"
  }"
echo ""
echo ""

# ============================================
# 6. Delete Event
# ============================================
EVENT_ID=1
echo "6. DELETE /api/events/$EVENT_ID - Eliminar evento"
echo "-------------------------------------------"
echo "curl -X DELETE \"$BASE_URL/api/events/$EVENT_ID?app_id=$APP_ID&userauth_id=$USERAUTH_ID\""
curl -X DELETE "$BASE_URL/api/events/$EVENT_ID?app_id=$APP_ID&userauth_id=$USERAUTH_ID"
echo ""
echo ""

# ============================================
# 7. Import Events (CSV/ICS)
# ============================================
echo "7. POST /api/events/import - Importar eventos"
echo "-------------------------------------------"
echo 'curl -X POST "$BASE_URL/api/events/import" \
  -F "app_id='$APP_ID'" \
  -F "userauth_id='$USERAUTH_ID'" \
  -F "format=csv" \
  -F "file=@events.csv"'
curl -X POST "$BASE_URL/api/events/import" \
  -F "app_id=$APP_ID" \
  -F "userauth_id=$USERAUTH_ID" \
  -F "format=csv" \
  -F "file=@events.csv"
echo ""
echo ""

# ============================================
# 8. Export Events (CSV/ICS)
# ============================================
echo "8. GET /api/events/export - Exportar eventos"
echo "-------------------------------------------"
echo "curl -X GET \"$BASE_URL/api/events/export?app_id=$APP_ID&userauth_id=$USERAUTH_ID&format=csv\""
curl -X GET "$BASE_URL/api/events/export?app_id=$APP_ID&userauth_id=$USERAUTH_ID&format=csv"
echo ""
echo ""

# ============================================
# 9. Calendar Week View
# ============================================
WEEK_START="2026-05-11"
echo "9. GET /api/calendar/week - Vista semanal del calendario"
echo "-------------------------------------------"
echo "curl -X GET \"$BASE_URL/api/calendar/week?app_id=$APP_ID&userauth_id=$USERAUTH_ID&week_start=$WEEK_START\""
curl -X GET "$BASE_URL/api/calendar/week?app_id=$APP_ID&userauth_id=$USERAUTH_ID&week_start=$WEEK_START"
echo ""
echo ""

# ============================================
# 10. Calendar Month View
# ============================================
YEAR=2026
MONTH=5
echo "10. GET /api/calendar/month - Vista mensual del calendario"
echo "-------------------------------------------"
echo "curl -X GET \"$BASE_URL/api/calendar/month?app_id=$APP_ID&userauth_id=$USERAUTH_ID&year=$YEAR&month=$MONTH\""
curl -X GET "$BASE_URL/api/calendar/month?app_id=$APP_ID&userauth_id=$USERAUTH_ID&year=$YEAR&month=$MONTH"
echo ""
echo ""

echo "============================================"
echo "Fin de los endpoints"
echo "============================================"