<?php
session_start();
header('Content-Type: application/json; charset=utf-8');

$mensaje = $_POST["mensaje"] ?? "";
$mensaje = trim($mensaje);

if ($mensaje === "") {
  http_response_code(400);
  echo json_encode(["error" => "mensaje vacío"], JSON_UNESCAPED_UNICODE);
  exit;
}

// Usar 127.0.0.1 en lugar de localhost evita problemas de resolución en Windows/XAMPP
$apiUrl = "http://127.0.0.1:8000/ask";

$payload = [
  "query" => $mensaje,
  "top_k" => 3,
  "min_score" => 0.85,
  "include_related" => true,
  "session_id" => session_id(),
  "user_id" => $_SESSION["user_id"] ?? null
];

$ch = curl_init($apiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Content-Type: application/json"]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload, JSON_UNESCAPED_UNICODE));
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);

$response = curl_exec($ch);
$curlError = curl_error($ch);
$httpCode  = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($response === false || $response === "") {
  http_response_code(503);
  echo json_encode([
    "error" => "sin respuesta de la API",
    "detalle" => $curlError ?: "curl_exec devolvió vacío",
    "url" => $apiUrl
  ], JSON_UNESCAPED_UNICODE);
  exit;
}

http_response_code($httpCode ?: 500);
echo $response;
