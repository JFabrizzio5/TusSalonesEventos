<?php

namespace App\Services;

use App\Models\Reservation;
use App\Models\Ticket;
use Illuminate\Database\Eloquent\ModelNotFoundException;

class ReservationService
{
    /**
     * Obtener todas las reservaciones
     */
    public function getAll()
    {
        return Reservation::with('ticket')->get();
    }

    /**
     * Obtener reservación por id
     */
    public function getById(int $id)
    {
        return Reservation::with('ticket')->findOrFail($id);
    }

    /**
     * Crear reservación
     */
    public function store(array $data)
    {
        // Verificar que exista el ticket
        $ticket = Ticket::findOrFail($data['ticket_id']);

        // Verificar si ya existe reservación activa
        $reservationExists = Reservation::where('ticket_id', $ticket->id)
            ->where('status', 'active')
            ->exists();

        if ($reservationExists) {
            throw new \Exception('El ticket ya tiene una reservación activa');
        }

        return Reservation::create($data);
    }

    /**
     * Actualizar reservación
     */
    public function update(int $id, array $data)
    {
        $reservation = Reservation::findOrFail($id);

        $reservation->update($data);

        return $reservation;
    }

    /**
     * Actualizar status
     */
    public function updateStatus(int $id, string $status)
    {
        $reservation = Reservation::findOrFail($id);

        $reservation->update([
            'status' => $status
        ]);

        return $reservation;
    }

    /**
     * Eliminar reservación
     */
    public function delete(int $id)
    {
        $reservation = Reservation::findOrFail($id);

        $reservation->delete();

        return true;
    }
}