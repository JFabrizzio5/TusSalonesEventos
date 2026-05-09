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
}
