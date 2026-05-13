<?php

namespace App\Http\Requests\Zones;

use Illuminate\Foundation\Http\FormRequest;

class StoreZoneRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     */
    public function rules(): array
    {
        return [
            'salon_id' => 'required|exists:salons,id',
            'name' => [
                'required',
                'string',
                'max:255',
                'in:Piso Alto,Piso Bajo,Lateral,Preferente'
            ],
        ];
    }

    /**
     * Custom validation messages.
     */
    public function messages(): array
    {
        return [
            'salon_id.required' => 'El salón es obligatorio.',
            'salon_id.exists' => 'El salón seleccionado no existe.',

            'name.required' => 'El nombre de la zona es obligatorio.',
            'name.string' => 'El nombre debe ser texto.',
            'name.max' => 'El nombre no debe superar 255 caracteres.',
            'name.in' => 'La zona debe ser: Piso Alto, Piso Bajo, Lateral o Preferente.',
        ];
    }
}