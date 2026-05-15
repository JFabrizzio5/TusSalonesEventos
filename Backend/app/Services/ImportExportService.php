<?php

namespace App\Services;

use App\Models\Seat;
use App\Models\Zone;
use Illuminate\Support\Facades\DB;

class ImportExportService
{
    /**
     * Importar asientos desde CSV
     */
    public function importFromCSV(string $filePath): void
    {
        DB::beginTransaction();

        try {

            $file = fopen($filePath, 'r');

            // Obtener encabezados
            $headers = fgetcsv($file);

            while (($row = fgetcsv($file)) !== false) {

                $data = array_combine($headers, $row);

                // Buscar zona
                $zone = Zone::where('name', $data['zone'])->first();

                if (!$zone) {
                    continue;
                }

                // Evitar duplicados
                $seatExists = Seat::where('zone_id', $zone->id)
                    ->where('row', $data['row'])
                    ->where('number', $data['number'])
                    ->exists();

                if ($seatExists) {
                    continue;
                }

                Seat::create([
                    'zone_id' => $zone->id,
                    'row' => $data['row'],
                    'number' => $data['number'],
                    'status' => $data['status']
                ]);
            }

            fclose($file);

            DB::commit();

        } catch (\Exception $e) {

            DB::rollBack();

            throw $e;
        }
    }

    /**
     * Exportar asientos a CSV
     */
    public function exportToCSV(int $salonId, string $filePath): void
    {
        $file = fopen($filePath, 'w');

        // Encabezados
        fputcsv($file, [
            'zone',
            'row',
            'number',
            'status'
        ]);

        $zones = Zone::with('seats')
            ->where('salon_id', $salonId)
            ->get();

        foreach ($zones as $zone) {

            foreach ($zone->seats as $seat) {

                fputcsv($file, [
                    $zone->name,
                    $seat->row,
                    $seat->number,
                    $seat->status
                ]);
            }
        }

        fclose($file);
    }
}