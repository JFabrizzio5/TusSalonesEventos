<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreEventRequest extends FormRequest
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
            'event_type_id' => ['required', 'integer', 'exists:event_types,id'],
            'title' => ['required', 'string', 'max:255'],
            'description' => ['nullable', 'string'],
            'metadata' => ['nullable', 'array'],
            'start_time' => ['required', 'date'],
            'end_time' => ['required', 'date', 'after:start_time'],
        ];
    }
}
