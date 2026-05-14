<?php

namespace App\Http\Controllers;

use Illuminate\Database\Eloquent\ModelNotFoundException;
use App\Services\SeatMapService;
use App\Utils\ApiResponse;

class SeatMapController extends Controller
{
    use ApiResponse;

    //Constructor para inyectar el servicio
    public function __construct(protected SeatMapService $seatMapService)
    {
    }

    /**
     * Obtener mapa de asientos de un salón
     */
    public function show(string $id)
    {
        try{
            $seatMap = $this->seatMapService->getSeatMap($id);
            return $this->success($seatMap);
        }catch(ModelNotFoundException){
            return $this->notFound();
        }catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Error retrieving seat map',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}