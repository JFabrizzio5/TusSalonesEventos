<?php

namespace App\Validators;

use App\Models\Reservation;
use App\Models\Ticket;

class ReservationValidator
{
    /**
     * Validar disponibilidad del ticket/asiento
     */
    public function validateTicketAvailability(Ticket $ticket): void
    {
        $seat = $ticket->seat;
        /**
         * Validar estado del asiento
         */
        if ($seat->status === 'reserved') {
            throw new \Exception('El asiento ya está reservado');
        }
        if ($seat->status === 'sold') {
            throw new \Exception('El asiento ya está vendido');
        }
        /**
         * Validar reservación activa
         */
        $reservationExists = Reservation::where('ticket_id', $ticket->id)
            ->where('status', 'active')
            ->exists();
        if ($reservationExists) {
            throw new \Exception(
                'El ticket ya tiene una reservación activa'
            );
        }
    }
}