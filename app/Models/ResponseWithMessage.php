<?php

namespace Models;

class ResponseWithMessage {
    public bool $status;
    public string $message;

    public function __construct() {
        $this->status = false;
        $this->message = ''; 
    }
}