<?php

namespace Utils;

use Utils\Database;
use Utils\DBManager;
use Utils\Logger;
use Utils\EmailService;
use Models\ResponseWithMessage;
use Models\ReporteModel;
//use Controllers\ReporteController;


class CiberReportes {

    private DBManager $DBManager;
    private Logger $log;

    public function __construct() {
        $db = new Database();
        $this->manager = new DBManager($db);
        $this->log = new Logger();
    }

    //CATALOGOS
    public function GetEstados(): ResponseWithMessage {
        $response = new ResponseWithMessage();

        try{
            $query ="select id_estado AS ID, nombre ESTADO from fn_retorna_estados(0);";
            $json = $this->manager->multipleSelect($query);
            $data = json_decode($json, true);
            //var_dump($data);
            if(empty($data)){
                $response->status = false;
                $response->message = "consulta sin datos";
                $response->entidades = null;
                $this->log->error("consulta 'select id_estado AS ID, nombre ESTADO from fn_retorna_estados();' sin datos");
            }else{
                $response->status = true;
                $response->message = "Consulta exitosa";
                $response->entidades = json_decode($json, true);
            }
        }catch(\Exception $e){
            $response->status = false;
            $response->message = "Error al obtener catalogo de estados";
            $this->log->error("Error en GetEstados: " . $e->getMessage());
        }
        return $response;
    }

    public function GetMunicipios($idEntidad): ResponseWithMessage {
        $response = new ResponseWithMessage();

        try{       
            $query = "select id_estado AS ID_ENTIDAD, id_municipio AS ID_MUNICIPIO, nombre as MUNICIPIO
                    from fn_retorna_mpiosxedo(:idEntidad)";
            $json = $this->manager->multipleSelect($query, [':idEntidad' => (int)$idEntidad]);
            $data = json_decode($json, true);
            //var_dump($data);
            if(empty($data)){
                $response->status = false;
                $response->message = "consulta sin datos";
                $response->municipios = null;
                $this->log->error("consulta 'fn_retorna_mpiosxedo($idEntidad)' sin datos");
            }else{
                $response->status = true;
                $response->message = "Consulta exitosa";
                $response->municipios = json_decode($json, true);
            }        
        }catch(\Exception $e){
            $response->status = false;
            $response->message = "Error al obtener municipios";
            $this->log->error("Error en GetMunicipios: " . $e->getMessage());
        }
        return $response;
    }

    public function GetMedio(): ResponseWithMessage {
        $response = new ResponseWithMessage();

        try{
            $query ="select id_estado AS ID, nombre AS Medio from fn_retorna_medios_sucedio();";
            $json = $this->manager->multipleSelect($query);
            $data = json_decode($json, true);
            //var_dump($data);
            if(empty($data)){
                $response->status = false;
                $response->message = "consulta sin datos";
                $response->medios = null;
                $this->log->error("consulta 'select id_estado AS ID, nombre AS Medio from fn_retorna_medios_sucedio();");
            }else{
                $response->status = true;
                $response->message = "Consulta exitosa";
                $response->medios = json_decode($json, true);
            }
        }catch(\Exception $e){
            $response->status = false;
            $response->message = "Error al obtener catalogo de como ocurrio";
            $this->log->error("Error en GetMedio: " . $e->getMessage());
        }
        return $response;
    }

    //OBTENER TIPO ARCHIVO
    public function GetTipoArchivo(): ResponseWithMessage {
        $response = new ResponseWithMessage();

        try{
            $query ="select id_estado as id, nombre as archivo from fn_retorna_tipos_archivos();";
            $json = $this->manager->multipleSelect($query);
            $data = json_decode($json, true);
            //var_dump($data);
            if(empty($data)){
                $response->status = false;
                $response->message = "consulta sin datos";
                $response->tipoArchivo = null;
                $this->log->error("consulta 'select id_estado as id, nombre as archivo from fn_retorna_tipos_archivos();' sin datos");
            }else{
                $response->status = true;
                $response->message = "Consulta exitosa";
                $response->tipoArchivo = json_decode($json, true);
            }
        }catch(\Exception $e){
            $response->status = false;
            $response->message = "Error al obtener catalogo de tipo de archivos";
            $this->log->error("Error en GetTipoArchivo: " . $e->getMessage());
        }
        return $response;
    }

    //OBTENER TIPO ARCHIVO
    public function GetCorreosPorEntidad($idEntidad): ResponseWithMessage {
        $response = new ResponseWithMessage();

        try{       
            $query = "select email from fn_lista_email_estados(:idEntidad)";
            $json = $this->manager->multipleSelect($query, [':idEntidad' => (int)$idEntidad]);
            $data = json_decode($json, true);
            //var_dump($data);
            if(empty($data)){
                $response->status = false;
                $response->message = "consulta sin datos";
                $response->email = null;
                $this->log->error("consulta 'fn_lista_email_estados($idEntidad)' sin datos");
            }else{
                $response->status = true;
                $response->message = "Consulta exitosa";
                $response->email = json_decode($json, true);
            }        
        }catch(\Exception $e){
            $response->status = false;
            $response->message = "Error al obtener correos por entidad";
            $this->log->error("Error en GetCorreosPorEntidad: " . $e->getMessage());
        }
        return $response;
    }


    //ENVIO DE REPORTE
    private function escapePgLiteral(?string $value): string {
        if (is_null($value)) {
            return "NULL";
        }
        $escaped = str_replace("'", "''", $value);
        return "'$escaped'";
    }

    private function validateReporte(ReporteModel $r): void {

        // enteros obligatorios
        $ints = ['idEstado','idMunicipio','idSucedio'];
        foreach ($ints as $k) {
            $v = $r->$k;
            if (!is_int($v) || $v <= 0) {
                throw new \Exception("Campo inválido: {$k} debe ser entero > 0");
            }
        }

        if (!is_bool($r->esAnonimo) || !is_bool($r->esFisica) || !is_bool($r->tePaso) || !is_bool($r->esExtranjero) || !is_bool($r->esMenor)) {
            throw new \Exception("Banderas booleanas inválidas");
        }

        $hasControlChars = function (string $s): bool {
            return (bool)preg_match('/[\x00-\x1F\x7F]/u', $s);
        };

        // =========================
        // validación email (estricta)
        // =========================
        if ($r->email !== null) {
            $email = trim((string)$r->email);

            if ($email !== '') {
                if (strlen($email) > 254) {
                    throw new \Exception("Email excede longitud máxima");
                }

                if (preg_match('/[\'"\s<>\(\);]/u', $email)) {
                    throw new \Exception("Email inválido");
                }

                if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
                    throw new \Exception("Email inválido");
                }

                if ($hasControlChars($email)) {
                    throw new \Exception("Email inválido");
                }
            }

            $r->email = $email;
        }

        // =========================
        // validación comoOcurrio
        // =========================
        if ($r->comoOcurrio !== null) {
            $t = (string)$r->comoOcurrio;

            if ($hasControlChars($t)) {
                throw new \Exception("El campo comoOcurrio contiene caracteres inválidos");
            }

            // Longitud (puedes bajar a 2000 para que empate con front, o mantener 3000)
            if (mb_strlen($t) > 3000) {
                throw new \Exception("El campo comoOcurrio excede la longitud máxima");
            }

            // Bloquea el set de prueba del documento: "'<>;()
            if (preg_match('/[\'"<>;\(\)]/u', $t)) {
                throw new \Exception("El campo comoOcurrio contiene caracteres no permitidos");
            }

            $r->comoOcurrio = $t;
        }

        // validación edad:
        if ($r->edad !== null) {
            if (!is_int($r->edad) || $r->edad < 0 || $r->edad > 120) {
                throw new \Exception("Edad inválida");
            }
        }
    }


    public function SendReporte(ReporteModel $reporte): ResponseWithMessage {
        $response = new ResponseWithMessage();

        if (!empty($_POST['website'])) {
            $this->log->warning("Intento de bot detectado. IP: " . $this->obtenerIPCliente());
            $response->status = false;
            $response->message = "Acceso no autorizado";
            $response->response = null;
            return $response;
        }

        $rutaBase = '/var/www/html/CiberReportes/'.date('Y-m-d');

        try {
            $anonimo = $reporte->esAnonimo ? 'true' : 'false';
            $esMenor = $reporte->esMenor ? 'true' : 'false';
            $esFisica = $reporte->esFisica ? 'true' : 'false';
            $tePaso = $reporte->tePaso ? 'true' : 'false';
            $esExtranjero = $reporte->esExtranjero ? 'true' : 'false';
            
            $ipCliente = $this->obtenerIPCliente();

            //Consumir servicio de tipos de archivo
            try {
                $dataResponse = $this->GetTipoArchivo();
                if (!$dataResponse->status) {
                    throw new \Exception($dataResponse->message);
                }
                $tiposArchivo = $dataResponse->tipoArchivo;
            } catch (\Exception $e) {
                $response->status = false;
                $response->message = "Error al obtener tipos de archivo";
                $response->response = null;
                $this->log->error("Error en GetTipoArchivo: " . $e->getMessage());
                return $response;
            }

            $rutasFinales = [];

            if (!empty($reporte->nombreArchivo)) {
                $nombreArchivos = explode(',', $reporte->nombreArchivo);

                foreach ($nombreArchivos as $nombre) {
                    $nombreSanitizado = preg_replace('/[^a-zA-Z0-9\.\-_]/', '_', trim($nombre));

                    if ($nombreSanitizado !== '') {
                        // Obtener extensión
                        $extension = strtolower(pathinfo($nombreSanitizado, PATHINFO_EXTENSION));

                        // Intentar obtener el ID del tipo de archivo
                        try {
                            $idTipo = $this->obtenerIdTipoPorExtension($extension, $tiposArchivo);
                        } catch (\Exception $e) {
                            $response->status = false;
                            $response->message = $e->getMessage();
                            $response->response = null;
                            $this->log->error("Archivo no permitido: $nombreSanitizado - " . $e->getMessage());
                            return $response;
                        }

                        // Construir el registro válido
                        $rutasFinales[] = $idTipo . ',' . $rutaBase . ',' . $nombreSanitizado;
                    }
                }
            }

            $cadenaRutaNombre = !empty($rutasFinales) ? implode(',', $rutasFinales) : '';
            //var_dump($cadenaRutaNombre);

            //Validación de tipos y longitudes
            $this->validateReporte($reporte);

            //SQL parametrizado
            $sql = "
                SELECT folio AS Folio, nombredo AS Estado, nombreareporta AS reporta
                FROM fn_guarda_datos_repcib(
                    :anonimo,
                    :esFisica,
                    :tePaso,
                    :esExtranjero,
                    :email,
                    :fechaHecho,
                    :idEstado,
                    :idMunicipio,
                    :colonia,
                    :idSucedio,
                    :cp,
                    :descOcurrio,
                    :nombreArchivo,
                    :rutasURL,
                    :ipOrigen,
                    :curp,
                    :esMenor,
                    :nombre,
                    :aPaterno,
                    :aMaterno,
                    :telefono,
                    :edad,
                    :fechaNacimiento,
                    :nombreReporta,
                    :apellidoPaternoReporta,
                    :apellidoMaternoReporta,
                    :PersonaMoral,
                    :telefonoMoral
                )
            ";

            //var_dump($sql);

            // valores “crudos” y PDO los trata como datos (no como SQL).
            $params = [
                ':anonimo'      => $anonimo,
                ':esFisica'     => $esFisica,
                ':tePaso'       => $tePaso,
                ':esExtranjero' => $esExtranjero,

                ':email'                   => $reporte->email ?: null,
                ':fechaHecho'              => $reporte->fechaHechos ?: null,

                ':idEstado'                => (int)$reporte->idEstado,
                ':idMunicipio'             => (int)$reporte->idMunicipio,

                ':colonia'                 => $reporte->colonia ?: null,
                ':idSucedio'               => (int)$reporte->idSucedio,

                ':cp'                      => $reporte->cp ?: null,
                ':descOcurrio'             => $reporte->comoOcurrio ?: null,

                // lógica de archivos (NO tocar)
                ':nombreArchivo'           => $cadenaRutaNombre ?: null,

                ':rutasURL'                => $reporte->rutasURL ?: null,
                ':ipOrigen'                => $ipCliente ?: null,

                ':curp'                    => $reporte->curp ?: null,

                ':esMenor'      => $esMenor,

                ':nombre'                  => $reporte->nombre ?: null,
                ':aPaterno'                => $reporte->aPaterno ?: null,
                ':aMaterno'                => $reporte->aMaterno ?: null,
                ':telefono'                => $reporte->telefono ?: null,

                ':edad'                    => $reporte->edad, // puede ser null
                ':fechaNacimiento'         => $reporte->fechaNacimiento ?: null,

                ':nombreReporta'           => $reporte->nombreReporta ?: null,
                ':apellidoPaternoReporta'  => $reporte->apellidoPaternoReporta ?: null,
                ':apellidoMaternoReporta'  => $reporte->apellidoMaternoReporta ?: null,
                ':PersonaMoral'            => $reporte->PersonaMoral ?: null,
                ':telefonoMoral'           => $reporte->telefonoMoral ?: null,
            ];

            //var_dump($params);

            $json = $this->manager->simpleSelect($sql, $params);
            //var_dump($json);
            $data = json_decode($json, true);

            if (empty($data)) {
                $response->status = false;
                $response->message = "Consulta sin datos";
                $response->response = null;
                $this->log->error("Consulta fn_guarda_datos_REPCIB_v1 sin datos");
            } else {        
                // ====== ENVÍO DE CORREO ======
                $idioma = strtolower($reporte->idioma ?? 'es');
                $idioma = in_array($idioma, ['es','en'], true) ? $idioma : 'es';

                $folio      = $this->extraerFolio($data);
                $emailPlano = trim((string)($reporte->email ?? ''));
                $attempted  = false;
                $sent       = false;
                $state      = 'skipped'; 

                if ($folio && $emailPlano && filter_var($emailPlano, FILTER_VALIDATE_EMAIL)) {
                    // === Nombres disponibles en el modelo ===
                    $nombreAfectada = trim(implode(' ', array_filter([
                        $reporte->nombre ?? '',
                        $reporte->aPaterno ?? '',
                        $reporte->aMaterno ?? '',
                    ])));

                    $nombreReporta = trim(implode(' ', array_filter([
                        $reporte->nombreReporta ?? '',
                        $reporte->apellidoPaternoReporta ?? '',
                        $reporte->apellidoMaternoReporta ?? '',
                    ])));

                    $nombreMoral = trim((string)($reporte->PersonaMoral ?? ''));

                    // === Fallback por idioma ===
                    $fallback = ($idioma === 'en') ? 'Citizen' : 'Ciudadano(a)';

                    // === Decidir el destinatario que irá en {$n} según banderas ===
                    // Reglas:
                    // - esAnonimo = true → fallback
                    // - esAnonimo = false && esFisica = true:
                    //      tePaso = true  → nombre de la persona afectada
                    //      tePaso = false → nombre de la persona que reporta
                    // - esAnonimo = false && esFisica = false → razón social (PersonaMoral)
                    $destinatarioNombre = $fallback;

                    if (!$reporte->esAnonimo) {
                        if ($reporte->esFisica) {
                            if ($reporte->tePaso) {
                                $destinatarioNombre = ($nombreAfectada !== '') ? $nombreAfectada : $fallback;
                            } else {
                                $destinatarioNombre = ($nombreReporta !== '') ? $nombreReporta : $fallback;
                            }
                        } else {
                            // Persona moral
                            $destinatarioNombre = ($nombreMoral !== '') ? $nombreMoral : $fallback;
                        }
                    }

                    $nombrePlano = $nombreAfectada;

                    $subject = ($idioma === 'en')
                        ? "Acknowledgment of Receipt – Case {$folio}"
                        : "Acuse de recepción – Folio {$folio}";

                    // === HTML del acuse al ciudadano con el destinatario elegido ===
                    $html = ($idioma === 'en')
                        ? $this->acuseCiudadanoHTML_EN($destinatarioNombre ?: $fallback, $folio)
                        : $this->acuseCiudadanoHTML($destinatarioNombre ?: $fallback, $folio);

                    try {
                        $mailer  = new EmailService();
                        // $mailer->enableDebug();
                        $mailRes = $mailer->send($emailPlano, $subject, $html);

                        $sent  = (bool)($mailRes['ok'] ?? false);
                        $state = $sent ? 'sent' : 'failed';

                        // ====== REENVÍO A CORREOS DE LA ENTIDAD (DINÁMICO) ======
                        $entidadId = (int)($reporte->idEstado ?? 0);

                        if ($entidadId > 0) {
                            try {
                                // 1) Obtener correos desde el servicio
                                $listado = $this->GetCorreosPorEntidad($entidadId);
                                
                                // --- Unwrap del wrapper del servicio ---
                                if (is_string($listado)) {
                                    $tmp = json_decode($listado, true);
                                    if (json_last_error() === JSON_ERROR_NONE) {
                                        $listado = $tmp;
                                    }
                                }
                                if (is_array($listado)) {
                                    if (isset($listado['email']) && is_array($listado['email'])) {
                                        $listado = $listado['email'];
                                    } elseif (isset($listado['correos']) && is_array($listado['correos'])) {
                                        $listado = $listado['correos'];
                                    } elseif (isset($listado['data']) && is_array($listado['data'])) {
                                        $listado = $listado['data'];
                                    }
                                } elseif (is_object($listado)) {
                                    if (isset($listado->email) && is_array($listado->email)) {
                                        $listado = $listado->email;
                                    } elseif (isset($listado->correos) && is_array($listado->correos)) {
                                        $listado = $listado->correos;
                                    } elseif (isset($listado->data) && is_array($listado->data)) {
                                        $listado = $listado->data;
                                    }
                                }

                                // 2) Normalizar a lista de emails válidos
                                $correosEntidad = [];
                                if (is_array($listado)) {
                                    foreach ($listado as $row) {
                                        $c = null;
                                        if (is_string($row)) {
                                            $c = $row;
                                        } elseif (is_array($row)) {
                                            $c = $row['correo'] ?? $row['email'] ?? null;
                                        } elseif (is_object($row)) {
                                            $c = $row->correo ?? $row->email ?? null;
                                        }
                                        if ($c) {
                                            $c = trim((string)$c);
                                            if ($c !== '' && strcasecmp($c, $emailPlano) !== 0 && filter_var($c, FILTER_VALIDATE_EMAIL)) {
                                                $correosEntidad[] = strtolower($c);
                                            }
                                        }
                                    }
                                }

                                // 3) Eliminar duplicados
                                $correosEntidad = array_values(array_unique($correosEntidad));

                                // 4) Enviar acuse a cada correo de la entidad
                                if (!empty($correosEntidad)) {
                                    $htmlEntidad = $this->acuseEstadoHTML($nombrePlano ?: 'Entidad receptora', $folio);
                                    foreach ($correosEntidad as $correoEntidad) {
                                        $mailRes2 = $mailer->send($correoEntidad, $subject, $htmlEntidad);
                                        if (!($mailRes2['ok'] ?? false)) {
                                            $this->log->error("Error reenviando a entidad {$entidadId} ({$correoEntidad}): " . ($mailRes2['error'] ?? 'desconocido'));
                                        } else {
                                            $this->log->info("Acuse enviado a entidad {$entidadId} ({$correoEntidad}) para folio {$folio}.");
                                        }
                                    }
                                } else {
                                    $this->log->info("Entidad {$entidadId} sin correos válidos para reenvío de acuse (folio {$folio}).");
                                }
                            } catch (\Throwable $e) {
                                $this->log->error("Excepción al obtener/enviar correos de entidad {$entidadId}: " . $e->getMessage());
                            }
                        } else {
                            $this->log->info("No se reenvía a entidad: idEstado inválido o no proporcionado (folio {$folio}).");
                        }

                        if (!$sent) {
                            $this->log->error("Error enviando acuse a {$emailPlano}: " . ($mailRes['error'] ?? 'desconocido'));
                        }
                    } catch (\Throwable $e) {
                        $state = 'failed';
                        $this->log->error("Excepción enviando acuse a {$emailPlano}: " . $e->getMessage());
                    }
                } else {
                    $this->log->info("No se envía acuse: folio/email inválidos (folio={$folio}, email={$emailPlano}).");
                }

                $response->status   = true;
                $response->message  = "Consulta exitosa";
                $response->SendMail = $sent;
                $response->response = $data;
            }


        } catch (\Exception $e) {
            $response->status = false;
            $response->message = "Error al guardar reporte";
            $this->log->error("Error en SendReporte: " . $e->getMessage());
        }

        return $response;
    }

    private function extraerFolio($data): ?string {
        if (is_array($data)) {
            if (!empty($data['Folio'])) return (string)$data['Folio'];
            if (!empty($data['folio'])) return (string)$data['folio'];

            if (isset($data[0]) && is_array($data[0])) {
                if (!empty($data[0]['Folio'])) return (string)$data[0]['Folio'];
                if (!empty($data[0]['folio'])) return (string)$data[0]['folio'];
            }
        }
        return null;
    }

    /* === Plantilla de correo HTML (ES) === */
    private function acuseCiudadanoHTML(string $nombre, string $folio): string {
        $n = htmlspecialchars($nombre, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
        $f = htmlspecialchars($folio,  ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');

        return <<<HTML
        <div style="font-family:Arial,Helvetica,sans-serif; color:#111; line-height:1.5;">
        <p style="margin:0 0 12px 0;"><b>{$n}</b></p>
        <p style="margin:0 0 12px 0;">
            Le informamos que su reporte cibernético se registró en el Sistema con el número de folio:
            <b>{$f}</b>. El cual ha sido remitido a una Unidad de Policía Cibernética para su
            atención correspondiente.
        </p>
        <p style="margin:0 0 12px 0;">Agradecemos su confianza.</p>
        <p style="margin:0;"><b>Secretaría de Seguridad y Protección Ciudadana</b></p>
        </div>
        HTML;
    }

    /* === Plantilla de correo HTML (ES) === */
    private function acuseEstadoHTML(string $nombre, string $folio): string {
        /* $n = htmlspecialchars($nombre, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); */
        $n = "Entidad receptora";
        $f = htmlspecialchars($folio,  ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');

        return <<<HTML
        <div style="font-family:Arial,Helvetica,sans-serif; color:#111; line-height:1.5;">
        <p style="margin:0 0 12px 0;"><b>{$n}</b></p>
        <p style="margin:0 0 12px 0;">
            Se ha recibido un nuevo reporte con el FOLIO:
            <b>{$f}</b>. para que sea atendido. A continuación se anexa el resumen del reporte recibido.
        </p>
        <p style="margin:0;"><b>Secretaría de Seguridad y Protección Ciudadana</b></p>
        </div>
        HTML;
    }

    /* === Plantilla de correo HTML (EN) === */
    private function acuseCiudadanoHTML_EN(string $name, string $folio): string {
        $n = htmlspecialchars($name,  ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
        $f = htmlspecialchars($folio, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');

        return <<<HTML
        <div style="font-family:Arial,Helvetica,sans-serif; color:#111; line-height:1.5;">
        <p style="margin:0 0 12px 0;"><b>{$n}</b></p>
        <p style="margin:0 0 12px 0;">
            We inform you that your cyber incident report has been registered in the system
            with the case number <b>{$f}</b>. It has been forwarded to a Cyber Police Unit
            for appropriate follow-up.
        </p>
        <p style="margin:0 0 12px 0;">Thank you for your trust.</p>
        <p style="margin:0;"><b>Secretaría de Seguridad y Protección Ciudadana</b></p>
        </div>
        HTML;
    }



    public function obtenerIPCliente(): string
    {
        $isValid  = static fn(string $ip, int $flags = 0): bool
            => (bool) filter_var($ip, FILTER_VALIDATE_IP, $flags);
        $isPublic = static fn(string $ip): bool
            => (bool) filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE);

        $hasProxyHints = function(): bool {
            return !empty($_SERVER['HTTP_X_FORWARDED_FOR'])
                || !empty($_SERVER['HTTP_X_REAL_IP'])
                || !empty($_SERVER['HTTP_CF_CONNECTING_IP'])
                || !empty($_SERVER['HTTP_FORWARDED'])
                || !empty($_SERVER['HTTP_VIA']);
        };

        $firstPublicFromList = static function(string $csv) use ($isValid, $isPublic): ?string {
            foreach (explode(',', $csv) as $part) {
                $ip = trim($part);
                if ($isValid($ip) && $isPublic($ip)) return $ip;
            }
            return null;
        };

        $remote = $_SERVER['REMOTE_ADDR'] ?? '';

        if ($hasProxyHints()) {
            // 1) Intentar headers (solo IPs públicas)
            if (!empty($_SERVER['HTTP_CF_CONNECTING_IP']) && $isPublic($_SERVER['HTTP_CF_CONNECTING_IP'])) {
                $ip = $_SERVER['HTTP_CF_CONNECTING_IP'];
            } elseif (!empty($_SERVER['HTTP_X_REAL_IP']) && $isPublic($_SERVER['HTTP_X_REAL_IP'])) {
                $ip = $_SERVER['HTTP_X_REAL_IP'];
            } elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
                $ip = $firstPublicFromList($_SERVER['HTTP_X_FORWARDED_FOR']);
            } else {
                $ip = null;
            }

            // 1) Si no encontramos IP pública del cliente, devolvemos 0.0.0.0
            if ($ip === '::1') $ip = '127.0.0.1';
            return ($ip && $isValid($ip)) ? $ip : '0.0.0.0';
        }

        // 2) Sin señales de proxy → conexión directa: aceptar REMOTE_ADDR pública
        if ($remote === '::1') return '127.0.0.1';
        return ($remote && $isPublic($remote)) ? $remote : '0.0.0.0';
    }

    private array $mapaCategorias = [
        'jpg'  => 'IMAGEN',
        'jpeg' => 'IMAGEN',
        'png'  => 'IMAGEN',
        'pdf'  => 'DOCUMENTO',
        'docx' => 'DOCUMENTO',
        'mp3'  => 'AUDIO',
        'aac'  => 'AUDIO',
        'opus' => 'AUDIO',
        'ogg'  => 'AUDIO',
        'mp4'  => 'VIDEO'
    ];

    private function obtenerIdTipoPorExtension(string $extension, array $tiposArchivo): int {
        $extension = strtolower($extension);

        // Validar si la extensión está en el mapa
        if (!array_key_exists($extension, $this->mapaCategorias)) {
            throw new \Exception("La extensión .$extension no está permitida");
        }

        $categoria = $this->mapaCategorias[$extension];

        foreach ($tiposArchivo as $tipo) {
            if (stripos($tipo['archivo'], $categoria) !== false) {               
                return $tipo['id'];
            }
        }

        throw new \Exception("No se encontró el ID para la categoría $categoria");
    }


}