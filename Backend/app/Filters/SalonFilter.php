<?php

namespace App\Filters;

use App\Filters\ApiFilter;

class SalonFilter extends ApiFilter{
    // --- Filtro Base para API: Define parámetros seguros, mapeos de columnas y operadores permitidos ---
    protected $safeParms = [
        'name' => ['eq'],
        'app_id' => ['eq'],
        'capacity' => ['gte', 'lte']

    ];
    protected $columnMap = [
        'name' => 'name',
        "app_id" => 'app_id',
        "capacity" => 'capacity'
    ];
    protected $operatorMap = [
        'eq' => '=',
        'gte' => '>=',
        'lte' => '<='
    ];
}