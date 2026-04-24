<?php
//ENRUTADOR ENDPOINTS
require_once __DIR__ . '/../vendor/autoload.php';

use Dotenv\Dotenv;

$dotenv = Dotenv::createImmutable(__DIR__ . '/../');
$dotenv->load();

$uri = $_SERVER['REQUEST_URI'];
$scriptName = dirname($_SERVER['SCRIPT_NAME']);
$basePath = rtrim($scriptName, '/');

$route = str_replace($basePath, '', $uri);
$route = trim($route, '/');
$parts = explode('/', $route);

$controllerName = $parts[0] ?? null;
$methodName = $parts[1] ?? null;

if ($controllerName && $methodName) {
    $controllerClass = "Controllers\\" . ucfirst($controllerName) . "Controller";

    if (class_exists($controllerClass)) {
        $controller = new $controllerClass();

        if (method_exists($controller, $methodName)) {
            if ($controllerName !== 'Views') {
                header('Content-Type: application/json');
            }

            $controller->$methodName();
            exit;
        } else {
            http_response_code(404);
            echo json_encode(["error" => "Método no encontrado"]);
            exit;
        }
    } else {
        http_response_code(404);
        echo json_encode(["error" => "Controlador no encontrado"]);
        exit;
    }
}

// CARGA DE VISTA INICIAL
require_once __DIR__ . '/../app/Views/home/rc.php';
exit;
