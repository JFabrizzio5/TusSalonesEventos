<?php

namespace App\Http\Requests\Seats;

use Illuminate\Foundation\Http\FormRequest;

class UpdateSeatRequest extends FormRequest
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
            'row' => [
                'sometimes',
                'string',
                'max:10'
            ],

            'number' => [
                'sometimes',
                'string',
                'max:10',
                'min:1'
            ],

            'status' => [
                'sometimes',
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

            'row.string' => 'La fila debe ser texto.',
            'row.max' => 'La fila no puede tener más de 10 caracteres.',

            'number.string' => 'El número del asiento debe ser texto.',
            'number.max' => 'El número del asiento no puede tener más de 10 caracteres.',
            'number.min' => 'El número del asiento debe ser un numero mayor a 0.',

            'status.in' => 'El estado debe ser: available, reserved o sold.'
        ];
    }
}