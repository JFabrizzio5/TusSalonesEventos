<?php

namespace App\Filters;
use Illuminate\Http\Request;


class ApiFilter{
    // --- Filtro Base para API: Define parámetros seguros, mapeos de columnas y operadores permitidos ---
    protected $safeParms = [];
    protected $columnMap = [];
    protected $operatorMap = [];

    public function transform(Request $request){
        $eloQuery = [];
        foreach ($this->safeParms as $parm => $operators) {
            $query = $request->query($parm);
            if (!isset($query)) continue;

            $column = $this->columnMap[$parm] ?? $parm;
            foreach ($operators as $operator) {
                if (isset($query[$operator])) {
                    $eloQuery[] = [$column, $this->operatorMap[$operator], $query[$operator]];
                }
            }
        }
        return $eloQuery;
    }
}