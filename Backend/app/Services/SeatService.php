<?php

namespace App\Services;

use App\Models\Seat;
use Illuminate\Database\Eloquent\ModelNotFoundException;

class SeatService
{
    /**
     * Crear asiento
     */
    public function createSeat(array $data): Seat
    {
        return Seat::create($data);
    }

    /**
     * Actualizar asiento
     */
    public function updateSeat(int $id, array $data): Seat
    {
        $seat = Seat::findOrFail($id);

        $seat->update($data);

        return $seat;
    }

    /**
     * Cambiar estado del asiento
     */
    public function updateSeatStatus(int $id,string $status): Seat 
    {

        $seat = Seat::findOrFail($id);

        $seat->status = $status;

        $seat->save();

        return $seat;
    }
}