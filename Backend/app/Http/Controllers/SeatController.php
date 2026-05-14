<?php

namespace App\Http\Controllers;

use App\Services\SeatService;
use App\Utils\ApiResponse;
use App\Http\Requests\Seats\StoreSeatRequest;
use App\Http\Requests\Seats\UpdateSeatRequest;
use App\Http\Requests\Seats\UpdateSeatStatusRequest;
use Illuminate\Database\Eloquent\ModelNotFoundException;

class SeatController extends Controller
{
    use ApiResponse;

    public function __construct(protected SeatService $seatService) 
    {
    }

    /**
     * Crear asiento
     */
    public function store(StoreSeatRequest $request)
    {
        try {
            $seat = $this->seatService->createSeat($request->validated());
            return $this->success($seat);
        } catch (ModelNotFoundException) {
            return $this->notFound();
        }
    }

    /**
     * Actualizar asiento
     */
    public function update(UpdateSeatRequest $request, string $id)
    {
        try {
            $seat = $this->seatService->updateSeat($id,$request->validated());
            return $this->success($seat);
        } catch (ModelNotFoundException) {
            return $this->notFound();
        } 
    }

    /**
     * Actualizar estado
     */
    public function updateStatus(UpdateSeatStatusRequest $request, string $id)
    {
        try {
            $seat = $this->seatService->updateSeatStatus($id,$request->validated());
            return $this->success($seat);
        } catch (ModelNotFoundException) {
            return $this->notFound();
        } 
    }
}