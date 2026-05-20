<?php

namespace App\Services;

use App\Models\Reservation;
use App\Models\Ticket;
use Illuminate\Support\Facades\DB;
use App\validators\ReservationValidator;

class ReservationService
{
    protected ReservationValidator $validator;

    public function __construct(ReservationValidator $validator)
    {
        $this->validator = $validator;
    }

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
        return DB::transaction(function () use ($data){
            // Verificar el ticket
            $ticket = Ticket::with('seat')->findOrFail($data['ticket_id']);
            $this->validator->validateTicketAvailability($ticket);
            
            //Cambiar estado del asiento a reservado
            $ticket->seat->update([
                'status' => 'reserved'
            ]);

            //crear reservacion
            return Reservation::create($data);
        });
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
        return DB::transaction(function () use ($id, $status){
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
        });
    }

    /**
     * Eliminar reservación
     */
    public function delete(int $id)
    {
        return DB::transaction(function () use ($id){
            $reservation = Reservation::findOrFail($id);
        
            $reservation->ticket->seat->update([
                    'status' => 'available'
                ]);
            
            $reservation->delete();

            return true;
        });
    }
}