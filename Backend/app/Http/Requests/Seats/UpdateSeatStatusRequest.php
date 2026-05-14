<?php

namespace App\Http\Requests\Seats;

use Illuminate\Foundation\Http\FormRequest;

class UpdateSeatStatusRequest extends FormRequest
{
    /**
     * Determine if the user is authorized.
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
            'status' => [
                'required',
                'in:available,reserved,sold'
            ]
        ];
    }

    /**
     * Mensajes personalizados
     */
    public function messages(): array
    {
        return [

            'status.required' => 'El estado es obligatorio.',

            'status.in' => 'El estado debe ser: available, reserved o sold.'
        ];
    }
}