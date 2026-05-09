<?php

namespace App\Filters;

use App\Filters\ApiFilter;

class CustomerFilter extends ApiFilter{
    // --- Filtro Base para API: Define parámetros seguros, mapeos de columnas y operadores permitidos ---
    protected $safeParms = [
        'name' => ['eq'],
        "app_id" => ['eq']
    ];
    protected $columnMap = [
        'name' => 'name',
        "app_id" => 'app_id'
    ];
    protected $operatorMap = [
        'eq' => '='
    ];
}