<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class ExportEventsRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'app_id' => ['required', 'string', 'max:255'],
            'userauth_id' => ['required', 'string', 'max:255'],
            'format' => ['required', 'in:csv,ics'],
            'event_type_id' => ['sometimes', 'integer', 'exists:event_types,id'],
            'event_type_slug' => ['sometimes', 'string', 'max:255', 'exists:event_types,slug'],
            'start_time' => ['sometimes', 'date'],
            'end_time' => ['sometimes', 'date'],
        ];
    }
}
