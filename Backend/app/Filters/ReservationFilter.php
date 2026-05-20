<?php

namespace App\Filters;

use App\Filters\ApiFilter;

class ReservationFilter extends ApiFilter{
    // --- Filtro Base para API: Define parámetros seguros, mapeos de columnas y operadores permitidos ---
    protected $safeParms = [
        'userauth_id' => ['eq'],
        'status' => ['eq'],
        'guest_count' => ['gte', 'lte']

    ];
    protected $columnMap = [
        'userauth_id' => 'userauth_id',
        'status' => 'status',
        'guest_count' => 'guest_count'
    ];
    protected $operatorMap = [
        'eq' => '=',
        'gte' => '>=',
        'lte' => '<='
    ];
}