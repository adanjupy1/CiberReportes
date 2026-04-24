    const textoIdioma = ['Idioma', 'Language'];
    let index = 0;
    const label = document.getElementById('fakeText');

    window.addEventListener('DOMContentLoaded', () => {
        const bait = document.querySelector('input[name="info_confirm"]');
        if (bait) bait.remove();
    });

    //Intervalo del input idioma
    setInterval(() => {
        label.classList.add('fade-up');
        setTimeout(() => {
            index = (index + 1) % textoIdioma.length;
            label.textContent = textoIdioma[index];
            label.classList.remove('fade-up');
        }, 500);
    }, 3000);

    //OVERLAY
    function showLoader(msgKey) {
    const overlay = document.getElementById('loaderOverlay');
    if (!overlay) return;

    const D = (typeof dic === 'function') ? dic() : (window.textos?.es || {});
    const textEl = document.getElementById('loaderText');
    if (textEl){
        const key = msgKey || 'loaderRegistering';
        textEl.textContent = D[key] || D.loaderRegistering || '...';
    }

    overlay.hidden = false;
    overlay.setAttribute('aria-busy', 'true');
    }

    function hideLoader() {
    const overlay = document.getElementById('loaderOverlay');
    if (!overlay) return;
    overlay.hidden = true;
    overlay.setAttribute('aria-busy', 'false');
    }

    /* showLoader(); */

    //LETRAS EN MAYUSCULAS
    document.getElementById('curp').addEventListener('input', function() {
        this.value = this.value.toUpperCase();
    });
    
    /* LOGICAS DE CHECKBOXES */
    const anonimos = document.getElementsByName('anonimo');
    const fisica = document.getElementsByName('fisica');
    const boxAfectado = document.getElementsByName('afectado');

    const trTipoPersona = document.querySelector('tr[name="trTipoPersona"]');
    const trAfectado = document.querySelector('tr[name="trAfectado"]');
    const trExtranjero = document.querySelector('tr[name="trExtranjero"]')

    const datosPersonaDiv = document.getElementById('datosPersona');
    const datosPersonaReporta = document.getElementById('datosPersonaReporta');
    const datosPersonaMoral = document.getElementById('datosPersonaMoral');

    /* FUNCION PARA LIMPIAR INPUTS AL OCULTAR */
    function setVisibility(section, show) {
        if (!section) return;

        if (show) {
            section.classList.remove('hidden');
            section.querySelectorAll('input, select, textarea').forEach(el => {
                el.disabled = false;
            });
        } else {
            section.classList.add('hidden');
            section.querySelectorAll('input, select, textarea').forEach(el => {
                if (el.type !== 'radio' && el.type !== 'checkbox') {
                    el.value = "";  
                }
                el.disabled = true; 
            });
        }
    }

    function actualizarSecciones() {
        const anonimo = document.querySelector('input[name="anonimo"]:checked')?.value;
        const esFisica = document.querySelector('input[name="fisica"]:checked')?.value;
        const afectado = document.querySelector('input[name="afectado"]:checked')?.value;

        // Mostrar filas por defecto
        trTipoPersona.classList.remove('hidden');
        trAfectado.classList.remove('hidden');
        trExtranjero.classList.remove('hidden');

        if (anonimo === 'si') {
            trTipoPersona.classList.add('hidden');
            trAfectado.classList.add('hidden');
            trExtranjero.classList.add('hidden');

            setVisibility(datosPersonaDiv, false);
            setVisibility(datosPersonaReporta, false);
            setVisibility(datosPersonaMoral, false);

        } else if (anonimo === 'no') {
            if (esFisica === 'no') {
                // Persona moral
                setVisibility(datosPersonaMoral, true);

                // Ocultar siempre afectado y extranjero
                trAfectado.classList.add('hidden');
                trExtranjero.classList.add('hidden');

                setVisibility(datosPersonaDiv, false);
                setVisibility(datosPersonaReporta, false);

            } else if (esFisica === 'si') {
                // Persona física
                setVisibility(datosPersonaDiv, true);

                if (afectado === 'no') {
                    setVisibility(datosPersonaReporta, true);
                } else {
                    setVisibility(datosPersonaReporta, false);
                }

                trExtranjero.classList.remove('hidden');
                setVisibility(datosPersonaMoral, false);
            }
        }
    }

    // listeners
    anonimos.forEach(el => el.addEventListener('change', actualizarSecciones));
    fisica.forEach(el => el.addEventListener('change', actualizarSecciones));
    boxAfectado.forEach(el => el.addEventListener('change', actualizarSecciones));

    // inicializar estado
    actualizarSecciones();

    // Mostrar/ocultar CURP
    const extranjero = document.getElementsByName('extranjero');
    const curpLabel = document.getElementById('lblcurp');
    const curpDiv = document.getElementById('curpDiv');
    const curpInput  = document.getElementById('curp');

    extranjero.forEach(r => {
        r.addEventListener('change', () => {
            const mostrarCurp = r.checked && r.value === 'no'; 
            setVisibility(curpDiv, mostrarCurp);               

            // sincroniza label y asegura limpieza cuando se oculta
            curpLabel?.classList.toggle('hidden', !mostrarCurp);
            if (!mostrarCurp && curpInput) {
            curpInput.value = '';
            curpInput.disabled = true;  // doble seguro
            } else if (curpInput) {
            curpInput.disabled = false;
            }
        });
    });

    // Estado inicial de CURP (por si ya viene seleccionado al cargar)
    (function initCurp(){
    const val = document.querySelector('input[name="extranjero"]:checked')?.value;
    const mostrarCurp = (val === 'no'); // mexicanos → mostrar CURP
    setVisibility(curpDiv, mostrarCurp);
    curpLabel?.classList.toggle('hidden', !mostrarCurp);
    if (!mostrarCurp && curpInput) { curpInput.value = ''; curpInput.disabled = true; }
    else if (curpInput) { curpInput.disabled = false; }
    })();

    // Mostrar/ocultar institucion
    const instRadios = document.getElementsByName('institucion');
    const instDiv = document.getElementById('instDiv');
    instRadios.forEach(r => {
        r.addEventListener('change', () => {
            if (r.checked && r.value === 'si') {
                instDiv.classList.remove('hidden');
            } else if (r.checked && r.value === 'no') {
                instDiv.classList.add('hidden');
            }
        });
    });

    document.addEventListener('DOMContentLoaded', function () {
        const today = new Date();
        const formatted = today.toISOString().split('T')[0];
        document.getElementById('fechaNacimiento').setAttribute('max', formatted);
        document.getElementById('fechaHechos').setAttribute('max', formatted);

        const minDateHechos = '1990-01-01';
        const minDateNacimiento = "1900-01-01";
        document.getElementById('fechaNacimiento').setAttribute('min', minDateNacimiento);
        document.getElementById('fechaHechos').setAttribute('min', minDateHechos);

        const fechaNacimientoInput = document.getElementById('fechaNacimiento');
        const edadInput = document.getElementById('edad');
        const curpInput = document.getElementById('curp');

        curpInput.addEventListener('input', function () {
            const curp = this.value.trim().toUpperCase();

            if (curp.length >= 10) {
                const anio = parseInt(curp.substring(4, 6), 10);
                const mes = parseInt(curp.substring(6, 8), 10) - 1;
                const dia = parseInt(curp.substring(8, 10), 10);
              
                const yearFull = (anio <= new Date().getFullYear() % 100 ? 2000 : 1900) + anio;

                const fecha = new Date(yearFull, mes, dia);

                if (!isNaN(fecha.getTime())) {
                    const fechaISO = fecha.toISOString().split('T')[0];
                    fechaNacimientoInput.value = fechaISO;
                    fechaNacimientoInput.disabled = true;

                    fechaNacimientoInput.dispatchEvent(new Event('change'));
                } else {
                    fechaNacimientoInput.disabled = false;
                }
            }else{
                fechaNacimientoInput.disabled = false;
            }
        });

        fechaNacimientoInput.addEventListener('change', function () {
            if (!this.value) {
                edadInput.value = "";
                return;
            }

            const fechaNac = new Date(this.value);
            const hoy = new Date();

            let edad = hoy.getFullYear() - fechaNac.getFullYear();
            const mes = hoy.getMonth() - fechaNac.getMonth();

            if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNac.getDate())) {
                edad--;
            }

            edadInput.disabled = false;
            edadInput.value = edad >= 0 ? edad : 0;
            edadInput.disabled = true;

            const menorSi = document.querySelector('input[name="menorEdad"][value="si"]');
            //console.log('menor si = ' + menorSi)
            const menorNo = document.querySelector('input[name="menorEdad"][value="no"]');
            //console.log('menor No = ' + menorSi)

            if (edad >= 18) {
                if (menorNo) {
                    menorNo.disabled = false; 
                    menorNo.checked = true;  
                    menorNo.disabled = true;
                }
                if (menorSi) {
                    menorSi.disabled = false;
                    menorSi.checked = false;
                    menorSi.disabled = true;
                }
            } else {
                if (menorSi) {
                    menorSi.disabled = false;
                    menorSi.checked = true;
                    menorSi.disabled = true;
                }
                if (menorNo) {
                    menorNo.disabled = false;
                    menorNo.checked = false;
                    menorNo.disabled = true;
                }
            }
        });
    });


    const textarea = document.getElementById('comoOcurrio');
    const contador = document.getElementById('contador');
    const max = 3000;

    textarea.addEventListener('input', function() {
        const remaining = max - textarea.value.length;
        contador.textContent = remaining + " caracteres restantes";
    });

    /* SECCION SUBIR ARCHIVOS */
    let modalInstance = null;

    function ErrorModal(mensaje) {
        const mensajeDiv = document.getElementById('errorModalMessage');
        mensajeDiv.innerHTML = mensaje;

        // Si ya existe un modal abierto, ciérralo y limpia el backdrop
        if (modalInstance) {
            modalInstance.hide();
            document.querySelectorAll('.modal-backdrop').forEach(e => e.remove());
        }

        // Crear o reutilizar la instancia
        modalInstance = bootstrap.Modal.getInstance(document.getElementById('errorModal')) 
            || new bootstrap.Modal(document.getElementById('errorModal'));

        modalInstance.show();
    }

    const fileInput = document.getElementById("fileInput");
    const uploadArea = document.getElementById("upload-area");
    const fileList = document.getElementById("file-list");
    const fileListContainer = document.getElementById("file-list-container");

    let selectedFiles = [];

    uploadArea.addEventListener("click", () => fileInput.click());

    uploadArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadArea.classList.add("dragover");
    });

    uploadArea.addEventListener("dragleave", () => {
        uploadArea.classList.remove("dragover");
    });

    uploadArea.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadArea.classList.remove("dragover");
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener("change", (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        const nuevosArchivos = Array.from(files);
        const extensionesPermitidas = ['jpg', 'jpeg', 'png', 'pdf', 'docx', 'mp3', 'aac', 'opus', 'ogg', 'mp4'];
        const LIMITE_TOTAL_MB = 10;
        const LIMITE_TOTAL_BYTES = LIMITE_TOTAL_MB * 1024 * 1024;

        const D = (typeof dic === 'function') ? dic() : (window.textos?.es || {}); // ← i18n
        let totalActual = selectedFiles.reduce((sum, f) => sum + f.size, 0);
        let errores = [];

        for (let nuevo of nuevosArchivos) {
            const extension = nuevo.name.split('.').pop().toLowerCase();

            // Validar extensión
            if (!extensionesPermitidas.includes(extension)) {
            errores.push((D.fileExtNotAllowed || 'El archivo "{name}" no tiene un formato permitido.')
                .replace('{name}', nuevo.name));
            continue;
            }

            // Validar tamaño total acumulado
            if ((totalActual + nuevo.size) > LIMITE_TOTAL_BYTES) {
            errores.push((D.fileTotalLimitExceeded || 'El archivo "{name}" excede el límite total de {limit} MB.')
                .replace('{name}', nuevo.name)
                .replace('{limit}', LIMITE_TOTAL_MB));
            continue;
            }

            // Validar duplicados (nombre y tamaño)
            const yaExiste = selectedFiles.some(f => f.name === nuevo.name && f.size === nuevo.size);
            if (yaExiste) continue;

            // ✅ Se agrega archivo válido
            selectedFiles.push(nuevo);
            totalActual += nuevo.size;
        }

        // Mostrar modal si hubo errores
        if (errores.length > 0) {
            const listaErrores = `<ul>${errores.map(e => `<li>${e}</li>`).join('')}</ul>`;
            ErrorModal(listaErrores);
        }

        actualizarLista();
    }


    function formatearBytes(bytes){
    const mb = bytes / (1024*1024);
    return (mb >= 1) ? `${mb.toFixed(2)} MB` : `${(bytes/1024).toFixed(0)} KB`;
    }

    function actualizarLista() {
    fileList.innerHTML = "";
    fileListContainer.style.display = selectedFiles.length ? 'block' : 'none';

    selectedFiles.forEach((file, index) => {
        const li = document.createElement("li");
        li.className = "fl-item";
        li.innerHTML = `
        <span class="fl-pill">
            <span class="fl-favicon"></span>
            <span class="fl-text" title="${file.name}">${file.name}</span>
        </span>
        <button class="fl-remove" aria-label="Eliminar archivo" onclick="eliminarArchivo(${index})">
            <i class="bi bi-trash-fill"></i>
        </button>
        `;
        fileList.appendChild(li);
    });

    const totalBytes = selectedFiles.reduce((sum, f) => sum + f.size, 0);
    const infoDiv = document.getElementById("file-size-info");
    infoDiv.style.display = selectedFiles.length ? 'block' : 'none';
    const mb = totalBytes / (1024 * 1024);
    infoDiv.textContent = `Total seleccionado: ${mb >= 1 ? mb.toFixed(2)+' MB' : Math.round(totalBytes/1024)+' KB'} / 10 MB`;
    }


    function eliminarArchivo(index) {
        selectedFiles.splice(index, 1);
        actualizarLista();
    }

    function obtenerFormData() {
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append("adjuntos[]", file);
        });
        return formData;
    }

    async function limpiarAdjuntosSesion() {
        try {
            await fetch('Reporte/LimpiarAdjuntos', { method: 'POST' });
        } catch (e) {
            // no rompas el flujo del usuario por esto
            console.warn('No se pudo limpiar adjuntos en sesión:', e);
        }
    }


    /* =========================
   SECCIÓN: URLs
   ========================= */

    const urlInput      = document.getElementById('urlInput');
    const btnAgregarURL = document.getElementById('btnAgregarURL');
    const urlsListWrap  = document.getElementById('urlsListWrap');
    const urlsList      = document.getElementById('urlsList');
    const urlHelp       = document.getElementById('urlHelp');
    const selIdioma     = document.getElementById('selectorIdioma');

    const MAX_URLS = 30;
    let rutasURL = [];

    /* FUNCION CONDICIONAL PARA TRADUCIR EL TEXTO */
    function dic() {
    const lang = selIdioma?.value || 'es';
    return textos[lang] || textos.es;
    }

    // Valida/normaliza
    function normalizarURL(raw) {
    if (!raw) return null;
    let v = raw.trim();
    if (!v) return null;

    if (/\s/.test(v)) return null;

    // Con protocolo http/https
    if (/^https?:\/\//i.test(v)) {
        try {
        const u = new URL(v);
        if (!/^https?:$/i.test(u.protocol)) return null;
        return u.href;
        } catch { return null; }
    }

    // Dominio directo simple
    const simpleOk = v.includes('.') && !v.startsWith('.') && v.length >= 4;
    if (!simpleOk) return null;

    const dominioRe = /^([a-z0-9-]+\.)+[a-z]{2,}(:\d+)?(\/\S*)?$/i;
    return dominioRe.test(v) ? v : null;
    }

    function renderURLs() {
    urlsList.innerHTML = '';
    const D = dic();

    rutasURL.forEach((u, idx) => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerHTML = `
        <span class="url-pill">
            <span class="url-favicon"></span>
            <span class="url-text" title="${u}">${u}</span>
        </span>
        <button type="button" class="url-remove" aria-label="${D.ariaRemoveUrl}" data-index="${idx}">
            <i class="bi bi-trash-fill"></i>
        </button>
        `;
        urlsList.appendChild(li);
    });

    urlsListWrap.style.display = rutasURL.length ? '' : 'none';
    actualizarEstadoURLs();
    }

    function actualizarEstadoURLs() {
    const D = dic();

    if (urlHelp) {
        urlHelp.textContent = (D.urlHelp || '')
        .replace('{added}', rutasURL.length)
        .replace('{max}', MAX_URLS);
    }

    const alLimite = rutasURL.length >= MAX_URLS;
    urlInput.disabled = alLimite;
    btnAgregarURL.disabled = alLimite;

    urlInput.placeholder = alLimite
        ? (D.urlPlaceholderLimit || '').replace('{max}', MAX_URLS)
        : (D.placeholderUrl || textos.es.placeholderUrl);
    }

    function agregarURLIndividual() {
    const D = dic();

    if (rutasURL.length >= MAX_URLS) {
        ErrorModal((D.urlErrorMax || '').replace('{max}', MAX_URLS));
        return;
    }

    const raw = urlInput.value;
    if (/\s/.test(raw)) {
        ErrorModal(D.urlErrorSpaces || '');
        return;
    }

    const norm = normalizarURL(urlInput.value);
    if (!norm) {
        ErrorModal(D.urlErrorInvalid || '');
        return;
    }

    // Evita duplicados (case-insensitive)
    const ya = rutasURL.some(x => x.toLowerCase() === norm.toLowerCase());
    if (ya) {
        ErrorModal(D.urlErrorDuplicate || '');
        return;
    }

    rutasURL.push(norm);
    urlInput.value = '';
    renderURLs();
    urlInput.focus();
    }

    urlsList.addEventListener('click', (ev) => {
    const btn = ev.target.closest('.url-remove');
    if (!btn) return;
    const i = parseInt(btn.dataset.index, 10);
    if (!Number.isNaN(i)) {
        rutasURL.splice(i, 1);
        renderURLs();
    }
    });

    btnAgregarURL.addEventListener('click', agregarURLIndividual);
    urlInput.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter') {
        ev.preventDefault();
        agregarURLIndividual();
    }
    });

    function obtenerCadenaURLs() {
        return rutasURL.join(',');
    }

    function resetearURLs() {
        rutasURL = [];
        renderURLs();
    }

    /* =========================
   (3) INICIALIZACIÓN
   ========================= */
    document.addEventListener('DOMContentLoaded', () => {
        const D = dic();
        if (document.getElementById('URLPermitidas')) {
            document.getElementById('URLPermitidas').textContent = D.lblUrl || '';
        }
        if (btnAgregarURL) btnAgregarURL.textContent = D.btnUrl || '';
        if (urlInput) urlInput.placeholder = D.placeholderUrl || textos.es.placeholderUrl;

        actualizarEstadoURLs();

        selIdioma?.addEventListener('change', () => {
            const Dx = dic();
            if (document.getElementById('URLPermitidas')) {
            document.getElementById('URLPermitidas').textContent = Dx.lblUrl || '';
            }
            if (btnAgregarURL) btnAgregarURL.textContent = Dx.btnUrl || '';
            if (urlInput) urlInput.placeholder = Dx.placeholderUrl || textos.es.placeholderUrl;

            actualizarEstadoURLs();
            renderURLs();
        });
    });
    
    let captchaValor = "";

    function generarCaptcha() {
        const canvas = document.getElementById('captchaCanvas');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
        let texto = "";
        for (let i = 0; i < 6; i++) texto += chars.charAt(Math.floor(Math.random() * chars.length));
        captchaValor = texto;

        ctx.fillStyle = "#f6f6f6";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < 5; i++) {
            ctx.strokeStyle = "rgba(120,120,120,0.3)";
            ctx.beginPath();
            ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
            ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
            ctx.stroke();
        }

        ctx.font = "28px Arial";
        ctx.fillStyle = "#222";
        for (let i = 0; i < texto.length; i++) {
            let x = 20 + i * 20;
            let y = 35 + Math.random() * 10;
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate((Math.random() - 0.5) * 0.4);
            ctx.fillText(texto[i], 0, 0);
            ctx.restore();
        }
    }
    generarCaptcha();

    function soloLetras(e) {
        const valor = e.target.value;
        // Permite letras mayúsculas/minúsculas, acentos y espacios
        e.target.value = valor.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
    }

    document.getElementById('reporteCibernetico').addEventListener('submit', async function (e) {
        e.preventDefault();
        let valid = true;
        document.querySelectorAll('.error').forEach(e => e.remove());

        /* SECCION ERRORES */
        function showError(input, msg) {
            let error = document.createElement('div');
            error.className = 'error';
            error.style.color = 'red';
            error.textContent = msg;
            input.parentNode.appendChild(error);
            valid = false;
        }

        let obligatorioError = "Campo obligatorio.";
        let obligatorioGlobal = "Faltan campos obligatorios"; 
        let telefonoError ="Teléfono de 10 dígitos.";
        let curpError = "CURP no válida.";
        let conoceCurpError = "Selecciona si conoce su CURP o no.";
        let reporteAnonimoError = "Selecciona si es reporte anónimo o no.";
        let personaFisicaError = "Selecciona si es persona física o no.";
        let tePasoError = "Selecciona si te pasó a ti o no";
        let esExtranjeroError = "Selecciona si eres extranjero o no";
        let correoError = "Correo invalido.";
        let cpInvalid = "Código postal inválido.";
        let sucedioError = "Seleccione por el que sucedió.";
        let reporteError = "Describa el reporte.";
        let ingreseCaptchaError = "Ingresa el captcha.";
        let incorrectoCaptchaError = "Captcha incorrecto.";
        let idiomaText = document.getElementById('selectorIdioma');
        if (idiomaText.value.trim() == 'en') {
            obligatorioError = "required field.";
            obligatorioGlobal = "Required fields are missing";
            telefonoError = "10-digit phone number.";
            curpError = "Invalid CURP.";
            conoceCurpError = "Select whether you know your CURP.";
            reporteAnonimoError = "Select whether this is an anonymous report.";
            personaFisicaError = "Select whether this is a natural person.";
            tePasoError = "Select if it happened to you.";
            esExtranjeroError = "Select if you are a foreigner.";
            correoError = "invalid Email.";
            cpInvalid = "Invalid Postal Code.";
            sucedioError = "Select how it happened.";
            reporteError = "Describe the report.";
            ingreseCaptchaError = "Enter the captcha.";
            incorrectoCaptchaError = "Incorrect captcha.";
        }

        /* FORMULARIO */
        const anonimos = document.querySelectorAll('input[name="anonimo"]');
        const anonimo = document.querySelector('input[name="anonimo"]:checked');
        const fisica = document.querySelectorAll('input[name="fisica"]');
        const esFisica = document.querySelector('input[name="fisica"]:checked');
        const tePasoM = document.querySelectorAll('input[name="afectado"]');
        const estePasoM = document.querySelector('input[name="afectado"]:checked')
        const ExtranjeroM = document.querySelectorAll('input[name="extranjero"]');
        const esExtranjeroM = document.querySelector('input[name="extranjero"]:checked')
        const tePaso = document.querySelector('input[name="afectado"]:checked');
        const esExtranjero = document.querySelector('input[name="extranjero"]:checked');
        const errorGlobal = document.getElementById('enviarReporte');

        let missingRequired = false;

        if (!anonimo) {
            showError(anonimos[0].parentNode, reporteAnonimoError);
            missingRequired = true;

            } else if (anonimo.value === 'no') {
            if (!esFisica) {
                showError(fisica[0].parentNode, personaFisicaError);
                missingRequired = true;
            }

            if (esFisica && esFisica.value === 'si') {
                if (!estePasoM) {
                showError(tePasoM[0].parentNode, tePasoError);
                missingRequired = true;
                }
                if (!esExtranjeroM) {
                showError(ExtranjeroM[0].parentNode, esExtranjeroError);
                missingRequired = true;
                }

                // --- Validaciones de persona física ---
                const nombre = document.getElementById('nombre');
                if (!nombre.value.trim()) showError(nombre, obligatorioError), (missingRequired = true);

                const ap1 = document.getElementById('apellidoPaterno');
                if (!ap1.value.trim()) showError(ap1, obligatorioError), (missingRequired = true);

                const ap2 = document.getElementById('apellidoMaterno');
                if (!ap2.value.trim()) showError(ap2, obligatorioError);

                const tel = document.getElementById('telefono');
                if (!/^\d{10}$/.test(tel.value.trim())) showError(tel, telefonoError), (missingRequired = true);

                const FechaNa = document.getElementById('fechaNacimiento');
                if (!FechaNa.value.trim()) {
                showError(FechaNa, obligatorioError);
                missingRequired = true;
                } else {
                const fecha = new Date(FechaNa.value);
                const hoy = new Date(); hoy.setHours(0,0,0,0);
                const fechaMin = new Date();
                fechaMin.setFullYear(hoy.getFullYear() - 120);
                if (isNaN(fecha.getTime())) {
                    showError(FechaNa, idiomaText.value.trim() == 'en' ? 'Invalid date.' : 'Fecha no válida.');
                } else if (fecha > hoy) {
                    showError(FechaNa, idiomaText.value.trim() == 'en' ? 'Birth date cannot be in the future.' : 'La fecha de nacimiento no puede ser futura.');
                } else if(fecha < fechaMin){
                    showError(FechaNa, idiomaText.value.trim() == 'en' ? 'Must be 90 years old or younger.' : 'Debe tener 90 años o menos.');
                } else {
                    // >18 y ≤90
                    let edad = hoy.getFullYear() - fecha.getFullYear();
                    const m = hoy.getMonth() - fecha.getMonth();
                    if (m < 0 || (m === 0 && hoy.getDate() < fecha.getDate())) edad--;
                    if (edad <= 18) {
                    showError(FechaNa, idiomaText.value.trim() == 'en' ? 'Must be older than 18 years.' : 'Debe ser mayor de 18 años.');
                    } else if (edad > 90) {
                    showError(FechaNa, idiomaText.value.trim() == 'en' ? 'Must be 90 years old or younger.' : 'Debe tener 90 años o menos.');
                    }
                }
                }

                if (esExtranjero && esExtranjero.value === 'no') {
                const curp = document.getElementById('curp');
                const valorCurp = curp.value.trim();
                if (valorCurp !== "" && !/^[A-Z]{4}[0-9]{6}[A-Z]{6}[0-9]{2}$/i.test(valorCurp)) {
                    showError(curp, curpError);
                }
                }

                if (tePaso && tePaso.value === 'no') {
                const nombreReporta = document.getElementById('nombreReporta');
                if (!nombreReporta.value.trim()) showError(nombreReporta, obligatorioError), (missingRequired = true);

                const apellidoPaternoReporta = document.getElementById('apellidoPaternoReporta');
                if (!apellidoPaternoReporta.value.trim()) showError(apellidoPaternoReporta, obligatorioError), (missingRequired = true);

                const apellidoMaternoReporta = document.getElementById('apellidoMaternoReporta');
                if (!apellidoMaternoReporta.value.trim()) showError(apellidoMaternoReporta, obligatorioError), (missingRequired = true);
                }

            } else if (esFisica && esFisica.value === 'no') {
                const moral = document.getElementById('moral');
                if (!moral.value.trim()) showError(moral, obligatorioError), (missingRequired = true);

                const telMoral = document.getElementById('telMoral');
                if (!telMoral.value.trim()) showError(telMoral, obligatorioError), (missingRequired = true);
            }
        }

        function isValidEmailStrict(v){
            v = (v ?? "").toString().trim();

            if (v.length < 6 || v.length > 254) return false;

            if (/[\'\"\s<>\(\);]/.test(v)) return false;

            return /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$/.test(v);
        }

        const correo = document.getElementById('correo');
            if (!isValidEmailStrict(correo.value)) {
            showError(correo, correoError);
            missingRequired = true;
        }

        const cp = document.getElementById('codigoPostal');
        if (cp.value.trim() && !/^\d{5}$/.test(cp.value.trim())) showError(cp, cpInvalid); 

        const desc = document.getElementById('medio');
        if (!desc.value.trim()) showError(desc, sucedioError), (missingRequired = true);

        const estado = document.getElementById('estado');
        if (!estado.value.trim()) showError(estado, obligatorioError), (missingRequired = true);

        const municipio = document.getElementById('municipio');
        if (!municipio.value.trim()) showError(municipio, obligatorioError), (missingRequired = true);

        const fechaHechos = document.getElementById('fechaHechos');
        const fechaMinHechos = new Date(1990, 0, 1);
        if (!fechaHechos.value.trim()) {
            showError(fechaHechos, obligatorioError);
            missingRequired = true;
        } else {
            const fecha = new Date(fechaHechos.value);
            const hoy = new Date(); hoy.setHours(0,0,0,0);
            if (isNaN(fecha.getTime())) {
                showError(fechaHechos, idiomaText.value.trim() == 'en' ? 'Invalid date.' : 'Fecha no válida.');
            } else if (fecha > hoy) {
                showError(fechaHechos, idiomaText.value.trim() == 'en' ? 'Date cannot be in the future.' : 'La fecha de los hechos no puede ser futura.');
            } else if(fecha < fechaMinHechos) {
                showError(fechaHechos, idiomaText.value.trim() == 'en' ? 'Date must not be earlier than 1990' : 'La fecha de los hechos no puede ser menor a 1990.');
            }
        }

        function isValidFreeTextStrict(v, maxLen = 3000){
            v = (v ?? "").toString();

            if (!v.trim()) return false;
            if (v.length > maxLen) return false;

            if (/[\'\"<>;\(\)]/.test(v)) return false;

            // bloquea chars de control invisibles
            if (/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/.test(v)) return false;

            return true;
        }

        const comoOcurrio = document.getElementById('comoOcurrio');
            if (!isValidFreeTextStrict(comoOcurrio.value, 3000)) {
            showError(comoOcurrio, idiomaText.value.trim() === 'en'
                ? 'Invalid characters or text too long.'
                : 'Texto inválido: evita caracteres especiales o texto demasiado largo.'
            );
            missingRequired = true;
        }

        const captchaInput = document.getElementById('captchaInput');
        const entrada = captchaInput.value.trim();
        const captchaErrorDiv = document.getElementById('captchaError');

        if (entrada === "") {
            captchaErrorDiv.innerHTML = ingreseCaptchaError;
            captchaErrorDiv.style.display = "block";
            valid = false;
        } else if (entrada !== captchaValor) {
            captchaErrorDiv.innerHTML = incorrectoCaptchaError;
            captchaErrorDiv.style.display = "block";
            generarCaptcha();
            valid = false;
        } else {
            captchaErrorDiv.style.display = "none";
        }

        if (missingRequired) showError(errorGlobal, obligatorioGlobal);

        if (!valid) return;

        const formData = new FormData();
        let archivosSubidos = [];

        if (selectedFiles.length > 0) {
            for (let i = 0; i < selectedFiles.length; i++) {
                formData.append('adjuntos[]', selectedFiles[i]);
            }

            try {
                const respArchivos = await fetch('Reporte/SubirAdjuntos', {
                    method: 'POST',
                    body: formData
                });

                const resArchivos = await respArchivos.json();

                if (!resArchivos.status) {
                    ErrorModal("Error al subir archivos: " + (resArchivos.message || ''));
                    await limpiarAdjuntosSesion();
                    return;
                }

                archivosSubidos = resArchivos.archivos;

            } catch (error) {
                ErrorModal("Error en subida de archivos");
                console.error("Error en subida de archivos:", error);
                await limpiarAdjuntosSesion();
                return;
            }
        }

        // Continúa con el resto de la lógica con o sin archivos
        const langRaw = document.getElementById('selectorIdioma')?.value || 'es';
        const lang = (langRaw === 'en') ? 'en' : 'es'; 

        const nombresArchivos = selectedFiles.map(a => a.name).join(',');
        const rutasURLCadena = obtenerCadenaURLs();

        const curpInputRef = document.getElementById('curp');
        const curpDivRef   = document.getElementById('curpDiv');

        const curpValue = (curpInputRef && !curpInputRef.disabled && !curpDivRef?.classList.contains('hidden'))
            ? (curpInputRef.value.trim() || null)
            : null;

        const datosReporte = {
            esAnonimo: anonimo?.value === 'si',
            esFisica: esFisica?.value === 'si',
            tePaso: tePaso?.value === 'si',
            esExtranjero: esExtranjero?.value === 'si',      
            idEstado: parseInt(document.getElementById('estado').value),
            idMunicipio: parseInt(document.getElementById('municipio').value),
            colonia: document.getElementById('colonia')?.value || null,
            cp: document.getElementById('codigoPostal')?.value || null,
            comoOcurrio: document.getElementById('comoOcurrio')?.value || null,
            fechaHechos: document.getElementById('fechaHechos')?.value || null,
            idSucedio: document.getElementById('medio')?.value || null,
            esMenor: document.querySelector('input[name="esMenor"]:checked')?.value === 'si',
            nombreReporta: document.getElementById('nombreReporta')?.value || null,
            apellidoPaternoReporta: document.getElementById('apellidoPaternoReporta')?.value || null,
            apellidoMaternoReporta: document.getElementById('apellidoMaternoReporta')?.value || null,
            PersonaMoral: document.getElementById('moral')?.value || null,
            telefonoMoral: document.getElementById('telMoral')?.value || null,
            curp: curpValue,
            nombre: document.getElementById('nombre')?.value || null,
            aPaterno: document.getElementById('apellidoPaterno')?.value || null,
            aMaterno: document.getElementById('apellidoMaterno')?.value || null,
            fechaNacimiento: document.getElementById('fechaNacimiento')?.value || null,
            edad: parseInt(document.getElementById('edad')?.value || 0),
            telefono: document.getElementById('telefono')?.value || null,
            email: document.getElementById('correo')?.value || null,
            nombreArchivo: nombresArchivos,     // ← se mantiene por compatibilidad / fallback
            rutasURL : rutasURLCadena,
            idioma: lang
        };

        const btnEnviar = document.querySelector('#enviarReporte');

        try {
            showLoader();
            btnEnviar?.setAttribute('disabled','disabled');

            const response = await fetch('Reporte/SendReporte', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosReporte)
            });

            const res = await response.json();

            if (res.status) {
                const D = dic();

                const folio  = res.response?.folio || "—";
                const estadoArr = res.response?.estado
                    ? res.response.estado.split(",").map(e => e.replace(/["()]/g, '').trim())
                    : [];
                let reporta = (res.response?.reporta?.trim())
                    ? res.response.reporta
                    : (D.anonimoValue || 'anónimo');             

                if (/^anonim/i.test(reporta)) reporta = D.anonimoValue || reporta; 

                const $title = document.getElementById('ModalTitle');
                if ($title) $title.innerHTML = D.modalSuccessTitle || 'REGISTRO<br>CORRECTO';

                const $btnOK = document.getElementById('btnAceptarTrue');
                if ($btnOK) $btnOK.textContent = D.modalAccept || 'Aceptar';                 

                const folioHTML = `
                    ${D.lblFolio || 'Folio:'} ${folio}<br>
                    ${D.lblEntidad || 'Entidad:'} ${estadoArr[1] ?? '—'}<br>
                    ${D.lblReporta || 'Reporta:'} ${reporta}
                `;

                document.getElementById('modalFolio').innerHTML = folioHTML;

                const modal = new bootstrap.Modal(document.getElementById('successModal'));
                modal.show();
                document.getElementById('reporteCibernetico').reset();
                generarCaptcha();

                selectedFiles = [];
                actualizarLista();
                resetearURLs();

                // ✅ Limpia inventario en backend, ya no lo necesitamos
                await limpiarAdjuntosSesion();

            } else {
                ErrorModal("Error al enviar reporte.");
                // (opcional) también puedes limpiar si quieres empezar desde cero
                await limpiarAdjuntosSesion();
            }
        } catch (error) {
            console.error("Error en el envío:", error);
            ErrorModal("Ocurrió un error al enviar el reporte.");
            // (opcional) limpiar inventario ante fallo
            await limpiarAdjuntosSesion();
        } finally {
            hideLoader();
            btnEnviar?.removeAttribute('disabled');
        }
    });


     // Cambio de Idioma
    const textos = {
      es: {
        idiomaError:"Campo obligatorio",
        spnHead:"Todos los datos marcados con (*) son obligatorios.",
        lblanonimo: "¿Le gustaría presentar su reporte de forma anónima?*",
        lblsiAnonimo: "Sí",
        lblsiExtranjero: "Sí",
        lblsiCurp: "Sí",
        lblsiMenor: "Sí",
        lblsiAfectado: "Sí",
        lblsiPersonaFisica: "Sí",
        lblPersonaFisica:"¿Eres persona física?",
        lblex: "¿Es usted extranjero?",
        lblno: "Nombre*:",
        lblpa: "Apellido paterno*:",
        lblma: "Apellido materno*:",
        smllMes: "(Donde sucedieron los hechos)",
        smllMes2:"(Descripción de los hechos)",
        mgeLink:"Consultar CURP 🔗",
        lbltel: "Teléfono*:",
        lblcurp: "¿Conoces tu CURP?:",
        lbled: "Edad:",
        lblfena: "Fecha de nacimiento*:",
        lblcorreo: "Correo*:",
        lblmenor: "Es menor de edad:",
        lblcp: "Código postal:",
        lbledo: "Estado*:",
        lblmun: "Municipio*:",
        lblcol: "Colonia:",
        lblpaso: "¿Esto te pasó a ti?",
        lblemp: "Institución/Empresa:",
        lblocurrio: "¿Cómo ocurrió?*:",
        lblhechos: "Fecha de los hechos*:",
        lblmedio:"¿A través de qué medio sucedió?* (red social, páginas web, aplicaciones, correos, etc.)",
        optEstado:"Seleccione:",
        optMunicipio:"Seleccione:",
        subirArchivo: "SUBIR ARCHIVO",
        arrastrar: "Arrástralo aquí",
        captchaInput:"Escriba el captcha",
        archivoPermitido: "Se permiten archivos: (.jpg, .jpeg, .png, .pdf, .docx, .mp3, .aac, .opus, .ogg, .mp4)",
        enviarReporte: "ENVIAR REPORTE",
        h5rc: "REGISTRO DE REPORTES CIBERNÉTICOS",
        divdp: "Datos persona afectada",
        divdc: "Describa aquí su reporte de Ciberseguridad",
        divReporta:"Datos Persona que Reporta",
        contador:"3000 caracteres restantes",
        lblnoReporta:"Nombre*:",
        lblpaReporta:"Apellido paterno*:",
        lblmaReporta:"Apellido materno*:",
        divMoral:"Datos Persona Moral",
        lblMoral:"Nombre de la Empresa / Institución*:",
        lbltelMoral:"Teléfono*:",
        placeholderTel:"10 dígitos",
        /* URL */
        lblUrl: "Agregar la(s) URL's donde ocurrió",
        btnUrl: "SUBIR URL",
        placeholderUrl: "www.ejemplo.com/ruta",
        urlHelp: "Ingresa una URL válida. Agregadas: {added}/{max}.",
        urlPlaceholderLimit: "Límite de {max} URLs alcanzado",
        ariaRemoveUrl: "Eliminar URL",
        urlErrorMax: "Se alcanzó el máximo de {max} URL(s).",
        urlErrorSpaces: "La URL no puede contener espacios.",
        urlErrorInvalid:"La URL no es válida. Ejemplos válidos: https://sitio.com, http://dominio.mx/recurso, www.ejemplo.com/ruta",
        urlErrorDuplicate: "Esa URL ya fue agregada.",
        /* LOADER */
        loaderRegistering: "Registrando reporte…",
        /* MODAL */
        modalSuccessTitle: "REGISTRO<br>CORRECTO",
        modalAccept: "Aceptar",
        lblFolio: "Folio:",
        lblEntidad: "Entidad:",
        lblReporta: "Reporta:",
        anonimoValue: "anónimo",
        fileExtNotAllowed: 'El archivo "{name}" no tiene un formato permitido.',
        fileTotalLimitExceeded: 'El archivo "{name}" excede el límite total de {limit} MB.',
      },
      en: {
        idiomaError:"Required field",
        spnHead:"All fields marked with (*) are required.",
        lblanonimo: "Would you like to submit your report anonymously?*",
        lblsiAnonimo: "Yes",
        lblsiExtranjero: "Yes",
        lblsiCurp: "Yes",
        lblsiMenor: "Yes",
        lblsiAfectado: "Yes",
        lblsiPersonaFisica: "Yes",
        lblPersonaFisica:"Are you a natural person?",
        lblex: "Are you foreign?",
        lblno: "Name*:",
        lblpa: "Paternal last name*:",
        lblma: "Maternal last name*:",
        lbltel: "Phone*:",
        lblcurp: "Do you know your CURP?:",
        lbled: "Age:",
        lblfena: "Date of birth*:",
        lblcorreo: "Email*:",
        lblmenor: "Is the affected person a minor?:",
        lblcp: "Postal code:",
        lbledo: "State*:",
        lblmun: "Country*:",
        lblcol: "Neighborhood:",
        smllMes: "(Location of the incident)",
        smllMes2: "(Incident description)",
        mgeLink: "Search CURP 🔗",
        lblpaso: "Did this happen to you?",
        lblocurrio: "How did it happen?*:",
        lblhechos: "Date of incident*:",
        lblmedio:"Through what medium did it happen?* (social network, websites, appication,emails)",
        optEstado:"SELECT:",
        optMunicipio:"SELECT:",
        subirArchivo: "BROWSE FILES",
        arrastrar: "Drag&Drop files here",
        captchaInput:"Enter captcha text",
        archivoPermitido: "Allowed files: (.jpg, .jpeg, .png, .pdf, .docx, .mp3, .aac, .opus, .ogg, .mp4)",
        enviarReporte: "SEND REPORT",
        h5rc: "CYBER INCIDENT REPORTS",
        divdp: "Personal details",
        divdc: "Describe your cybersecurity report here",
        divReporta:"Reporter Information",
        contador:"3000 characters remaining",
        lblnoReporta:"Name*:",
        lblpaReporta:"Paternal last name*:",
        lblmaReporta:"Maternal last name*:",
        divMoral:"Organization Information",
        lblMoral:"Company / Institution Name*:",
        lbltelMoral:"Phone*:",
        placeholderTel:"10 digits",
        /* URL */
        lblUrl: "Add the URL(s) where it happened",
        btnUrl: "ADD URL",
        placeholderUrl: "www.example.com/path",            
        urlHelp: "Enter a valid URL. Added: {added}/{max}.",
        urlPlaceholderLimit: "Limit of {max} URLs reached",
        ariaRemoveUrl: "Remove URL",
        urlErrorMax: "Maximum of {max} URL(s) reached.",
        urlErrorSpaces: "The URL cannot contain spaces.",
        urlErrorInvalid: "The URL is not valid. Valid examples: https://site.com, http://domain.com/resource, www.example.com/path",
        urlErrorDuplicate: "This URL has already been added.",
        /* LOADER */
        loaderRegistering: "Submitting report…",
        /* MODAL: */
        modalSuccessTitle: "REGISTRATION<br>SUCCESSFUL",
        modalAccept: "Accept",
        lblFolio: "Receipt ID:",
        lblEntidad: "State:",
        lblReporta: "Reporter:",
        anonimoValue: "anonymous",
        fileExtNotAllowed: 'The file "{name}" has an unsupported format.',
        fileTotalLimitExceeded: 'The file "{name}" exceeds the total limit of {limit} MB.',
      },
    };

    document.getElementById('selectorIdioma').addEventListener('change', function() {
        document.querySelectorAll('.error').forEach(e => e.remove());

        const lang = this.value;
        document.getElementById('spnHead').textContent = textos[lang].spnHead;
        document.getElementById('lblanonimo').textContent = textos[lang].lblanonimo;
        document.getElementById('lblex').textContent = textos[lang].lblex;
        document.getElementById('lblno').textContent = textos[lang].lblno;
        document.getElementById('lblpa').textContent = textos[lang].lblpa;
        document.getElementById('lblma').textContent = textos[lang].lblma;
        document.getElementById('lbltel').textContent = textos[lang].lbltel;
        document.getElementById('lblcurp').textContent = textos[lang].lblcurp;
        document.getElementById('lbled').textContent = textos[lang].lbled;
        document.getElementById('lblfena').textContent = textos[lang].lblfena;
        document.getElementById('lblcorreo').textContent = textos[lang].lblcorreo;
        document.getElementById('lblmenor').textContent = textos[lang].lblmenor;
        document.getElementById('lblcp').textContent = textos[lang].lblcp;
        document.getElementById('lbledo').textContent = textos[lang].lbledo;
        document.getElementById('lblmun').textContent = textos[lang].lblmun;
        document.getElementById('lblcol').textContent = textos[lang].lblcol;
        document.getElementById('smallMessage1').textContent = textos[lang].smllMes;
        document.getElementById('smallMessage2').textContent = textos[lang].smllMes;
        document.getElementById('smallMessage3').textContent = textos[lang].smllMes;
        document.getElementById('smallMessage4').textContent = textos[lang].smllMes;
        document.getElementById('smallMessage5').textContent = textos[lang].smllMes;
        document.getElementById('smallMessage6').textContent = textos[lang].smllMes2;
        document.getElementById('messageLink').textContent = textos[lang].mgeLink;
        document.getElementById('lblpaso').textContent = textos[lang].lblpaso;
        document.getElementById('lblocurrio').textContent = textos[lang].lblocurrio;
        document.getElementById('lblhechos').textContent = textos[lang].lblhechos;
        document.getElementById('lblmedio').textContent = textos[lang].lblmedio;
        document.getElementById('optEstado').textContent = textos[lang].optEstado;
        document.getElementById('optmedio').textContent = textos[lang].optEstado;
        document.getElementById('optMunicipio').textContent = textos[lang].optMunicipio;
        document.getElementById('subirArchivo').textContent = textos[lang].subirArchivo;
        document.getElementById('arrastrar').textContent = textos[lang].arrastrar;
        document.getElementById('captchaInput').placeholder = textos[lang].captchaInput;
        document.getElementById('archivoPermitido').textContent = textos[lang].archivoPermitido;
        document.getElementById('enviarReporte').textContent = textos[lang].enviarReporte;
        document.getElementById('h5rc').textContent = textos[lang].h5rc;
        document.getElementById('divdp').textContent = textos[lang].divdp;
        document.getElementById('divdc').textContent = textos[lang].divdc;
        document.getElementById('contador').textContent = textos[lang].contador;
        document.getElementById('lblsiAnonimo').textContent = textos[lang].lblsiAnonimo;        
        document.getElementById('lblsiExtranjero').textContent = textos[lang].lblsiExtranjero; 
        document.getElementById('lblsiMenor').textContent = textos[lang].lblsiMenor; 
        document.getElementById('lblsiAfectado').textContent = textos[lang].lblsiAfectado; 
        document.getElementById('lblsiPersonaFisica').textContent = textos[lang].lblsiPersonaFisica;
        document.getElementById('divReporta').textContent = textos[lang].divReporta;
        document.getElementById('lblPersonaFisica').textContent = textos[lang].lblPersonaFisica;
        document.getElementById('lblnoReporta').textContent = textos[lang].lblnoReporta;
        document.getElementById('lblpaReporta').textContent = textos[lang].lblpaReporta;
        document.getElementById('lblmaReporta').textContent = textos[lang].lblmaReporta;
        document.getElementById('divMoral').textContent = textos[lang].divMoral;
        document.getElementById('lblMoral').textContent = textos[lang].lblMoral;
        document.getElementById('lbltelMoral').textContent = textos[lang].lbltelMoral;
        document.getElementById('telefono').setAttribute('placeholder', textos[lang].placeholderTel);
        document.getElementById('telMoral').setAttribute('placeholder', textos[lang].placeholderTel);

        idiomaError = textos[lang].idiomaError;      
    });  

    document.addEventListener('DOMContentLoaded', function () {
        var myModal = new bootstrap.Modal(document.getElementById('autoModal'), {
            keyboard: false,
            backdrop: 'static'
        });
        myModal.show();
    });

    document.getElementById('btnAceptarTrue').addEventListener('click', function () {
        location.reload();
    });

    //CATALOGOS
    let estadosCargados = false;
    let ComoOcurrioCargados = false;

    async function GetSelectEstado() {
        if (estadosCargados) return;

        try {
            const response = await fetch('Reporte/GetEstados')
            const res = await response.json();

            if (res.status) {
                const select = document.getElementById('estado');
                const lang = document.getElementById('selectorIdioma').value || 'es';
                select.innerHTML = `<option id="optEstado" value="" disabled selected hidden>${textos[lang].optEstado}</option>`;


                res.entidades.forEach(estado => {
                    const option = document.createElement('option');
                    option.value = estado.id;
                    option.textContent = estado.estado;
                    select.appendChild(option);
                });

                estadosCargados = true;
            } else {
                console.warn('No se pudo obtener la lista de estados');
            }
        } catch (error) {
            console.error('Error al obtener estados:', error);
        }
    }

    async function GetSelectMedio() {
        if (ComoOcurrioCargados) return;

        try {
            const response = await fetch('Reporte/GetMedio')
            const res = await response.json();

            if (res.status) {
                const select = document.getElementById('medio');
                const lang = document.getElementById('selectorIdioma').value || 'es';
                select.innerHTML = `<option id="optEstado" value="" disabled selected hidden>${textos[lang].optEstado}</option>`;

                res.medios.forEach(medio => {
                    const option = document.createElement('option');
                    option.value = medio.id;
                    option.textContent = medio.medio;
                    select.appendChild(option);
                });

                ComoOcurrioCargados = true;
            } else {
                console.warn('No se pudo obtener la lista de estados');
            }
        } catch (error) {
            console.error('Error al obtener estados:', error);
        }
    }

    async function GetSelectMunicipio(id) {
    if (!id) return;

        try {
            const response = await fetch('Reporte/GetMunicipios', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ idEntidad: id })
            });

            const res = await response.json();

            const municipioSelect = document.getElementById('municipio');
            /* municipioSelect.innerHTML = '<option value="" disabled selected hidden>Seleccione:</option>'; */
            const lang = document.getElementById('selectorIdioma').value || 'es';
            municipioSelect.innerHTML = `<option id="optMunicipio" value="" disabled selected hidden>${textos[lang].optMunicipio}</option>`;

            if (res.status && res.municipios.length > 0) {
                res.municipios.forEach(municipio => {
                    const option = document.createElement('option');
                    option.value = municipio.id_municipio;
                    option.textContent = municipio.municipio;
                    municipioSelect.appendChild(option);
                });

                municipioSelect.disabled = false;
            } else {
                municipioSelect.innerHTML = '<option disabled>No hay municipios</option>';
                municipioSelect.disabled = true;
            }
        } catch (error) {
            console.error('Error al obtener municipios:', error);
            document.getElementById('municipio').disabled = true;
        }
    }

    function OnEstadoChange(idEstado) {
        const municipioSelect = document.getElementById('municipio');

        municipioSelect.innerHTML = '<option value="" disabled selected hidden>Cargando...</option>';
        municipioSelect.disabled = true;

        GetSelectMunicipio(idEstado);
    }