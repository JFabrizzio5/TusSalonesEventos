<?php

namespace App\Http\Controllers;

use Illuminate\Database\Eloquent\ModelNotFoundException;
use App\Utils\ApiResponse;
use App\Services\TicketService;
use App\Http\Requests\Tickets\StoreTicketRequest;
use App\Http\Requests\Tickets\UpdateTicketRequest;

class TicketController extends Controller
{
    use ApiResponse;

    //Constructor para inyectar el servicio
    public function __construct(protected TicketService $ticketService)
    {
    }
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $tickets = $this->ticketService->getAll();
        return $this->success($tickets);
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        try{
            $ticket = $this->ticketService->getById($id);
            return $this->success($ticket);
        }catch(ModelNotFoundException){
            return $this -> notFound();
        }
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(StoreTicketRequest $request)
    {   
        try{
            $ticket = $this->ticketService->create($request->validated());
            return $this->success($ticket,'Ticket creado correctamente',201);
        }catch(ModelNotFoundException){
            return $this -> notFound();
        }
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateTicketRequest $request, string $id)
    {
        try{
            $ticket = $this->ticketService->update($id,$request->validated());
            return $this->success($ticket,'Ticket actualizado correctamente');
        }catch(ModelNotFoundException){
            return $this -> notFound();
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        try{
            $this->ticketService->delete($id);
            return $this->success(null, 'Ticket eliminado correctamente');
        }catch(ModelNotFoundException){
            return $this -> notFound();
        }
    }
}   