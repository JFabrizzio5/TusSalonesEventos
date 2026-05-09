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
    public function getById(string $id)
    {
        return Salon::find($id);
    }

    //Crear salon
    public function create(array $data)
    {
        return Salon::create($data);
    }

    //Actualizar salon
    public function update(string $id, array $data)
    {
        $salon = Salon::find($id);

        if (!$salon) {
            return null;
        }

        $salon -> update($data);
        return $salon;
    }

    // Eliminar
    public function delete(string $id)
    {
        $salon = Salon::find($id);

        if (!$salon) {
            return false;
        }

        return $salon->delete();
    }
}