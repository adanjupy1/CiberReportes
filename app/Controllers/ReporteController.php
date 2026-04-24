<?php

namespace Controllers;

use Utils\CiberReportes;
use Models\ReporteModel;
use phpseclib3\Net\SFTP;
use phpseclib3\Crypt\PublicKeyLoader;

class ReporteController {
    private CiberReportes $service;

    public function __construct() {
        $this->service = new CiberReportes();

        if (session_status() !== PHP_SESSION_ACTIVE) {
            session_set_cookie_params([
                'lifetime' => 0,
                'path'     => '/',
                'secure'   => (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off'),
                'httponly' => true,
                'samesite' => 'Lax',
            ]);
            session_start();
        }
    }

    private function sftpConnect(): SFTP {
        $host       = $_ENV['SFTP_HOST'] ?? '';
        $port       = (int)($_ENV['SFTP_PORT'] ?? 22);
        $user       = $_ENV['SFTP_USER'] ?? '';
        $pass       = $_ENV['SFTP_PASS'] ?? null;
        $keyPath    = $_ENV['SFTP_PRIVATE_KEY'] ?? '';
        $passphrase = $_ENV['SFTP_KEY_PASSPHRASE'] ?? null;

        if (!$host || !$user) {
            throw new \Exception('Faltan datos SFTP: host/user.');
        }

        $sftp = new SFTP($host, $port, 10); // timeout 10s

        if ($keyPath) {
            if (!is_file($keyPath)) {
                throw new \Exception("Clave privada no encontrada: $keyPath");
            }
            $key = PublicKeyLoader::load(file_get_contents($keyPath), $passphrase ?: false);
            if (!$sftp->login($user, $key)) {
                throw new \Exception('Autenticación SFTP falló con clave privada (v3).');
            }
        } elseif ($pass) {
            if (!$sftp->login($user, $pass)) {
                throw new \Exception('Autenticación SFTP falló con contraseña (v3).');
            }
        } else {
            throw new \Exception('No se proporcionó clave ni contraseña para SFTP (v3).');
        }

        return $sftp;
    }

    private function normalizaArchivos(array $files): array {
        if (!is_array($files['name'])) {
            return [
                'name'     => [$files['name']],
                'type'     => [$files['type']],
                'tmp_name' => [$files['tmp_name']],
                'error'    => [$files['error']],
                'size'     => [$files['size']],
            ];
        }
        return $files;
    }

    private function sanitizaNombre(string $nombre): string {
        $nombre = basename($nombre);
        return preg_replace('/[^a-zA-Z0-9\.\-_]/', '_', $nombre) ?? 'archivo';
    }

    private function sanitizeFolio(string $folio): string {
        $folio = str_replace(['/', '\\'], '-', $folio);
        return preg_replace('/[^A-Za-z0-9\-\._]/', '_', $folio);
    }

    private function extValida(string $nombre, array $permitidas): bool {
        $ext = strtolower(pathinfo($nombre, PATHINFO_EXTENSION));
        return in_array($ext, $permitidas, true);
    }

    private function buildRemoteDir(): string {
        $base = rtrim($_ENV['SFTP_BASE'] ?? '/var/www/html/Adjuntos', '/'); 
        $sub = date('Y-m-d');        
        return $base . '/' . $sub;
    }

    private function ensureRemoteDir(SFTP $sftp, string $remoteDir): void {
        if (!$sftp->is_dir($remoteDir)) {
            if (!$sftp->mkdir($remoteDir, -1, true)) {
                throw new \Exception("No se pudo crear carpeta remota: {$remoteDir}");
            }
        }
    }

    //END-POINT ESTADOS
    public function GetEstados() {
        header('Content-Type: application/json');

        echo json_encode($this->service->GetEstados()); exit;
    }

    //END-PONT MUNICIPIOS
    public function GetMunicipios() {
        header('Content-Type: application/json');

        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(["error" => "Método no permitido"]);
            return;
        }
        $input = json_decode(file_get_contents('php://input'), true);

        if (!isset($input['idEntidad']) || trim($input['idEntidad']) === '') {
            http_response_code(400);
            echo json_encode(["error" => "El campo 'idEntidad' es requerido y no puede estar vacío"]);
            return;
        }

        $idEntidad = (int)$input['idEntidad'];
        if ($idEntidad <= 0) {
            http_response_code(400);
            echo json_encode(["error" => "El campo 'idEntidad' debe ser un entero > 0"]);
            return;
        }
        echo json_encode($this->service->GetMunicipios($idEntidad)); exit;
    }

    //END-POINT MEDIO SUCEDIO
    public function GetMedio() {
        header('Content-Type: application/json');

        echo json_encode($this->service->GetMedio()); exit;
    }

    //END-POINT TIPO DE ARCHIVO
    public function GetTipoArchivo() {
        header('Content-Type: application/json');

        echo json_encode($this->service->GetTipoArchivo()); exit;
    }

    //END-POINT OBTENER CORREOS POR ENTIDAD
    public function GetCorreosPorEntidad() {
        header('Content-Type: application/json');

        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(["error" => "Método no permitido"]);
            return;
        }
        $input = json_decode(file_get_contents('php://input'), true);

        if (!isset($input['idEntidad']) || trim($input['idEntidad']) === '') {
            http_response_code(400);
            echo json_encode(["error" => "El campo 'idEntidad' es requerido y no puede estar vacío"]);
            return;
        }

        $idEntidad = (int)$input['idEntidad'];
        if ($idEntidad <= 0) {
            http_response_code(400);
            echo json_encode(["error" => "El campo 'idEntidad' debe ser un entero > 0"]);
            return;
        }
        echo json_encode($this->service->GetCorreosPorEntidad($idEntidad)); exit;
    }


    //END-POINT ENVIO DE REPORTE
    public function SendReporte() {
        header('Content-Type: application/json');

        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            http_response_code(405);
            echo json_encode(["error" => "Método no permitido"]); exit;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        if ($input === null && !empty($_POST)) $input = $_POST;

        try {
            $reporte = new ReporteModel($input);
            $res = $this->service->SendReporte($reporte);
      
            $status   = false;
            $folioRaw = null;

            if (is_object($res)) {
                $status = $res->status ?? false;
                if (isset($res->response)) {
                    if (is_object($res->response))      $folioRaw = $res->response->folio ?? null;
                    elseif (is_array($res->response))    $folioRaw = $res->response['folio'] ?? null;
                }
                if (!$folioRaw) $folioRaw = $res->folio ?? null;
            } elseif (is_array($res)) {
                $status = $res['status'] ?? false;
                if (isset($res['response'])) {
                    if (is_array($res['response']))     $folioRaw = $res['response']['folio'] ?? null;
                    elseif (is_object($res['response'])) $folioRaw = $res['response']->folio ?? null;
                }
                if (!$folioRaw) $folioRaw = $res['folio'] ?? null;
            }

            $out = is_object($res) ? json_decode(json_encode($res), true) : $res;

            // --- Mover a /YYYY-MM-DD/<FOLIO>/ si hubo folio y hay adjuntos en sesión
            if ($status && $folioRaw && !empty($_SESSION['uploads_repcib'])) {
                $sftp = $this->sftpConnect();
                $folioSan = $this->sanitizeFolio($folioRaw);

                $moved = [];
                foreach ($_SESSION['uploads_repcib'] as $it) {
                    $dateDir  = $it['dir'];                      // /.../Adjuntos/2025-09-05
                    $oldPath  = $dateDir . '/' . $it['stored'];  // /.../2025-09-05/HHMMSS_token_nombre.ext
                    $folioDir = $dateDir . '/' . $folioSan;      // /.../2025-09-05/DG-2025-000000014

                    $this->ensureRemoteDir($sftp, $folioDir);

                    $target = $folioDir . '/' . $it['orig'];
                    if ($sftp->file_exists($target)) {
                        $target = $folioDir . '/' . $it['token'] . '_' . $it['orig'];
                    }

                    if ($sftp->rename($oldPath, $target)) {
                        $moved[] = $target;
                    } else {
                        error_log("No se pudo mover $oldPath a $target");
                    }
                }

                unset($_SESSION['uploads_repcib']);

                // añadimos info útil a la respuesta
                $out['archivos_paths']   = $moved;
                $out['archivos_carpeta'] = $folioSan;
            }

            echo json_encode($out); exit;

        } catch (\Throwable $e) {
            http_response_code(500);
            echo json_encode(["status"=>false, "message"=>"Error en SendReporte: ".$e->getMessage()]); exit;
        }
    }



    //END-POINT SUBIR ARCHIVOS (SFTP)
    public function SubirAdjuntos() {
        header('Content-Type: application/json');

        try {
            if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
                http_response_code(405);
                echo json_encode(["status"=>false, "message"=>"Método no permitido"]);
                return;
            }

            if (empty($_FILES['adjuntos'])) {
                http_response_code(400);
                echo json_encode(["status"=>false, "message"=>"No se recibieron archivos."]);
                return;
            }

            // Reglas
            $limiteTotal = 10 * 1024 * 1024; // 10MB
            $permitidas = [
                'pdf','jpg','jpeg','png','gif','mp4','mov','avi',
                'mp3','wav','txt','doc','docx','xls','xlsx','opus','ogg','aac',
                'ppt','pptx','zip','rar','7z','csv','json'
            ];

            $archivos  = $this->normalizaArchivos($_FILES['adjuntos']);
            $totalSize = 0;
            $aSubir    = [];

            foreach ($archivos['name'] as $i => $nombreOriginal) {
                $err  = $archivos['error'][$i];
                $size = (int)$archivos['size'][$i];
                if ($err !== UPLOAD_ERR_OK) continue;

                $totalSize += $size;
                if ($totalSize > $limiteTotal) {
                    http_response_code(400);
                    echo json_encode(["status"=>false, "message"=>"El total de archivos supera los 10 MB permitidos."]);
                    return;
                }

                $safe = $this->sanitizaNombre($nombreOriginal);
                if (!$this->extValida($safe, $permitidas)) {
                    http_response_code(400);
                    echo json_encode(["status"=>false, "message"=>"Extensión no permitida: {$nombreOriginal}"]);
                    return;
                }

                $aSubir[] = [
                    'tmp'  => $archivos['tmp_name'][$i],
                    'safe' => $safe,
                    'size' => $size,
                    'type' => $archivos['type'][$i] ?? 'application/octet-stream',
                ];
            }

            if (empty($aSubir)) {
                http_response_code(400);
                echo json_encode(["status"=>false, "message"=>"No se pudo subir ningún archivo válido."]);
                return;
            }

            $sftp      = $this->sftpConnect();
            $remoteDir = $this->buildRemoteDir();
            $this->ensureRemoteDir($sftp, $remoteDir);

            $_SESSION['uploads_repcib'] = $_SESSION['uploads_repcib'] ?? [];
            $subidos = [];

            foreach ($aSubir as $file) {
                $pref = date('His') . '_' . bin2hex(random_bytes(3));
                $remoteName = $pref . '_' . $file['safe'];
                $remotePath = $remoteDir . '/' . $remoteName;

                $ok = $sftp->put($remotePath, $file['tmp'], SFTP::SOURCE_LOCAL_FILE);
                if (!$ok) {
                    throw new \Exception("Falló la carga del archivo: {$file['safe']}");
                }

                $ext = strtolower(pathinfo($file['safe'], PATHINFO_EXTENSION));
                $_SESSION['uploads_repcib'][] = [
                    'dir'    => $remoteDir,
                    'orig'   => $file['safe'],     
                    'stored' => $remoteName,       
                    'ext'    => $ext,
                    'token'  => $pref,
                    'size'   => $file['size'],
                    'type'   => $file['type'],
                ];

                $subidos[] = [
                    'name'        => $file['safe'],
                    'remote_name' => $remoteName,
                    'remote_dir'  => $remoteDir,
                    'remote_path' => $remotePath,
                    'size'        => $file['size'],
                    'type'        => $file['type'],
                    'token'       => $pref,
                ];
            }

            echo json_encode([
                "status"    => true,
                "message"   => "Archivos subidos correctamente al servidor remoto.",
                "archivos"  => $subidos,
                "inventario_guardado" => true,
                "count"     => count($subidos),
            ]);
        } catch (\Throwable $e) {
            http_response_code(500);
            echo json_encode([
                "status"  => false,
                "message" => "Error en subida SFTP: " . $e->getMessage()
            ]);
        }
    }

    public function LimpiarAdjuntos() {
        header('Content-Type: application/json');
        if (session_status() !== PHP_SESSION_ACTIVE) {
            session_start();
        }
        unset($_SESSION['uploads_repcib']);
        echo json_encode(["status"=>true, "message"=>"Adjuntos en sesión limpiados."]);
    }
    
}