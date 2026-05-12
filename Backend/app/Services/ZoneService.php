<?php

namespace App\Services;

use App\Models\Zone;

class ZoneService
{
    public function getAll()
    {
        return Zone::get();
    }

    public function getById(int $id)
    {
        return Zone::findOrFail($id);
    }

    public function create(array $data)
    {
        return Zone::create($data);
    }

    public function update(int $id, array $data)
    {
        $zone = Zone::findOrFail($id);

        $zone->update($data);

        return $zone;
    }

    public function delete(int $id)
    {
        $zone = Zone::findOrFail($id);

        $zone->delete();

        return true;
    }
}