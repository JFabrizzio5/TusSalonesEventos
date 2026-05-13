<?php

namespace App\Http\Controllers;

use Illuminate\Database\Eloquent\ModelNotFoundException;
use App\Services\ZoneService;
use App\Utils\ApiResponse;
use App\Http\Requests\Zones\StoreZoneRequest;
use App\Http\Requests\Zones\UpdateZoneRequest;


class ZoneController extends Controller
{
    use ApiResponse;

    //Constructor para inyectar el servicio
    public function __construct(protected ZoneService $zoneService)
    {
    }
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $zones = $this->zoneService->getAll();

        return $this->success($zones);
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        try{
            $zone = $this->zoneService->getById($id);
            return $this->success($zone);
        }catch(ModelNotFoundException){
            return $this -> notFound();
        }
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(StoreZoneRequest $request)
    {   try{
            $zone = $this->zoneService->create($request->validated());
            return $this->success($zone, 'Zona creada correctamente', 201);
        }catch(ModelNotFoundException){
            return $this->notFound();
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateZoneRequest $request, string $id)
    {
        try{
            $zone = $this->zoneService->update($id, $request->validated());
            return $this->success($zone, 'Zona actualizada correctamente');
        }catch(ModelNotFoundException){
            return $this->notFound();
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        try{
            $this->zoneService->delete($id);

            return $this->success(message: 'Zona eliminada correctamente');
        }catch(ModelNotFoundException){
            return $this->notFound();
        }
    }
}