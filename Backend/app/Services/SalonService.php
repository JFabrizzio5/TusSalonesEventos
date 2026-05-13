<?php

namespace App\Services;

use App\Models\Salon;
use App\Models\Reservation;

class SalonService
{
    //Obtener todos los salones
    public function getAll(array $filters = [])
    {
        $query = Salon::query();    
        //Validar si hay filtros
        if(!empty($filters)){
            $query -> where($filters);
        }
        return $query->get();
    }

    //Obtener un salon por id
    public function getById(string $id): Salon
    {
        return Salon::findOrFail($id);
    }

    //Crear salon
    public function create(array $data): Salon
    {
        return Salon::create($data);
    }

    //Actualizar salon
    public function update(string $id, array $data): Salon
    {
        $salon = Salon::findOrFail($id);
        
        $salon -> update($data);
        return $salon;
    }

    // Eliminar
    public function delete(string $id)
    {
        $salon = Salon::findOrFail($id);

        if (!$salon) {
            return false;
        }

        return $salon->delete();
    }
    // Obtener la capacidad de un salon
    public function getCapacity(string $id)
    {
        $salon = Salon::findOrFail($id);
        
        //Obtener el numero de personas registradas en las reservas del salon
        $registeredPeople = Reservation::where('status', 'active')
            ->sum('guest_count');

        //lugares restantes
        $remainingCapacity = $salon->capacity - $registeredPeople;

        return [
            'salon_id'            => $salon->id,
            'salon_name'          => $salon->name,
            'capacity'            => $salon->capacity,
            'registered_people'  => $registeredPeople,
            'remaining_capacity' => max($remainingCapacity, 0),
            'is_full'             => $remainingCapacity <= 0,
        ];
    }
}