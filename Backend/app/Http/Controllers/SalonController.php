<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\SalonService;
use App\Http\Requests\Salons\StoreSalonRequest;
use App\Http\Requests\Salons\UpdateSalonRequest;
use App\Filters\SalonFilter;
use Illuminate\Database\Eloquent\ModelNotFoundException;

class SalonController extends Controller
{
    public function __construct(protected SalonService $salonService)
    {
    }
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        //Filter
        $filter = new SalonFilter();
        $queryItems = $filter->transform($request); // [['column', 'operator', 'value']]

        //Get all salones /api/salons
        $salon = $this->salonService->getAll($queryItems);

        return $this->success($salon);
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        try{
            //GET /api/salons/{id}
            $salon = $this->salonService->getById($id);
            return $this ->success($salon);
        }catch(ModelNotFoundException){
            return $this -> notFound();
        }
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(StoreSalonRequest $request)
    {
        // POST /api/salons
        $salon = $this->salonService->create($request->validated());

        return $this->success(
            data: $salon,
            message: 'Salon creado correctamente',
            status: 201
        );
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateSalonRequest $request, string $id)
    {
        // PUT /api/salons/{id}
        try {
            $salon = $this->salonService->update($id, $request->validated());
            return $this->success($salon, 'Salón actualizado correctamente.');
        } catch (ModelNotFoundException) {
            return $this->notFound();
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        try{
            //DELETE /api/salons/{id}
            $this->salonService->delete($id);
            return $this->success(message: 'Salon eliminado correctamente');
        }catch(ModelNotFoundException){
            return $this -> notFound();
        }
    }

    /* -----------------------------------------------------------------------
    | Helpers privados para respuestas consistentes
    | ---------------------------------------------------------------------- */

    private function success(mixed $data = null, string $message = 'OK', int $status = 200)
    {
        $body = ['message' => $message];

        if (!is_null($data)) {
            $body['data'] = $data;
        }

        return response()->json($body, $status);
    }

    private function notFound(string $message = 'Salón no encontrado.')
    {
        return response()->json(['message' => $message], 404);
    }
}