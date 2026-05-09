<?php

namespace Database\Seeders;

use App\Models\EventType;
use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        collect([
            ['name' => 'Cine', 'slug' => 'cine'],
            ['name' => 'Torneo', 'slug' => 'torneo'],
            ['name' => 'Showcase', 'slug' => 'showcase'],
            ['name' => 'Sesión de DJs', 'slug' => 'sesion-djs'],
            ['name' => 'Conferencias', 'slug' => 'conferencias'],
            ['name' => 'DJ Set', 'slug' => 'dj-set'],
            ['name' => 'Llamada de Zoom', 'slug' => 'llamada-de-zoom'],
        ])->each(fn (array $type) => EventType::query()->firstOrCreate(
            ['slug' => $type['slug']],
            ['name' => $type['name'], 'is_active' => true],
        ));
        // User::factory(10)->create();

        User::factory()->create([
            'name' => 'Test User',
            'email' => 'test@example.com',
        ]);
    }
}
