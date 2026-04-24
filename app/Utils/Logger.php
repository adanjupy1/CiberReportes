<?php
namespace Utils;

use Monolog\Logger as MonoLogger;
use Monolog\Handler\StreamHandler;
use Monolog\Formatter\LineFormatter;

class Logger {
    private MonoLogger $logger;

    public function __construct(string $channel = 'app') {
        $this->logger = new MonoLogger($channel);

        $logPath = __DIR__ . '/../../logs/CiberReportes.log';

        $formatter = new LineFormatter(null, null, false, true);
        $stream = new StreamHandler($logPath, MonoLogger::DEBUG);
        $stream->setFormatter($formatter);

        $this->logger->pushHandler($stream);
    }

    public function info(string $message): void {
        $this->logger->info($message);
    }

    public function error(string $message): void {
        $this->logger->error($message);
    }

    public function debug(string $message): void {
        $this->logger->debug($message);
    }
}
