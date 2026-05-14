<?php

namespace App\Services;

use App\Models\Salon;
use Illuminate\Database\Eloquent\ModelNotFoundException;

class SeatMapService
{
    /**
     * Obtener mapa de asientos de un salón
     */

    public function getSeatMap(int $id): Salon
    {   
        
        $salon = Salon::with([
            //Ordenar zonas por nombre
            'zones' => function($query){
                $query->orderBy('name');
            },
            //Ordenar asientos por fila y numero
            'zones.seats' => function($query){
                $query->orderBy('row') -> orderBy('number');
            }
        ])->findOrFail($id);
        return $salon;
    }
}