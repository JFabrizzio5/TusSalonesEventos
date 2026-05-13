<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Zone extends Model
{
    //Protected $fillable 
    protected $fillable = [
        'salon_id',
        'name'
    ];

    //Casting de tipos de datos
    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i:s',
        'updated_at' => 'datetime:Y-m-d H:i:s',
    ];
    
    //Relacion muchos a uno(salones-zonas)
    public function salon()
    {
        $this -> belongsTo(Salon::class);
    }
}
