<?php

namespace App\Http\Controllers;

use App\Http\Requests\Reservations\StoreReservationRequest;
use App\Http\Requests\Reservations\UpdateReservationRequest;
use App\Http\Requests\Reservations\UpdateReservationStatusRequest;
use App\Services\ReservationService;
use App\Utils\ApiResponse;
use Illuminate\Database\Eloquent\ModelNotFoundException;

class ReservationController extends Controller
{
    use ApiResponse;

    public function __construct(protected ReservationService $service)
    {
    }

    /**
     * Obtener todas las reservaciones
     */
    public function index()
    {
        try {
            $reservations = $this->service->getAll();

            return $this->success(
                $reservations,
                'Reservaciones obtenidas correctamente'
            );

        } catch (\Exception) {
            return $this->notFound();
        }
    }

    /**
     * Obtener reservación por id
     */
    public function show(int $id)
    {
        try {

            $reservation = $this->service->getById($id);

            return $this->success(
                $reservation,
                'Reservación obtenida correctamente'
            );

        } catch (ModelNotFoundException $e) {
            return $this->notFound();
        }
    }

    /**
     * Crear reservación
     */
    public function store(StoreReservationRequest $request)
    {
        try {

            $reservation = $this->service->store(
                $request->validated()
            );

            return $this->success(
                $reservation,
                'Reservación creada correctamente',
                201
            );

        } catch (ModelNotFoundException) {
            return $this->notFound();
        }
    }

    /**
     * Actualizar reservación
     */
    public function update(UpdateReservationRequest $request, int $id)
    {
        try {

            $reservation = $this->service->update(
                $id,
                $request->validated()
            );

            return $this->success(
                $reservation,
                'Reservación actualizada correctamente'
            );

        } catch (ModelNotFoundException $e) {

            return $this->notFound();
        }
    }

    /**
     * Actualizar status
     */
    public function updateStatus(
        UpdateReservationStatusRequest $request,
        int $id
    ) {
        try {

            $reservation = $this->service->updateStatus(
                $id,
                $request->validated()['status']
            );

            return $this->success(
                $reservation,
                'Estado actualizado correctamente'
            );

        } catch (ModelNotFoundException $e) {

            return $this->notFound();
        }
    }

    /**
     * Eliminar reservación
     */
    public function destroy(int $id)
    {
        try {

            $this->service->delete($id);

            return $this->success(
                null,
                'Reservación eliminada correctamente'
            );

        } catch (ModelNotFoundException $e) {

            return $this->notFound();
        }
    }
}