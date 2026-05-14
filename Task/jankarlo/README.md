# Jankarlo - Persona 2: Salones / Asientos / Tickets

Este repositorio contiene los microservicios para el módulo de gestión de salones, asientos y boletaje.

## Contexto del Proyecto
Se requiere el desarrollo de módulos independientes que consuman y gestionen:
* `app_id`
* `userauth_id`
* **Solo vía API** (Intercambio de datos JSON)

---

## Task 1 — $450 MXN (Entregable: Modelos, Migraciones y CRUD Base)

### Salones / asientos / tickets
* [x] **CRUD de salones**: Gestión de espacios físicos.
* [x] **Capacidad**: Control de aforo por salón.
* [x] **Zonas**: Configuración de áreas:
  * Piso alto
  * Piso bajo
  * Lateral
  * Preferente
* [ ] **Mapa de asientos**: Estructura de distribución de lugares.
* [ ] **Estados de asiento**: Gestión de estados (Disponible, Reservado, Ocupado).
* [ ] **Tickets básicos**: Generación de boletos base por evento.
* [ ] **Importación/Exportación**: Soporte para layouts y disponibilidad en `.csv`.

> [!IMPORTANT]
> Se otorgará carta de recomendación laboral una vez entregado satisfactoriamente el Task 1.

---

## Task 2 — $450 MXN (Entregable: Sistema de Reservas y Tickets)

### Reservas / tickets
* [ ] **Reservar asiento**: Proceso de selección y bloqueo de lugar.
* [ ] **Validar disponibilidad**: Verificación en tiempo real.
* [ ] **Liberar reserva**: Gestión de cancelaciones o tiempos de expiración.
* [ ] **Historial de reservas**: Registro de actividad por usuario.
* [ ] **Tickets por evento**: Generación detallada de boletaje.
* [ ] **Importación/Exportación**: Gestión de reservas en `.csv`.

