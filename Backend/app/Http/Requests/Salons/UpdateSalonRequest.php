<?php

namespace App\Http\Requests\Salons;

use Illuminate\Foundation\Http\FormRequest;

class UpdateSalonRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'name'     => ['sometimes', 'string', 'max:255'],
            'capacity' => ['sometimes', 'integer', 'min:1'],
        ];
    }

    public function messages(): array
    {
        return [
            'name.max'         => 'El nombre no puede superar los 255 caracteres.',
            'capacity.integer' => 'La capacidad debe ser un número entero.',
            'capacity.min'     => 'La capacidad mínima es 1.',
        ];
    }
}