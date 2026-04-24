<?php
namespace Utils;

use PDO;
use PDOException;
use Utils\Logger;

class Database {
    private PDO $connection;

    public function __construct() {
        $host = $_ENV['DB_HOST'] ?? 'localhost';
        $port = $_ENV['DB_PORT'] ?? '5432';
        $dbname = $_ENV['DB_NAME'] ?? '';
        $user = $_ENV['DB_USER'] ?? '';
        $password = $_ENV['DB_PASSWORD'] ?? '';

        $dsn = "pgsql:host=$host;port=$port;dbname=$dbname";

        try {
            $this->connection = new PDO($dsn, $user, $password, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
            ]);

        //ESQUEMA POR DEFECTO    
        //$this->connection->exec("SET search_path TO repcib_v2, public");

        } catch (PDOException $e) {
            throw new \Exception("Error de conexión: " . $e->getMessage());
            $this->log->error("Error de conexión a Base de Datos");

        }
    }

    public function getConnection(): PDO {
        return $this->connection;
    }
}
