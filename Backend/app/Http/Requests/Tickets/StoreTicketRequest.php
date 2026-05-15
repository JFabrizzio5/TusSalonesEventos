<?php

namespace App\Http\Requests\Tickets;

use Illuminate\Foundation\Http\FormRequest;

class StoreTicketRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true;
    }

    /**
     * Reglas de validación
     */
    public function rules(): array
    {
        return [
            'event_id' => 'required|exists:events,id',

            'seat_id' => 'required|exists:seats,id',

            'price' => 'required|numeric|min:0'
        ];
    }

    /**
     * Mensajes personalizados
     */
    public function messages(): array
    {
        return [

            'event_id.required' => 'El evento es obligatorio.',
            'event_id.exists' => 'El evento no existe.',

            'seat_id.required' => 'El asiento es obligatorio.',
            'seat_id.exists' => 'El asiento no existe.',

            'price.required' => 'El precio es obligatorio.',
            'price.numeric' => 'El precio debe ser numérico.',
            'price.min' => 'El precio no puede ser negativo.'
        ];
    }
}