<?php

namespace Models;

class ReporteModel {
    public bool $esAnonimo;
    public bool $esFisica;
    public bool $tePaso;
    public bool $esExtranjero;
    public ?int $idEstado;
    public ?int $idMunicipio;
    public ?string $colonia;
    public ?string $cp;
    public ?string $comoOcurrio;
    public ?string $fechaHechos;
    public ?int $idSucedio;
    public ?string $ipOrigen;
    public bool $esMenor;
    public ?string $nombreReporta;
    public ?string $apellidoPaternoReporta;
    public ?string $apellidoMaternoReporta;
    public ?string $PersonaMoral;
    public ?string $telefonoMoral;
    public ?string $curp;
    public ?string $nombre;
    public ?string $aPaterno;
    public ?string $aMaterno;
    public ?string $fechaNacimiento;
    public ?int $edad;
    public ?string $telefono;
    public ?string $email;
    public ?string $nombreArchivo;
    public ?string $rutasURL;
    public ?string $idioma;


    public function __construct(array $data) {
    $this->esAnonimo = (bool) $data['esAnonimo'];
    $this->esFisica = (bool) $data['esFisica'];
    $this->tePaso = (bool) $data['tePaso'];
    $this->esExtranjero = (bool) $data['esExtranjero'];
    $this->idEstado = isset($data['idEstado']) ? (int) $data['idEstado'] : null;
    $this->idMunicipio = isset($data['idMunicipio']) ? (int) $data['idMunicipio'] : null;
    $this->colonia = $data['colonia'] ?? null;
    $this->cp = $data['cp'] ?? null;
    $this->comoOcurrio = $data['comoOcurrio'] ?? null;
    $this->fechaHechos = $data['fechaHechos'] ?? null;
    $this->idSucedio = isset($data['idSucedio']) ? (int) $data['idSucedio'] : null;
    $this->ipOrigen = $data['ipOrigen'] ?? null;
    $this->esMenor = (bool) $data['esMenor'];
    $this->nombreReporta = $data['nombreReporta'] ?? null;
    $this->apellidoPaternoReporta = $data['apellidoPaternoReporta'] ?? null;
    $this->apellidoMaternoReporta = $data['apellidoMaternoReporta'] ?? null;
    $this->PersonaMoral = $data['PersonaMoral'] ?? null;
    $this->telefonoMoral = $data['telefonoMoral'] ?? null;
    $this->curp = $data['curp'] ?? null;
    $this->nombre = $data['nombre'] ?? null;
    $this->aPaterno = $data['aPaterno'] ?? null;
    $this->aMaterno = $data['aMaterno'] ?? null;
    $this->fechaNacimiento = $data['fechaNacimiento'] ?? null;  
    $this->edad = isset($data['edad']) ? (int) $data['edad'] : null;
    $this->telefono = $data['telefono'] ?? null;
    $this->email = $data['email'] ?? null;
    $this->nombreArchivo = $data['nombreArchivo'] ?? null;
    $this->rutasURL = $data['rutasURL'] ?? null;
    $this->idioma = $data['idioma'] ?? null;
    }

}

