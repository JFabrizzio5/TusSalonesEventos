<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\SalonService;

class SalonController extends Controller
{
    // Inyección de dependencia del servicio de Salones
    protected $salonService;

    public function __construct(SalonService $salonService)
    {
        $this->salonService = $salonService;
    }

    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        //Get all salones /api/salons
        $salon = $this->salonService->getAll();

        return response()->json($salon);
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        //GET /api/salons/{id}
        $salon = $this->salonService->getById($id);

        if (!$salon){
            return response()->json(['message' => 'Salon no encontrado'], 404);
        }
        return response()->json($salon);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        // POST /api/salons
        $validatedData = $request->validate([
            'name' => 'required|string|max:255',
            'capacity' => 'required|integer|min:1',
            'app_id' => 'required|string',
            'userauth_id' => 'required|string'
        ]);

        $salon = $this ->salonService->create($validatedData);

        return response()->json([
            'message' => 'Salon creado correctamente',
            'data' => $salon
        ], 201);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        // PUT /api/salons/{id}
        // Validar datos de entrada(solo los campos name y capacity pueden ser actualizados)
        $validatedData = $request->validate([
            'name' => 'sometimes|string|max:255',
            'capacity' => 'sometimes|integer|min:1'
        ]);

        $salon = $this ->salonService->update($id, $validatedData);

        if (!$salon){
            return response()->json(['message' => 'Salon no encontrado'], 404);
        }

        return response()->json([
            'message' => 'Salon actualizado correctamente',
            'data' => $salon
        ]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //DELETE /api/salons/{id}
        $deleted = $this->salonService->delete($id);

        if (!$deleted) {
            return response()->json([
                'message' => 'Salon no encontrado'
            ], 404);
        }

        return response()->json([
            'message' => 'Salon eliminado correctamente'
        ]);
    }
}
