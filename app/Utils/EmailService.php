<?php
namespace Utils;

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

class EmailService {
    private PHPMailer $mail;

    private function env(string $key, ?string $default=null): ?string {
        $v = $_ENV[$key] ?? $_SERVER[$key] ?? getenv($key);
        if ($v === false || $v === null) return $default;
        $v = trim((string)$v);
        return $v === '' ? $default : $v;
    }

    public function __construct() {
        $this->mail = new PHPMailer(true);
        $this->mail->CharSet = 'UTF-8';
        $this->mail->Timeout = 30;
        $this->mail->SMTPKeepAlive = false;

        // remitente
        $from     = $this->env('SMTP_FROM') ?: $this->env('SMTP_USER');
        $fromName = $this->env('SMTP_FROM_NAME', 'No-Reply');
        if (!filter_var($from, FILTER_VALIDATE_EMAIL)) {
            error_log('[MAIL CFG] SMTP_FROM inválido: '.var_export($from,true));
            throw new \RuntimeException('Config inválida: SMTP_FROM/SMTP_USER no es email');
        }

        // transporte
        $transport = strtolower($this->env('SMTP_TRANSPORT', 'smtp'));

        if ($transport === 'sendmail') {
            // Postfix local
            $path = $this->env('SENDMAIL_PATH', '/usr/sbin/sendmail');
            $this->mail->isSendmail();
            $this->mail->Sendmail = $path; // PHPMailer añade -t -i
            $this->mail->setFrom($from, $fromName);
            $this->mail->Sender = $from;   // envelope-from (-f)
        } else {
            // SMTP (OCI/túnel/etc.)
            $this->mail->isSMTP();
            $this->mail->Host     = (string)$this->env('SMTP_HOST');
            $hasUser              = (bool)$this->env('SMTP_USER');
            $this->mail->SMTPAuth = filter_var($this->env('SMTP_AUTH', $hasUser ? '1' : '0'), FILTER_VALIDATE_BOOLEAN);
            $this->mail->Username = (string)$this->env('SMTP_USER', '');
            $this->mail->Password = (string)$this->env('SMTP_PASS', '');

            $secure = strtolower($this->env('SMTP_SECURE','tls')); // tls|ssl|none
            if ($secure === 'ssl') {
                $this->mail->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;
                $this->mail->Port       = (int)$this->env('SMTP_PORT','465');
            } elseif ($secure === 'tls') {
                $this->mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
                $this->mail->Port       = (int)$this->env('SMTP_PORT','587');
            } else {
                $this->mail->SMTPSecure = false; // solo redes internas
                $this->mail->Port       = (int)$this->env('SMTP_PORT','25');
            }

            $this->mail->setFrom($from, $fromName);
            $this->mail->Sender = $from; // envelope-from
        }
    }

    public function send(
        string $to,
        string $subject,
        string $htmlBody,
        ?string $replyTo = null,
        array $attachments = []
    ): array {
        try {
            if (!filter_var($to, FILTER_VALIDATE_EMAIL)) {
                return ['ok'=>false, 'error'=>'Email destino inválido'];
            }

            $this->mail->clearAllRecipients();
            $this->mail->clearAttachments();

            $this->mail->addAddress($to);
            if ($replyTo && filter_var($replyTo, FILTER_VALIDATE_EMAIL)) {
                $this->mail->addReplyTo($replyTo);
            }

            $this->mail->isHTML(true);
            $this->mail->Subject = $subject;
            $this->mail->Body    = $htmlBody;
            $this->mail->AltBody = strip_tags($htmlBody);

            foreach ($attachments as $path) {
                if (is_file($path)) $this->mail->addAttachment($path);
            }

            $ok = $this->mail->send();
            return ['ok'=>$ok, 'error'=>null];
        } catch (Exception $e) {
            return ['ok'=>false, 'error'=>$this->mail->ErrorInfo ?: $e->getMessage()];
        }
    }

    public function enableDebug(): void {
        $this->mail->SMTPDebug   = 2;          // 0=off, 2=verbose
        $this->mail->Debugoutput = 'error_log';
    }
}
