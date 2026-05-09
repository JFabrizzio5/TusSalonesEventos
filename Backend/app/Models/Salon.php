<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Salon extends Model
{
    //Protecion contra asignacion masiva
    protected $table = 'salons';

    protected $fillable = [
        'name',
        'capacity',
        'app_id',
        'userauth_id'
    ];

    //Casting de tipos de datos
    protected $casts = [
        'created_at' => 'datetime:Y-m-d H:i:s',
        'updated_at' => 'datetime:Y-m-d H:i:s',
    ];

}
