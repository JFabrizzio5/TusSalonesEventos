<?php

namespace App\Http\Requests\Reservations;

use Illuminate\Foundation\Http\FormRequest;

class UpdateReservationRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'guest_count' => 'sometimes|integer|min:1',
            'status' => 'sometimes|in:active,cancelled,completed'
        ];
    }

    public function messages(): array
    {
        return [
            'guest_count.integer' => 'La cantidad debe ser numérica',
            'guest_count.min' => 'Debe haber al menos 1 invitado',

            'status.in' => 'El estado no es válido'
        ];
    }
}