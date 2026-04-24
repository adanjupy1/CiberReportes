<!DOCTYPE html>       <!-- DE AQUI ADAN -->
<html lang="en">
<?php
// Cargar autoload y variables de entorno si no están cargadas
if (!class_exists('Dotenv\Dotenv')) {
    require_once __DIR__ . '/../../../vendor/autoload.php';
}

//if (!isset($_ENV['ASSISTANT_IFRAME_PATH']) || empty($_ENV['ASSISTANT_IFRAME_PATH'])) {
    // Intentar cargar el .env si no está cargado
//    try {
//        $dotenv = \Dotenv\Dotenv::createImmutable(__DIR__ . '/../../../');
//        $dotenv->load();
//    } catch (\Exception $e) {
        // Ya está cargado o no se puede cargar
//    }
//}

$year = date("y");

// Función auxiliar para obtener variables de entorno con valor por defecto
function getEnvOrDefault($key, $default = '') {
    return isset($_ENV[$key]) && !empty($_ENV[$key]) ? $_ENV[$key] : $default;
}

// Cargar rutas base del proyecto desde variables de entorno

$projectBasePath = getEnvOrDefault('PROJECT_BASE_PATH', '/var/www/html');
$ciberReportesPath = getEnvOrDefault('CIBERREPORTES_PATH', $projectBasePath . '/CiberReportes');
$proyectosAltPath = getEnvOrDefault('PROYECTOS_ALT_PATH', $projectBasePath . '/proyectos_alternativos');

//================================================================== HASTA AQUI ADAN





//---------CODIGO ADAN ----------------------------------------------
// Cargar variables de entorno para rutas de assets (relativas desde public/)
$imgPath = getEnvOrDefault('ASSETS_IMG_PATH', 'img/');
$cssPath = getEnvOrDefault('ASSETS_CSS_PATH', 'css/');
$jsPath = getEnvOrDefault('ASSETS_JS_PATH', 'js/');
$vendorPath = getEnvOrDefault('ASSETS_VENDOR_PATH', 'vendor/');

// Ruta del asistente (iframe)
$assistantPath = getEnvOrDefault('ASSISTANT_IFRAME_PATH', 'default_value');

// Debug: descomentar para ver los valores
// echo "<!-- DEBUG: assistantPath = " . htmlspecialchars($assistantPath) . " -->";
// echo "<!-- DEBUG: ASSISTANT_IFRAME_PATH desde ENV = " . htmlspecialchars($_ENV['ASSISTANT_IFRAME_PATH'] ?? 'NO DEFINIDA') . " -->";
// echo "<!-- DEBUG: projectBasePath = " . htmlspecialchars($projectBasePath) . " -->";
// echo "<!-- DEBUG: ciberReportesPath = " . htmlspecialchars($ciberReportesPath) . " -->";  

//-----------------------------------------------HASTA AQUI ADAN ----------------------------------------------
?>

<head>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <title>CiberReportes</title>
    <meta content="" name="description">
    <meta content="" name="keywords">
    <!-- Favicons -->
    <!-- <link href="<?php echo $imgPath; ?>nv3.png" rel="icon"> -->
    <link href="<?php echo $imgPath; ?>apple-touch-icon.png" rel="apple-touch-icon">
    <!-- Google Fonts -->
    <link href="https://fonts.gstatic.com" rel="preconnect">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,300i,400,400i,600,600i,700,700i|Nunito:300,300i,400,400i,600,600i,700,700i|Poppins:300,300i,400,400i,500,500i,600,600i,700,700i" rel="stylesheet">
    <!-- Vendor CSS Files -->
    <link href="<?php echo $vendorPath; ?>bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="<?php echo $vendorPath; ?>bootstrap-icons/bootstrap-icons.css" rel="stylesheet">
    <link href="<?php echo $vendorPath; ?>boxicons/css/boxicons.min.css" rel="stylesheet">
    <link href="<?php echo $vendorPath; ?>quill/quill.snow.css" rel="stylesheet">
    <link href="<?php echo $vendorPath; ?>quill/quill.bubble.css" rel="stylesheet">
    <link href="<?php echo $vendorPath; ?>remixicon/remixicon.css" rel="stylesheet">
    <link href="<?php echo $cssPath; ?>style.css" rel="stylesheet">
</head>
<body>
    <link rel="stylesheet" href="<?php echo $cssPath; ?>rcestilos.css">
    <section class="section">
        <div class="form-container">
            <div class="row">
                <div class="col-lg-12">
                    <div class="card mb-3">
                        <!-- <div class="card-header text-center" style="background-color: #611031;"><img src="img/rcimg2.png" class="img-fluid" alt="Descripción" style="max-inline-size: 100%; "></div> -->
                        <div class="card-header text-center" style="background-color: #611031;">
<!-- ADAN -->                 <img src="img/rcimg2.png" class="img-fluid" alt="Descripción" style="max-inline-size: 100%;">
                        </div>
                        <div class="form-body">
                            <div class="card-body">
                                <h5 id="h5rc" class="card-title" style="color: #611031; text-align: center;">REGISTRO DE REPORTES CIBERNÉTICOS</h5>
                                <h5 class="card-title" style="color: #611031; text-align: end;">                           
                                    <div class="selector-wrapper">
                                        <select class="form-control select-idioma pe-4" id="selectorIdioma">
                                            <option value="" selected hidden></option>
                                            <option value="es">Español</option>
                                            <option value="en">English</option>
                                        </select>
                                        <span id="fakeText" class="fake-label">Idioma</span>
                                        <span class="dropdown-icon">▼</span>
                                    </div>                      
                                </h5>
                                <span id="spnHead" class="spanHead">Todos los datos marcados con (*) son obligatorios.</span>
                                <form method="POST" action="" enctype="multipart/form-data" id="reporteCibernetico" novalidate>
                                    <div class="row">
                                        <hr style="border: none; block-size: 2px; background: #611031;">                               
                                        <table class="encuesta">
                                            <tr>
                                                <td id="lblanonimo">¿Le gustaría presentar su reporte de forma anónima?*</td>
                                                <td>
                                                    <label><input type="radio" class="form-check-input" name="anonimo" value="si" required><span id="lblsiAnonimo">Sí</span></label>
                                                    <label><input type="radio" class="form-check-input" name="anonimo" value="no"> No</label>
                                                </td>
                                            </tr>
                                            <tr name="trTipoPersona">
                                                <td id="lblPersonaFisica">¿Eres persona física?</td>
                                                <td>
                                                    <label><input type="radio" class="form-check-input" name="fisica" value="si" required><span id="lblsiPersonaFisica">Sí</span></label>
                                                    <label><input type="radio" class="form-check-input" name="fisica" value="no"> No</label>
                                                </td>
                                            </tr>
                                            <tr name="trAfectado">
                                                <td id="lblpaso">¿Esto te pasó a ti?</td>
                                                <td>
                                                    <label><input type="radio" class="form-check-input" name="afectado" value="si" required><span id="lblsiAfectado">Sí</span></label>
                                                    <label><input type="radio" class="form-check-input" name="afectado" value="no"> No</label>
                                                </td>
                                            </tr>
                                            <tr name="trExtranjero">
                                                <td id="lblex">¿Es usted extranjero?</td>
                                                <td>
                                                    <label><input type="radio" class="form-check-input" name="extranjero" value="si" required><span id="lblsiExtranjero">Sí</span></label>
                                                    <label><input type="radio" class="form-check-input" name="extranjero" value="no"> No</label>
                                                </td>
                                            </tr>
                                        </table>

                                        <!-- DATOS PERSONA AFECTADA -->
                                        <div id="datosPersona" class="hidden">
                                            <div class="row mb-3">
                                                <div id="divdp" class="section-title" style="background-color: #611031; color:#ffffff; text-align: center;"><strong>Datos persona afectada</strong></div>
                                            </div>                                 
                                            <div class="row mb-3">
                                                <label id="lblcurp" for="nombre" class="col-sm-3 col-form-label">CURP: </label>
                                                <div id="curpDiv" class="col-sm-3">
                                                    <input type="text" class="form-control" id="curp" name="curp" maxlength="18" pattern="[A-Z]{4}[0-9]{6}[A-Z]{6}[0-9]{2}">
                                                    <small>
                                                        <a href="https://www.gob.mx/curp/" target="_blank" id="messageLink">Consultar CURP 🔗</a>
                                                    </small>
                                                </div>

                                                <label id="lblfena" for="fechaNacimiento" class="col-sm-3 col-form-label">Fecha de nacimiento*: </label>
                                                <div class="col-sm-3">
                                                    <input class="form-control" type="date" id="fechaNacimiento" name="fechaNacimiento">
                                                </div>                                       
                                            </div>

                                            <input type="text" name="info_confirm" class="honeypot" style="display:none;">

                                            <div class="row mb-3">
                                                <label id="lblno"for="nombre" class="col-sm-3 col-form-label">Nombre*: </label>
                                                <div class="col-sm-3">
                                                    <input type="text" class="form-control" id="nombre" name="nombre" maxlength="40" oninput="soloLetras(event)">
                                                </div>

                                                <label id="lblpa" for="apellidoPaterno" class="col-sm-3 col-form-label">Apellido paterno*:</label>
                                                <div class="col-sm-3">
                                                    <input type="text" class="form-control" id="apellidoPaterno" name="apellidoPaterno" maxlength="40" oninput="soloLetras(event)">
                                                </div>
                                            </div>

                                            <div class="row mb-3">
                                                <label id="lblma" for="apellidoMaterno" class="col-sm-3 col-form-label">Apellido materno*: </label>
                                                <div class="col-sm-3">
                                                    <input type="text" class="form-control" id="apellidoMaterno" name="apellidoMaterno" maxlength="40" oninput="soloLetras(event)">
                                                </div>

                                                <label id="lbltel" for="telefono" class="col-sm-3 col-form-label">Teléfono*: </label>
                                                <div class="col-sm-3">
                                                    <input class="form-control" type="tel" id="telefono" name="telefono" maxlength="10" pattern="[0-9]{10}" placeholder="10 dígitos">
                                                </div>
                                            </div>

                                            <div class="row mb-3">                                       
                                                <label id="lbled" for="edad" class="col-sm-3 col-form-label">Edad: </label>
                                                <div class="col-sm-3">
                                                    <input class="form-control" type="number" id="edad" name="edad" min="0" disabled style="appearance: none;">
                                                </div>

                                                <label id="lblmenor" class="col-sm-3 col-form-label">Es menor de edad: </label>
                                                <div class="col-sm-2 d-flex gap-3">
                                                    <label><input type="radio" class="form-check-input" name="menorEdad" value="si"><span id="lblsiMenor">Sí</span></label>
                                                    <label><input type="radio" class="form-check-input" name="menorEdad" value="no">No</label>
                                                </div>
                                            </div>

                                        </div>
                                        <!-- PERSONA QUE REPORTA -->
                                        <div id="datosPersonaReporta" class="hidden">
                                            <div class="row mb-3">
                                                <div id="divReporta" class="section-title" style="background-color: #611031; color:#ffffff; text-align: center;"><strong>Datos Persona que Reporta</strong></div>
                                            </div>                                                                   

                                            <div class="row mb-3">
                                                <label id="lblnoReporta"for="nombreReporta" class="col-sm-3 col-form-label">Nombre*: </label>
                                                <div class="col-sm-3">
                                                    <input type="text" class="form-control" id="nombreReporta" name="nombreReporta" maxlength="40" oninput="soloLetras(event)">
                                                </div>

                                                <label id="lblpaReporta" for="apellidoPaternoReporta" class="col-sm-3 col-form-label">Apellido paterno*:</label>
                                                <div class="col-sm-3">
                                                    <input type="text" class="form-control" id="apellidoPaternoReporta" name="apellidoPaternoReporta" maxlength="40" oninput="soloLetras(event)">
                                                </div>
                                            </div>

                                            <div class="row mb-3">
                                                <label id="lblmaReporta" for="apellidoMaternoReporta" class="col-sm-3 col-form-label">Apellido materno*: </label>
                                                <div class="col-sm-3">
                                                    <input type="text" class="form-control" id="apellidoMaternoReporta" name="apellidoMaternoReporta" maxlength="40" oninput="soloLetras(event)">
                                                </div>                                      
                                            </div>                                  
                                        </div>
                                                                                                
                                        <!-- PERSONA DE PERSONA MORAL -->
                                        <div id="datosPersonaMoral" class="hidden">

                                            <div class="row mb-3">
                                                <div id="divMoral" class="section-title" style="background-color: #611031; color:#ffffff; text-align: center;"><strong>Datos Persona Moral</strong></div>
                                            </div>
                                            
                                            <div class="row mb-3">
                                                <label id="lblMoral"for="moral" class="col-sm-5 col-form-label">Nombre de la Empresa / Institución*: </label>
                                                <div class="col-sm-5">
                                                    <input type="text" class="form-control" id="moral" name="moral" maxlength="50">
                                                </div>
                                            </div>
                                            <div class="row mb-3">                                                
                                                <label id="lbltelMoral" for="telMoral" class="col-sm-3 col-form-label">Teléfono*: </label>
                                                <div class="col-sm-3">
                                                    <input class="form-control" type="tel" id="telMoral" name="telMoral" maxlength="10" pattern="[0-9]{10}" placeholder="10 dígitos">
                                                </div>
                                            </div>                                                                               
                                        </div>

                                        <!-- REPORTE -->
                                        <div>
                                            <div class="row mb-3">
                                                <div id="divdc" class="section-title" style="background-color: #611031; color:#ffffff; text-align: center;"><strong>Describa aqui su reporte de Ciberseguridad </strong></div>
                                            </div>
                                        </div>

                                        <div class="row mb-3">
                                            <label id="lblcorreo" for="correo" class="col-sm-3 col-form-label">Correo*: </label>
                                            <div class="col-sm-3">
                                                <input class="form-control" type="email" id="correo" name="correo" maxlength="50">                                               
                                            </div>
                                            <label id="lblhechos" for="fechaHechos" class="col-sm-3 col-form-label">Fecha de los hechos*: </label>
                                            <div class="col-sm-3">
                                                <input class="form-control" type="date" id="fechaHechos" name="fechaHechos">
                                            </div>
                                        </div>

                                        <div class="row mb-3">
                                            <label id="lblcp" for="codigoPostal" class="col-sm-3 col-form-label">Código postal: </label>
                                            <div class="col-sm-3">
                                                <input class="form-control" type="text" id="codigoPostal" name="codigoPostal" maxlength="5" pattern="[0-9]{5}">
                                                <small id="smallMessage1" class="form-text text-muted">(Donde sucedieron los hechos)</small>                                              
                                            </div>

                                            <label id="lbledo" for="estado" class="col-sm-3 col-form-label">Estado*: </label>
                                            <div class="col-sm-3 position-relative">
                                                <select class="form-control pe-4" id="estado" name="estado" onchange="OnEstadoChange(this.value)" onfocus="GetSelectEstado()" style="appearance: none;">
                                                    <option id="optEstado" value="" disabled selected hidden>Seleccione:</option>
                                                </select>
                                                <span style="position: absolute; inset-inline-end: 20px; inset-block-start: 30%; transform: translateY(-50%); pointer-events: none;">
                                                    ▼
                                                </span>
                                                <small id="smallMessage2" class="form-text text-muted">(Donde sucedieron los hechos)</small>                                              

                                            </div>
                                        </div>

                                        <div class="row mb-3">
                                            <label id="lblmun" for="municipio" class="col-sm-3 col-form-label">Municipio*: </label>
                                            <div class="col-sm-3 position-relative">
                                                <select class="form-control pe-4" id="municipio" name="municipio" disabled style="appearance: none;">
                                                    <option id="optMunicipio" value="" disabled selected hidden>Seleccione:</option>
                                                </select>
                                                <span style="position: absolute; inset-inline-end: 20px; inset-block-start: 30%; transform: translateY(-50%); pointer-events: none;">
                                                    ▼
                                                </span>
                                                <small id="smallMessage3" class="form-text text-muted">(Donde sucedieron los hechos)</small>
                                            </div>

                                            <label id="lblcol" for="colonia" class="col-sm-3 col-form-label">Colonia: </label>
                                            <div class="col-sm-3">
                                                <input class="form-control" type="text" id="colonia" name="colonia" maxlength="60">
                                                <small id="smallMessage4" class="form-text text-muted">(Donde sucedieron los hechos)</small>  
                                            </div>
                                        </div>
                                        <!-- <hr style="border: none; block-size: 2px; background: #611031;"> -->

                                        <div class="row mb-3">
                                            <div class="row mb-3">
                                                <label id="lblmedio" for="medio" class="col-sm-12 col-form-label">¿A través de qué medio sucedió?*</label>
                                            </div>
                                            <div class="col-sm-12 position-relative">
                                                <select class="form-control pe-4" id="medio" name="medio" onfocus="GetSelectMedio()" style="appearance: none;">
                                                    <option id="optmedio" value="" disabled selected hidden>Seleccione:</option>
                                                </select>
                                                <span style="position: absolute; inset-inline-end: 20px; inset-block-start: 30%; transform: translateY(-50%); pointer-events: none;">
                                                    ▼
                                                </span>
                                                <small id="smallMessage5" class="form-text text-muted">(Donde sucedieron los hechos)</small>  
                                            </div>
                                        </div>

                                        <div class="row mb-3">
                                            <div class="row mb-3">
                                                <label id="lblocurrio" for="comoOcurrio" class="col-sm-3 col-form-label">¿Cómo ocurrió?* </label>
                                            </div>
                                            <div class="col-sm-12">
                                                <textarea class="form-control" id="comoOcurrio" name="comoOcurrio" maxlength="3000"></textarea>
                                                <div class="d-flex justify-content-between">
                                                    <small id="smallMessage6" class="form-text text-muted">(Descripción de los hechos)</small>
                                                    <div id="contador" style="font-size: 0.9em; color: #666;">3000 caracteres restantes</div>
                                                </div>
                                            </div>
                                        </div>                                        
                                        <div class="honeypot">
                                            <label for="website">CiberReportes</label>
                                            <input type="text" id="website" name="website" autocomplete="off">
                                        </div>

                                        <div class="row mb-3">                                                       
                                            <span id="URLPermitidas">Agregar la(s) URL's donde ocurrió</span>
                                        </div>

                                        <!-- Campo para agregar URLs -->
                                        <div class="row mb-2">
                                            <div class="col-12">
                                                <div class="urlbox">
                                                <input
                                                    id="urlInput"
                                                    class="form-control form-control-sm urlbox-input"
                                                    type="url"
                                                    inputmode="url"
                                                    placeholder="www.ejemplo.com/ruta"
                                                    aria-label="Agregar URL"
                                                    autocomplete="off"
                                                />
                                                <button id="btnAgregarURL" type="button" class="btn btn-primary btn-sm urlbox-btn">
                                                    SUBIR URL
                                                </button>
                                                </div>
                                                <small class="text-muted d-block mt-1" id="urlHelp"></small><br>
                                            </div>
                                        </div>
                                        <!-- Lista de URLs agregadas -->
                                        <div class="row mb-3" id="urlsListWrap" style="display:none;">
                                            <div class="col-12">
                                                <ul id="urlsList" class="list-group list-group-flush url-list"></ul>
                                            </div>
                                        </div>

                                        <div class="row mb-3">                                                       
                                            <span id="archivoPermitido">Se permiten archivos: (.jpg, .jpeg, .png, .pdf, .docx, .mp3, .aac, .opus, .ogg, .mp4)</span>
                                        </div>

                                        <div id="upload-area" class="upload-box text-center">
                                            <input type="file" id="fileInput" multiple hidden>
                                            <div class="upload-content">
                                                <button id="subirArchivo" type="button" class="btn btn-primary btn-sm BtnsubirArchivo">SUBIR ARCHIVO</button>
                                                <p id="arrastrar" class="text-muted">Arrástralo aquí</p>
                                            </div>
                                        </div>

                                        <div id="file-size-info" class="mt-2 text-muted" style="display: none;">
                                            Total seleccionado: 0 MB / 10 MB
                                        </div>

                                        <div class="mt-3" id="file-list-container" style="display:none;">
                                            <h6>Archivos seleccionados:</h6>
                                            <ul id="file-list" class="fl-list"></ul>
                                        </div>

                                        <div class="row mb-3 captchaBox" style="text-align: center;">
                                            <div style="margin-block-end:1em;">
                                                <canvas id="captchaCanvas" width="150" height="50"></canvas><br>
                                                <!-- <button type="button" onclick="generarCaptcha()" style="margin-inline-start:10px;">Recargar</button>-->
                                            </div>
                                            <div style="text-align: center;">
                                                <input class="form-control" type="text" id="captchaInput" required placeholder="Escriba el captcha" maxlength="10" style="inline-size: 170px; margin-inline-start: auto;margin-inline-end: auto; text-align: center;">
                                            </div>
                                            <div id="captchaError" style="color:red; display:none;"></div>
                                            <div style="text-align: center; margin-block-start: 10px;">
                                                <button id="enviarReporte" class="btn btn-dark" type="submit" style="background-color: #611031; margin-block-start: 10px;">ENVIAR REPORTE</button>
                                            </div>
                                        </div>

                                    </div>
                            </div>
                            <div class="card-footer text-center">
                                <img src="img/rcimg1.png" class="img-fluid" alt="Descripción" style="max-inline-size: auto;">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- inicio de Modales -->
        <div class="modal fade" id="autoModal" tabindex="-1" aria-labelledby="autoModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content bg-red-translucent text-white">
                    <div class="modal-header border-0">
                        <h2 class="modal-title w-100 text-center" id="autoModalLabel">Aviso de privacidad</h2>
                        <!-- <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Cerrar"></button> -->
                    </div>                    
                    <div class="modal-body avisoPrivacidad">
                        AVISO DE PRIVACIDAD

                        La Secretaría de Seguridad y Protección Ciudadana (SSPC) a través de la Unidad de Inteligencia, Investigación Cibernética y Operaciones Tecnológicas (UIICOT), con domicilio ubicado en Avenida Constituyentes No. 947, Colonia Belén de las Flores, Alcaldía Álvaro Obregón, C.P. 01110 en la Ciudad de México, es la responsable del tratamiento de los datos personales que se proporcionen, los cuales serán protegidos conforme a lo establecido por la Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados y demás normativa aplicable del caso concreto.

                        DATOS PERSONALES QUE SERÁN SOMETIDOS A TRATAMIENTO

                        • La Unidad de Inteligencia, Investigación Cibernética y Operaciones Tecnológicas (UIICOT), tratará los datos personales que se desprendan de las búsquedas realizadas en el Sistema Web para el Registro de Reportes de Incidentes Cibernéticos, en los términos de la Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados y demás disposiciones aplicables.

                        Los datos personales que se recabarán son los siguientes:

                        • Datos de identificación: Nombre, apellido paterno, apellido materno, CURP, edad, fecha de nacimiento, confirmación si es menor de edad.

                        • Datos de contacto: Domicilio (código postal, estado, municipio, colonia) teléfono y correo electrónico.

                        FUNDAMENTO LEGAL PARA EL TRATAMIENTO DE DATOS PERSONALES

                        La Unidad de Inteligencia, Investigación Cibernética y Operaciones Tecnológicas (UIICOT), tratará los datos personales antes señalados con fundamento en lo dispuesto por los artículos 6, Inciso A y 16, párrafo segundo de la Constitución Política de los Estados Unidos Mexicanos; 3, fracción III, 7, 12, 14, fracción III, 15 segundo párrafo, 18, 19, 20, 21, 22, 23, 26, 27, 28, 65 y 85, fracción II de la Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados; 41, 45, 56, 64 y 68 de la Ley General de Transparencia y Acceso a la Información Pública; 
                        
                        31, 32, 33, 34, y 35 de la Ley Nacional del Registro de Detenciones; numerales Octavo fracción III y Décimo Segundo inciso B de los Lineamientos para el Funcionamiento, Operación y Conservación del Registro Nacional de Detenciones (RND); 64 fracción XXVI, 69 fracciones VIII, IX, X, y XVI del Reglamento Interior de la Secretaría de Seguridad y Protección Ciudadana; y artículo 27, 28, 29, 31, y 40 de los Lineamientos Generales de Protección de Datos Personales para el Sector Público.

                        FINALIDADES DEL TRATAMIENTO

                        La Unidad de Inteligencia, Investigación Cibernética y Operaciones Tecnológicas (UIICOT), hace de su conocimiento que la finalidad del tratamiento aplicado a sus datos personales es la siguiente:

                        • Implementará las herramientas tecnológicas, con la finalidad de almacenar y administrar la información e instrumentar las acciones de coordinación con los tres órdenes de gobierno para el cumplimiento de los fines del “Sistema Web para el Registro de Reportes de Incidentes Cibernéticos”, para las personas que realicen la consulta.

                        TRANSFERENCIA DE LA INFORMACIÓN Y EXCEPCIONES AL CONSENTIMIENTO

                        La Unidad de Inteligencia, Investigación Cibernética y Operaciones Tecnológicas (UIICOT), trata y conserva los datos personales favoreciendo en todo momento el derecho a la privacidad y a la protección de los mismos, por lo que los datos personales que se administren no serán transferidos, salvo que se actualice alguna de las excepciones previstas en los artículos 22 fracción II, 66 y 70 de la Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados.

                        MECANISMO PARA MANIFESTAR LA NEGATIVA DEL TRATAMIENTO DE LOS DATOS PERSONALES RECABADOS.

                        De conformidad con el artículo 52 de la Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados, se pone a su disposición el correo electrónico <a href="transparencia@sspc.gob.mx" target="_blank" rel="noopener noreferrer" class="link-light">transparencia@sspc.gob.mx</a>, con la finalidad de que a través de la Unidad de Transparencia de la Secretaría de Seguridad y Protección Ciudadana, o bien, directamente en el Módulo de Transparencia ubicado en Avenida Constituyentes N° 947, colonia Belén de las Flores, alcaldía Álvaro Obregón, C.P. 01110 en la Ciudad de México, pueda manifestar su negativa para la finalidad y transferencia que requieran el consentimiento de la o el titular.

                        MECANISMOS PARA EJERCER LOS DERECHOS ARCO

                        Tiene derecho a conocer qué datos personales tenemos de usted, para qué los utilizamos y las condiciones de su uso (Acceso). Asimismo, es su derecho solicitar la corrección de su información personal en caso de que sea inexacta, esté desactualizada o incompleta (Rectificación); que la eliminemos de nuestros registros o bases de datos cuando considere que la misma no está siendo utilizada conforme a los principios, deberes y obligaciones previstas en el marco normativo (Cancelación); así como oponerse al uso de sus datos personales para fines específicos (Oposición). 
                        
                        Estos derechos se conocen como derechos ARCO. Para ejercicio de cualquiera de los Derechos ARCO, Usted o su representante legal deberán presentar la solicitud respectiva, a través de la Plataforma Nacional de Transparencia en la siguiente liga:

                        <a href="https://www.plataformadetransparencia.org.mx/web/guest/inicio" target="_blank" rel="noopener noreferrer" class="link-light">https://www.plataformadetransparencia.org.mx/web/guest/inicio</a>

                        También puede presentarse al Módulo de Transparencia de la Secretaría de Seguridad y Protección Ciudadana ubicado en Avenida Constituyentes N° 947, Colonia Belén de

                        las Flores, Alcaldía Álvaro Obregón, Código Postal 01110, Ciudad de México, Teléfono (55) 1103 6000, extensión 11444, correo electrónico: <a href="transparencia@sspc.gob.mx" target="_blank" rel="noopener noreferrer" class="link-light">transparencia@sspc.gob.mx</a>.

                        Para que se pueda dar seguimiento a su solicitud, usted o su representante legal, deberán acreditar correctamente su identidad (Nombre completo, domicilio o correo electrónico, con documentos oficiales INE, Pasaporte o cédula profesional; en el caso del representante legal se requiere acreditar la representación con carta poder firmada ante dos testigos o poder otorgado ante fedatario público e identificación del representante legal, así como la descripción clara y precisa de los datos personales respecto de los que se busca ejercer.

                        PORTABILIDAD DE DATOS PERSONALES

                        La Unidad de Inteligencia, Investigación Cibernética y Operaciones Tecnológicas (UIICOT), actualmente no cuenta con formatos estructurados y comúnmente utilizados para la portabilidad de datos personales, en términos de lo dispuesto en los artículos 57 de la Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados y 8 de los Lineamientos que establecen los Parámetros, Modalidades y Procedimientos para la Portabilidad de Datos Personales, por lo que no es posible hacer la aplicación de la portabilidad de datos personales por el momento.

                        DOMICILIO DE LA UNIDAD DE TRANSPARENCIA

                        Avenida Constituyentes N° 947, Colonia Belén de las Flores, Alcaldía Álvaro Obregón, Código Postal 01110, Ciudad de México.

                        CAMBIOS AL AVISO DE PRIVACIDAD

                        En caso de que exista un cambio o actualización lo haremos de su conocimiento, a través del siguiente vínculo electrónico disponible para su consulta en la siguiente dirección electrónica:

                        <a href="https://www.gob.mx/cms/uploads/attachment/file/782879/AVISO_DE_PRIVACIDAD_SISTEMA_DE_INCIDENTES.pdf" target="_blank" rel="noopener noreferrer" class="link-light">AVISO_DE_PRIVACIDAD_SISTEMA_DE_INCIDENTES</a>

                    </div>
                    <div class="modal-footer border-0 justify-content-center">
                        <button type="button" class="btn btn-light" data-bs-dismiss="modal">Aceptar</button>
                    </div>
                </div>
            </div>
        </div>
    
        <div class="modal fade" id="successModal" tabindex="-1" aria-labelledby="successModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content custom-modal-content-true">
                    <div class="modal-body text-center">
                        <!-- Icono de check -->
                        <div class="check-icon mb-3">
                            <svg width="90" height="90" fill="none" stroke="#196f3d" stroke-width="6" viewBox="0 0 90 90">
                                <circle cx="45" cy="45" r="40" stroke="#196f3d" stroke-width="4" fill="none" />
                                <polyline points="30,50 42,62 62,36" stroke="#196f3d" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>
                        <!-- Título -->
                        <div id="ModalTitle" class="fw-bold modal-title-custom-true mb-3">REGISTRO<br>CORRECTO</div>
                        <!-- Texto informativo -->
                        <div id="modalFolio" class="modal-info msgCorrecto mb-4">
                           
                        </div>
                        <!-- Botón -->
                        <button type="button" class="btn custom-btn-true" id="btnAceptarTrue" data-bs-dismiss="modal">Aceptar</button>
                    </div>
                </div>
            </div>
        </div>
        

        <div class="modal fade" id="errorModal" tabindex="-1" aria-labelledby="errorModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content custom-modal-content">
                    <div class="modal-body text-center">
                        <!-- Icono de X -->
                        <div class="check-icon mb-3">
                            <svg width="90" height="90" fill="none" stroke="#7C2946" stroke-width="6" viewBox="0 0 90 90">
                                <circle cx="45" cy="45" r="40" stroke="#7C2946" stroke-width="4" fill="none" />
                                <line x1="30" y1="30" x2="60" y2="60" stroke="#7C2946" stroke-width="6" stroke-linecap="round" />
                                <line x1="60" y1="30" x2="30" y2="60" stroke="#7C2946" stroke-width="6" stroke-linecap="round" />
                            </svg>
                        </div>

                        <!-- Mensaje dinámico -->
                        <div id="errorModalMessage" class="modal-info mb-4">
                        </div>

                        <!-- Botón -->
                        <button type="button" class="btn custom-btn" data-bs-dismiss="modal">Aceptar</button>
                    </div>
                </div>
            </div>
        </div>

<!-- Modal para reproducir video -->
        <div class="modal fade" id="videoModal" tabindex="-1" aria-labelledby="videoModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content bg-dark">
                    <div class="modal-header border-0">
                        <h2 class="modal-title w-100 text-center text-white" id="videoModalLabel">Guía de uso</h2>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                    </div>
                    <div class="modal-body" style="background-color: #000;">
                        <video id="videoPlayer" width="100%" controls style="border-radius: 8px;" controlsList="nodownload">
                            <source id="videoSource" src="img/video.mp4" type="video/mp4">
                            Tu navegador no soporta el elemento de video.
                        </video>
                    </div>
                </div>
            </div>
        </div>
 <!-- fin de Modales -->

 <!-- Loader overlay -->
    <div id="loaderOverlay" class="loader-overlay" aria-live="polite" aria-busy="false" hidden>
        <div class="loader-content">
            <div class="spinner-border" role="status" aria-hidden="true"></div>
            <div id="loaderText" class="mt-3 fw-semibold">Registrando reporte…</div>
        </div>
    </div>
 <!-- fin Loader overlay -->

    </section>
    <script src="<?php echo $jsPath; ?>rcscript.js"></script>

    <!-- Script para manejar modales en cascada -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const autoModal = document.getElementById('autoModal');
            const videoModal = document.getElementById('videoModal');
            
            if (autoModal) {
                autoModal.addEventListener('hidden.bs.modal', function () {
                    // Esperar 500ms a que se cierre la animación
                    setTimeout(function() {
                        // Mostrar el modal de video
                        const modalInstance = new bootstrap.Modal(videoModal);
                        modalInstance.show();
                    }, 500);
                });
            }

	// Pausar el video cuando se cierre el modal
            if (videoModal) {
                videoModal.addEventListener('hidden.bs.modal', function () {
                    if (videoPlayer) {
                        videoPlayer.pause();
                        videoPlayer.currentTime = 0;
                    }
                });
            }
        });

        // Función para abrir video en el modal (puedes usarla desde JavaScript o eventos)
        function playVideoInModal(videoUrl) {
            const videoSource = document.getElementById('videoSource');
            const videoPlayer = document.getElementById('videoPlayer');
            videoSource.src = videoUrl;
            videoPlayer.load();
            
            const videoModal = new bootstrap.Modal(document.getElementById('videoModal'));
            videoModal.show();
        }
    </script>
    
<!-- ===== Asistente RC: UI flotante ===== -->
<!-- COMENTADO TEMPORALMENTE -->
<style>
    .nova-bot-toggle {
        position: fixed;
        inset-inline-end: 60px;
        inset-block-end: 18px;
        z-index: 2147483000;
        padding: 12px 16px;
        border-radius: 999px;
        border: 0;
        cursor: pointer;
        background: linear-gradient(135deg, #611031, #611031);
        color: #fff;
        font-weight: 700;
        box-shadow: 0 10px 25px rgba(0, 0, 0, .25);
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }

    .nova-bot-toggle:focus {
        outline: 3px solid rgba(255, 255, 255, .6);
        outline-offset: 2px;
    }

    .nova-pulse {
        animation: novaPulse 2s infinite;
    }

    @keyframes novaPulse {
        0% {
            box-shadow: 0 0 0 0 rgba(0, 172, 193, .6)
        }

        70% {
            box-shadow: 0 0 0 16px rgba(0, 172, 193, 0)
        }

        100% {
            box-shadow: 0 0 0 0 rgba(0, 172, 193, 0)
        }
    }

    .nova-bot-panel {
        position: fixed;
        inset-inline-end: 18px;
        inset-block-end: 82px;
        inline-size: min(494px, 92vw);
        block-size: 480px;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 24px 60px rgba(0, 0, 0, .35);
        background: #0b1220;
        z-index: 2147483000;
        display: none;
    }

    .nova-bot-panel header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 12px;
        background: linear-gradient(135deg, #611031, #611031);
        color: #fff;
        gap: 8px;
    }

    .nova-bot-title-group {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
        min-width: 0;
        flex-wrap: nowrap;
        overflow: hidden;
    }

    .nova-bot-title {
        font-size: 15px;
        font-weight: 700;
        letter-spacing: .3px;
        white-space: nowrap;
    }

    .nova-bot-ia-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 999px;
        border: 1px solid rgb(107, 142, 35);
        background: rgba(107, 142, 35, 0.25);
        color: #cfe87a;
        cursor: pointer;
        white-space: nowrap;
        transition: background 0.2s, box-shadow 0.2s;
    }

    .nova-bot-ia-chip:hover {
        background: rgba(107, 142, 35, 0.45);
        box-shadow: 0 0 8px rgba(107, 142, 35, 0.5);
    }

    .nova-bot-rag-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 999px;
        border: 1px solid #b8860b;
        background: rgba(184, 134, 11, 0.2);
        color: #f0c040;
        cursor: pointer;
        white-space: nowrap;
        transition: background 0.2s, box-shadow 0.2s;
    }

    .nova-bot-rag-chip:hover {
        background: rgba(184, 134, 11, 0.45);
        box-shadow: 0 0 8px rgba(184, 134, 11, 0.5);
    }

    .nova-bot-actions button {
        background: transparent;
        border: 0;
        color: #fff;
        cursor: pointer;
        padding: 6px;
    }

    .nova-bot-iframe {
        inline-size: 100%;
        block-size: calc(100% - 46px);
        border: 0;
        background: #111827;
    }

    .nova-hidden {
        display: none !important;
    }
</style>

<div id="novaBotPanel" class="nova-bot-panel" role="dialog" aria-modal="false" aria-label="Asistente de Reporte Cibernético">
    <header>
        <div class="nova-bot-title-group">
            <div class="nova-bot-title">Ciber Agente</div>
            <div class="nova-bot-ia-chip" title="Cambiar a Asistente IA (Ollama)"
                 onclick="document.getElementById('novaBotFrame').contentWindow.postMessage({type:'nova-switch-project', project:'ollama', breadcrumb:{state:'OLLAMA', label:'Asistente IA'}}, '*')">
                 🤖 Asistente IA
            </div>
            <div class="nova-bot-rag-chip" title="Consultar Glosario RAG"
                 onclick="document.getElementById('novaBotFrame').contentWindow.postMessage({type:'nova-switch-project', project:'rag', breadcrumb:{state:'GLOSARY', label:'Glosario'}}, '*')">
                 📖 Glosario
            </div>
        </div>
        <div class="nova-bot-actions">
            <button id="novaBotMinBtn" type="button" aria-label="Minimizar">—</button>
            <button id="novaBotCloseBtn" type="button" aria-label="Cerrar">✕</button>
        </div>
    </header>
    <iframe id="novaBotFrame" class="nova-bot-iframe" src="<?php echo $assistantPath; ?>" title="Asistente en línea"></iframe>
</div>

<button id="novaBotToggle" type="button" class="nova-bot-toggle nova-pulse" aria-controls="novaBotPanel" aria-expanded="false">
    🤖
</button>

<script>
    (() => {
        // ==== Configuración ====
        const INACTIVITY_MS = 2000000; // 2000s sin interacción -> ocultar panel
        const REAPPEAR_MS = 30000; // 30s -> reaparecer si no fue "cerrado por el usuario"

        // ==== Elementos ====
        const panel = document.getElementById('novaBotPanel');
        const frame = document.getElementById('novaBotFrame');
        const toggle = document.getElementById('novaBotToggle');
        const btnMin = document.getElementById('novaBotMinBtn');
        const btnClose = document.getElementById('novaBotCloseBtn');

        // ==== Estado persistente ====
        const LS_CLOSED = 'novaBotWidgetClosed'; // "1" = no auto-reaparecer
        const LS_MIN = 'novaBotWidgetMin'; // "1" = minimizado
        let inactivityTimer = null,
            reappearTimer = null;

        const isClosedByUser = () => localStorage.getItem(LS_CLOSED) === '1';
        const setClosedByUser = (v) => localStorage.setItem(LS_CLOSED, v ? '1' : '0');

        const isMinimized = () => localStorage.getItem(LS_MIN) === '1';
        const setMinimized = (v) => localStorage.setItem(LS_MIN, v ? '1' : '0');

        // ==== Mostrar/Ocultar ====
        function showPanel() {
            if (isClosedByUser()) return; // respetar decisión del usuario
            panel.style.display = 'block';
            toggle.setAttribute('aria-expanded', 'true');
            resetInactivityTimer();
        }

        function hidePanel() {
            panel.style.display = 'none';
            toggle.setAttribute('aria-expanded', 'false');
            clearTimeout(inactivityTimer);
        }

        function minimizePanel() {
            setMinimized(true);
            hidePanel();
            // Reaparecerá por timer o por focus en inputs del form
        }

        function openPanelFromUserAction() {
            setClosedByUser(false);
            setMinimized(false);
            showPanel();
            // Dar foco seguro
            try {
                frame.focus();
            } catch {}
        }

        function closePanelByUser() {
            setClosedByUser(true);
            hidePanel();
        }

        // ==== Timers de inactividad/reaparición ====
        function resetInactivityTimer() {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(() => {
                // Solo ocultar si está visible
                if (panel.style.display !== 'none') hidePanel();
            }, INACTIVITY_MS);
        }

        function scheduleReappear() {
            clearTimeout(reappearTimer);
            reappearTimer = setTimeout(() => {
                if (!isClosedByUser() && isMinimized()) {
                    showPanel();
                } else if (!isClosedByUser() && panel.style.display === 'none') {
                    // si no está minimizado, pero está oculto por inactividad, también puede reaparecer
                    showPanel();
                }
            }, REAPPEAR_MS);
        }

        // ==== Eventos ====
        // Botón flotante
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (panel.style.display === 'none') openPanelFromUserAction();
            else hidePanel();
        });

        // Minimizar y Cerrar
        btnMin.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            minimizePanel();
            scheduleReappear();
        });
        btnClose.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            closePanelByUser();
        });

        // Interacción general de la página -> reset de inactividad
        ['click', 'keydown', 'mousemove', 'scroll', 'touchstart'].forEach(evt => {
            window.addEventListener(evt, () => {
                if (panel.style.display !== 'none') resetInactivityTimer();
            }, {
                passive: true
            });
        });

        // Reaparecer si el usuario enfoca inputs del formulario
        document.addEventListener('focusin', (e) => {
            const isFormFocus = !!e.target.closest('form');
            if (isFormFocus && !isClosedByUser()) {
                setMinimized(false);
                showPanel();
            }
        });

        // Mensajes desde el iframe del bot -> cuentan como interacción
        window.addEventListener('message', (e) => {
            if (e && e.data && e.data.type === 'nova-bot-interaction') {
                if (panel.style.display !== 'none') resetInactivityTimer();
            }
        });

        // Defensa: si por layout el botón quedara dentro de un <form>, no debe enviar el form
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('button#novaBotToggle');
            if (!btn) return;
            const form = btn.closest('form');
            if (form) {
                e.preventDefault();
                e.stopPropagation();
            }
        }, true);

        // Iniciar cerrado por defecto
        // El usuario debe hacer clic en el botón para abrir
        hidePanel();
        
        // Plan de reaparición cíclico (solo si el usuario ya lo abrió antes)
        if (!isClosedByUser() && isMinimized()) {
            scheduleReappear();
        }
    })();
</script>
<!-- FIN COMENTARIO -->

    <a href="#" class="back-to-top d-flex align-items-center justify-content-center bg-dark"><i class="bi bi-arrow-up-short"></i></a>
    <script src="<?php echo $vendorPath; ?>apexcharts/apexcharts.min.js"></script>
    <script src="<?php echo $vendorPath; ?>bootstrap/js/bootstrap.bundle.min.js"></script>
    <script src="<?php echo $vendorPath; ?>echarts/echarts.min.js"></script>
    <script src="<?php echo $vendorPath; ?>quill/quill.min.js"></script>
    <script src="<?php echo $vendorPath; ?>tinymce/tinymce.min.js"></script>
    <script src="<?php echo $vendorPath; ?>php-email-form/validate.js"></script>
    <script src="<?php echo $jsPath; ?>main.js"></script>
    <script src="<?php echo $jsPath; ?>jquery-3.6.1.js"></script>
</body>

</html>
