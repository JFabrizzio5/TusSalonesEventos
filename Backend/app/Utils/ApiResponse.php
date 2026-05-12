<?php

namespace App\Utils;

use Illuminate\Http\JsonResponse;

/**
 * Trait ApiResponse
 *
 * Centraliza las respuestas JSON de la API para mantener
 * un formato consistente en todos los controladores.
 *
 * Uso:
 *   use App\Utils\ApiResponse;
 *
 *   class MiController extends Controller
 *   {
 *       use ApiResponse;
 *   }
 */
trait ApiResponse
{
    /* ------------------------------------------------------------------
    | Respuesta exitosa
    | ------------------------------------------------------------------ */

    /**
     * Devuelve una respuesta JSON de éxito.
     *
     * @param  mixed       $data    Payload a incluir (null = se omite la clave 'data')
     * @param  string      $message Mensaje descriptivo
     * @param  int         $status  Código HTTP (default 200)
     */
    protected function success(
        mixed $data = null,
        string $message = 'OK',
        int $status = 200
    ): JsonResponse {
        $body = ['message' => $message];

        if (!is_null($data)) {
            $body['data'] = $data;
        }

        return response()->json($body, $status);
    }

    /* ------------------------------------------------------------------
    | Respuestas de error
    | ------------------------------------------------------------------ */

    /**
     * Devuelve una respuesta JSON 404 Not Found.
     *
     * @param  string  $message  Mensaje de error personalizable
     */
    protected function notFound(string $message = 'Recurso no encontrado.'): JsonResponse
    {
        return $this->error($message, 404);
    }

    /**
     * Devuelve una respuesta JSON 400 Bad Request.
     *
     * @param  string  $message  Mensaje de error personalizable
     */
    protected function badRequest(string $message = 'Solicitud inválida.'): JsonResponse
    {
        return $this->error($message, 400);
    }

    /**
     * Devuelve una respuesta JSON 401 Unauthorized.
     *
     * @param  string  $message  Mensaje de error personalizable
     */
    protected function unauthorized(string $message = 'No autenticado.'): JsonResponse
    {
        return $this->error($message, 401);
    }

    /**
     * Devuelve una respuesta JSON 403 Forbidden.
     *
     * @param  string  $message  Mensaje de error personalizable
     */
    protected function forbidden(string $message = 'Acceso denegado.'): JsonResponse
    {
        return $this->error($message, 403);
    }

    /**
     * Devuelve una respuesta JSON 422 Unprocessable Entity.
     *
     * @param  mixed   $errors  Errores de validación (array o string)
     * @param  string  $message Mensaje de error personalizable
     */
    protected function validationError(
        mixed $errors = null,
        string $message = 'Error de validación.'
    ): JsonResponse {
        $body = ['message' => $message];

        if (!is_null($errors)) {
            $body['errors'] = $errors;
        }

        return response()->json($body, 422);
    }

    /**
     * Devuelve una respuesta JSON 500 Internal Server Error.
     *
     * @param  string  $message  Mensaje de error personalizable
     */
    protected function serverError(string $message = 'Error interno del servidor.'): JsonResponse
    {
        return $this->error($message, 500);
    }

    /* ------------------------------------------------------------------
    | Helper base de error (uso interno del trait)
    | ------------------------------------------------------------------ */

    /**
     * Construye cualquier respuesta de error con un código arbitrario.
     *
     * @param  string  $message  Mensaje descriptivo
     * @param  int     $status   Código HTTP de error
     */
    protected function error(string $message, int $status): JsonResponse
    {
        return response()->json(['message' => $message], $status);
    }
}