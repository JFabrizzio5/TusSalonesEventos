<?php

namespace App\Http\Requests\ImportExport;

use Illuminate\Foundation\Http\FormRequest;

class ExportReservRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'event_id' => [
                'required',
                'integer',
                'exists:events,id'
            ]
        ];
    }

    public function messages(): array
    {
        return [
            'event_id.required' => 'El id del evento es obligatorio.',
            'event_id.integer' => 'El id del evento debe ser numérico.',
            'event_id.exists' => 'El evento no existe.'
        ];
    }
}