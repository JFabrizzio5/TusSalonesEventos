<?php

namespace App\Http\Requests\Tickets;

use Illuminate\Foundation\Http\FormRequest;

class UpdateTicketRequest extends FormRequest
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

            'event_id' => 'sometimes|exists:events,id',

            'seat_id' => 'sometimes|exists:seats,id',

            'price' => 'sometimes|numeric|min:0'
        ];
    }

    /**
     * Mensajes personalizados
     */
    public function messages(): array
    {
        return [

            'event_id.exists' => 'El evento no existe.',

            'seat_id.exists' => 'El asiento no existe.',

            'price.numeric' => 'El precio debe ser numérico.',
            'price.min' => 'El precio no puede ser negativo.'
        ];
    }
}