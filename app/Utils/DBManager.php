<?php
namespace Utils;

use PDO;
use Exception;

class DBManager {
    private PDO $db;

    public function __construct(Database $database) {
        $this->db = $database->getConnection();
    }

    public function simpleSelect(string $sql, array $params = []): string {
        try {
            $stmt = $this->db->prepare($sql);
            $stmt->execute($params);
            $result = $stmt->fetch(PDO::FETCH_ASSOC);
            return json_encode($result ?: []);
        } catch (Exception $e) {
            throw new Exception("Error en simpleSelect: " . $e->getMessage());
        }
    }

    public function multipleSelect(string $sql, array $params = []): string {
        try {
            $stmt = $this->db->prepare($sql);
            $stmt->execute($params);
            $result = $stmt->fetchAll(PDO::FETCH_ASSOC);
            return json_encode($result);
        } catch (Exception $e) {
            throw new Exception("Error en multipleSelect: " . $e->getMessage());
        }
    }

    public function getRowsAffected(string $sql, array $params = []): int {
        try {
            $stmt = $this->db->prepare($sql);
            $stmt->execute($params);
            return (int)$stmt->rowCount();
        } catch (Exception $e) {
            throw new Exception("Error en getRowsAffected: " . $e->getMessage());
        }
    }

    public function getMultipleResults(string $sql, array $params = []): string {
        try {
            $results = [];
            $stmt = $this->db->prepare($sql);
            $stmt->execute($params);

            do {
                $result = $stmt->fetchAll(PDO::FETCH_ASSOC);
                if ($result) {
                    $results[] = $result;
                }
            } while ($stmt->nextRowset());

            return json_encode($results);
        } catch (Exception $e) {
            throw new Exception("Error en getMultipleResults: " . $e->getMessage());
        }
    }
}
