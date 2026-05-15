<?php

namespace App\Services;

use App\Models\Ticket;

class TicketService
{
    public function getAll()
    {
        return Ticket::get();
    }

    public function getById(int $id)
    {
        return Ticket::findOrFail($id);
    }

    public function create(array $data)
    {   
        //Validar que el asiento exista y esté disponible
        $exists = Ticket::where('event_id', $data['event_id'])
                        ->where('seat_id', $data['seat_id'])
                        ->exists();

        if($exists){
            throw new \Exception('El asiento ya está reservado para este evento');
        }
        return Ticket::create($data);
    }

    public function update(int $id, array $data)
    {
        $ticket = Ticket::findOrFail($id);

        $ticket->update($data);

        return $ticket;
    }

    public function delete(int $id)
    {
        $ticket = Ticket::findOrFail($id);

        $ticket->delete();

        return true;
    }
}