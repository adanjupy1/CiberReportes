<?php

namespace Controllers;

class ViewsController {
    public function Home() {
        require_once __DIR__ . '/../Views/home/rc.php';
    }
    
    public function Index() {
        require_once __DIR__ . '/../Views/home/index.php';
    }
    
    public function IndexOllama() {
        require_once __DIR__ . '/../Views/home/index_ollama.php';
    }
    
    public function IndexPro() {
        // Fusionado en index_ollama.php
        require_once __DIR__ . '/../Views/home/index_ollama.php';
    }
    
    public function IndexRag() {
        // Fusionado en index_ollama.php
        require_once __DIR__ . '/../Views/home/index_ollama.php';
    }
    
}