<?php

namespace App\Services;

use App\Models\Salon;

class SalonService
{
    //Obtener todos los salones
    public function getAll()
    {
        return Salon::all();
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
}