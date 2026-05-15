<?php

namespace App\Http\Requests\ImportExport;

use Illuminate\Foundation\Http\FormRequest;

class ImportRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'file' => [
                'required',
                'file',
                'mimes:csv,txt',
                'max:2048'
            ]
        ];
    }

    public function messages(): array
    {
        return [
            'file.required' => 'El archivo CSV es obligatorio.',
            'file.file' => 'Debe subir un archivo válido.',
            'file.mimes' => 'El archivo debe ser formato CSV.',
            'file.max' => 'El archivo no puede superar los 2MB.'
        ];
    }
}