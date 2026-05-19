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
        $ticket = Ticket::with('seat')->findOrFail($data['ticket_id']);
        $seat = $ticket->seat;

        // Verificar que el estado del asiento
        if($seat->status === 'reserved'){
            throw new \Exception('El asiento ya está reservado');
        }
        if($seat->status === 'sold'){
            throw new \Exception('El asiento ya está vendido');
        }

        // Verificar si ya existe reservación activa
        $reservationExists = Reservation::where('ticket_id', $ticket->id)
            ->where('status', 'active')
            ->exists();

        if ($reservationExists) {
            throw new \Exception('El ticket ya tiene una reservación activa');
        }

        //Cambiar estado del asiento a reservado
        $seat->update([
            'status' => 'reserved'
        ]);

        //crear reservacion
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

        $seat=$reservation->ticket->seat;

        if($status === 'cancelled') {
            $seat->update([
                'status' => 'available'
            ]);
        }
        if($status === 'completed') {
            $seat->update([
                'status' => 'sold'
            ]);
        }

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
        
        $reservation->ticket->seat->update([
                'status' => 'available'
            ]);
        
        $reservation->delete();

        return true;
    }
}