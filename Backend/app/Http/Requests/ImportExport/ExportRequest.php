<?php

namespace App\Http\Requests\ImportExport;

use Illuminate\Foundation\Http\FormRequest;

class ExportRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'salon_id' => [
                'required',
                'integer',
                'exists:salons,id'
            ]
        ];
    }

    public function messages(): array
    {
        return [
            'salon_id.required' => 'El id del salón es obligatorio.',
            'salon_id.integer' => 'El id del salón debe ser numérico.',
            'salon_id.exists' => 'El salón no existe.'
        ];
    }
}