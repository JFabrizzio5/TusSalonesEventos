<?php

namespace App\Services;

use App\Models\Reservation;
use App\Models\Ticket;
use Illuminate\Support\Facades\DB;

class ImportExportReservService
{
    /**
     * Importar reservaciones desde CSV
     */
    public function importReservationsFromCSV(string $filePath): void
    {
        DB::beginTransaction();

        try {

            $file = fopen($filePath, 'r');

            $headers = fgetcsv($file);

            while (($row = fgetcsv($file)) !== false) {
                $data = array_combine($headers, $row);
                // Validar ticket
                $ticket = Ticket::find($data['ticket_id']);
                if (!$ticket) {
                    continue;
                }

                // Evitar duplicados
                $reservationExists = Reservation::where('ticket_id', $data['ticket_id'])->exists();
                    
                if ($reservationExists) {
                    continue;
                }

                Reservation::create([
                    'ticket_id' => $data['ticket_id'],
                    'userauth_id' => $data['userauth_id'],
                    'guest_count' => $data['guest_count'],
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

    public function exportReservationsFromCSV(int $eventId, string $filePath): void
    {
        $file = fopen($filePath, 'w');

        fputcsv($file, [
            'reservation_id',
            'ticket_id',
            'userauth_id',
            'guest_count',
            'status'
        ]);

        $reservations = Reservation::whereHas(
            'ticket',
            function ($query) use ($eventId) {
                $query->where('event_id', $eventId);
            }
        )->get();

        foreach ($reservations as $reservation) {

            fputcsv($file, [
                $reservation->id,
                $reservation->ticket_id,
                $reservation->userauth_id,
                $reservation->guest_count,
                $reservation->status
            ]);
        }

        fclose($file);
    }
}