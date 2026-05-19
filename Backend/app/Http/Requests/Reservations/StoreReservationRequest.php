<?php

namespace App\Http\Requests\Reservations;

use Illuminate\Foundation\Http\FormRequest;

class StoreReservationRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'ticket_id' => 'required|integer|exists:tickets,id',
            'userauth_id' => 'required|string|max:255',
            'guest_count' => 'required|integer|min:1',
            'status' => 'sometimes|in:active,cancelled,completed'
        ];
    }

    public function messages(): array
    {
        return [
            'ticket_id.required' => 'El ticket es obligatorio',
            'ticket_id.exists' => 'El ticket no existe',

            'userauth_id.required' => 'El usuario es obligatorio',

            'guest_count.required' => 'La cantidad de invitados es obligatoria',
            'guest_count.integer' => 'La cantidad debe ser numérica',
            'guest_count.min' => 'Debe haber al menos 1 invitado',

            'status.in' => 'El estado no es válido'
        ];
    }
}