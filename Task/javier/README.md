# Javier - Persona 1: Calendario / Eventos

Este repositorio contiene los microservicios para el módulo de eventos y calendario.

## Contexto del Proyecto
Se requiere el desarrollo de módulos independientes que consuman y gestionen:
* `app_id`
* `userauth_id`
* **Solo vía API** (Intercambio de datos JSON)

---

## Task 1 — $450 MXN (Entregable: Modelos, Migraciones y CRUD Base)

### Calendario / eventos
* [X] **CRUD de eventos**: Creación, lectura, actualización y eliminación.
* [X] **Calendario**: Vista mensual y semanal.
* [X] **Filtros**: Por usuario (`userauth_id`), aplicación (`app_id`), fecha y tipo de evento.
* [X] **Validación de conflictos**: Evitar que se traslapen eventos en el mismo horario.
* [X] **Importación/Exportación**: Soporte para archivos `.csv` y `.ics`.
* [ ] **Tipos de evento**: Soporte dinámico para:
  * Cine
  * Torneo
  * Showcase
  * Sesión de DJs
  * Conferencias

> [!IMPORTANT]
> Se otorgará carta de recomendación laboral una vez entregado satisfactoriamente el Task 1.

---

## Task 2 — $450 MXN (Entregable: Demo y Funcionalidad Avanzada)

### Demo + exportaciones
* [ ] **Vista simple de calendario**: Interfaz funcional para visualización.
* [ ] **Gestión de eventos**: Interfaz para crear, editar y ver detalles.
* [ ] **Exportación .ics**: Generación de archivos para calendarios externos.
* [ ] **Google Wallet**: Generación de pase básico tipo Google Wallet.
