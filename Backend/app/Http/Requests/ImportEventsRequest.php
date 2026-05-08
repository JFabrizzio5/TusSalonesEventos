<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class ImportEventsRequest extends FormRequest
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
            'file' => ['required', 'file'],
        ];
    }
}
