<?php

namespace App\Http\Requests\Seats;

use Illuminate\Foundation\Http\FormRequest;

class StoreSeatRequest extends FormRequest
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
            'zone_id' => [
                'required',
                'integer',
                'exists:zones,id'
            ],

            'row' => [
                'required',
                'string',
                'max:10'
            ],

            'number' => [
                'required',
                'string',
                'max:10',
                'min:1'
            ],

            'status' => [
                'nullable',
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

            'zone_id.required' => 'La zona es obligatoria.',
            'zone_id.integer' => 'La zona debe ser un número entero.',
            'zone_id.exists' => 'La zona seleccionada no existe.',

            'row.required' => 'La fila es obligatoria.',
            'row.string' => 'La fila debe ser texto.',
            'row.max' => 'La fila no puede tener más de 10 caracteres.',

            'number.required' => 'El número del asiento es obligatorio.',
            'number.string' => 'El número del asiento debe ser texto.',
            'number.max' => 'El número del asiento no puede tener más de 10 caracteres.',
            'number.min' => 'El número del asiento debe ser un numero mayor a 0.',

            'status.in' => 'El estado debe ser: available, reserved o sold.'
        ];
    }
}