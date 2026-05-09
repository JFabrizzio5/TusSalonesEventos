<?php

namespace App\Http\Requests\Salons;

use Illuminate\Foundation\Http\FormRequest;

class StoreSalonRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'name'        => ['required', 'string', 'max:255'],
            'capacity'    => ['required', 'integer', 'min:1'],
            'app_id'      => ['required', 'string'],
            'userauth_id' => ['required', 'string'],
        ];
    }

    public function messages(): array
    {
        return [
            'name.required'        => 'El nombre del salón es obligatorio.',
            'name.max'             => 'El nombre no puede superar los 255 caracteres.',
            'capacity.required'    => 'La capacidad es obligatoria.',
            'capacity.integer'     => 'La capacidad debe ser un número entero.',
            'capacity.min'         => 'La capacidad mínima es 1.',
            'app_id.required'      => 'El app_id es obligatorio.',
            'userauth_id.required' => 'El userauth_id es obligatorio.',
        ];
    }
}