<!DOCTYPE html>
<html lang="es">
<?php
// Cargar autoload y variables de entorno si no están cargadas
if (!class_exists('Dotenv\Dotenv')) {
    require_once __DIR__ . '/../../../vendor/autoload.php';
}

if (!isset($_ENV['CONFIG_JS_PATH']) || empty($_ENV['CONFIG_JS_PATH'])) {
    try {
        $dotenv = \Dotenv\Dotenv::createImmutable(__DIR__ . '/../../../');
        $dotenv->load();
    } catch (\Exception $e) {
        // Ya está cargado
    }
}

$configJsPath = isset($_ENV['CONFIG_JS_PATH']) && !empty($_ENV['CONFIG_JS_PATH']) 
    ? $_ENV['CONFIG_JS_PATH'] 
    : '/proyectos_alternativos/frontend/config.js';
?>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>El Agente Bit - Plataforma Unificada</title>
  <style> 
    :root {
      --bg: #0a0a0f;
      --card: #1a0f1f;
      --muted: #9d8ba5;
      --text: #e8dff0;
      --accent-pro: #8b4789;
      --accent-rag: #b8860b;
      --border: rgba(139, 71, 137, .15);
      --success: #6b8e23;
      --warning: #daa520;
      --error: #8b0000;
    }
     
    * { box-sizing: border-box; }
    
    body {
      margin: 0;
      font-family: 'Garamond', 'Georgia', serif, ui-sans-serif, system-ui;
      background: radial-gradient(1200px 600px at 20% 10%, rgba(139, 71, 137, .2), transparent 60%), 
                  radial-gradient(1000px 500px at 80% 90%, rgba(75, 0, 130, .15), transparent 60%), 
                  var(--bg);
      color: var(--text);
      line-height: 1.6;
    }
    
    .wrap {
      max-inline-size: 100%;
      margin: 0 auto;
      padding: 8px 10px;
      block-size: 100vh;
      display: flex;
      flex-direction: column;
    }
    
    /* Header unificado */
    .header {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 14px;
      margin-block-end: 10px;
      padding: 10px 16px;
      background: linear-gradient(135deg, rgba(26, 15, 31, 0.95), rgba(40, 20, 50, 0.9));
      border-radius: 12px;
      border: 1px solid rgba(139, 71, 137, .3);
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 20px rgba(139, 71, 137, .25);
      flex-shrink: 0;
    }
    
    .logo {
      inline-size: 42px;
      block-size: 42px;
      border-radius: 12px;
      background: linear-gradient(135deg, #4b0082, #8b4789, #b8860b);
      box-shadow: 0 8px 20px rgba(139, 71, 137, .5), inset 0 1px 1px rgba(255,255,255,.1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      border: 1px solid rgba(184, 134, 11, .3);
    }
    
    .title h1 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      letter-spacing: 0.5px;
      background: linear-gradient(135deg, var(--accent-pro), var(--accent-rag));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .header-status {
      display: none;
    }
    
    .status-badge {
      font-size: 10px;
      padding: 5px 10px;
      border-radius: 999px;
      border: 1px solid;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    
    .status-badge.pro {
      border-color: var(--accent-pro);
      background: rgba(124, 92, 255, .1);
      color: var(--accent-pro);
    }
    
    .status-badge.rag {
      border-color: var(--accent-rag);
      background: rgba(184, 134, 11, 0.15);
      color: var(--accent-rag);
    }
    
    .status-dot {
      inline-size: 5px;
      block-size: 5px;
      border-radius: 50%;
      background: var(--warning);
    }
    
    .status-dot.connected { background: var(--success); }
    
    /* Tabs de selección de proyecto */
    .tabs {
      display: flex;
      flex-wrap: nowrap;
      gap: 8px;
      margin-block-end: 8px;
      padding: 6px 10px;
      background: linear-gradient(135deg, rgba(26, 15, 31, .7), rgba(40, 20, 50, .6));
      border-radius: 12px;
      border: 1px solid rgba(139, 71, 137, .25);
      box-shadow: inset 0 2px 8px rgba(0,0,0,.3);
      flex-shrink: 0;
      overflow-x: auto;
    }
    
    .tab {
      padding: 8px 14px;
      border-radius: 999px;
      border: 1px solid var(--border);
      cursor: pointer;
      text-align: center;
      transition: all 0.2s;
      font-weight: 500;
      font-size: 12px;
      background: rgba(255, 255, 255, .03);
      color: var(--text);
      white-space: nowrap;
      min-inline-size: 120px;
    }
    
    .tab.pro:hover {
      border-color: var(--accent-pro);
      background: rgba(139, 71, 137, .25);
      transform: translateY(-2px);
      box-shadow: 0 0 15px rgba(139, 71, 137, .4);
    }
    
    .tab.pro.active {
      border-color: var(--accent-pro);
      background: linear-gradient(135deg, rgba(139, 71, 137, .35), rgba(75, 0, 130, .3));
      box-shadow: 0 2px 8px rgba(139, 71, 137, .5), inset 0 1px 1px rgba(255,255,255,.1);
    }
    

    
    .tab-title {
      font-size: 12px;
      font-weight: 500;
    }
    
    /* Layout principal */
    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      flex: 1;
      min-block-size: 0;
    }
    
    /* Chat compartido */
    .chat {
      background: linear-gradient(135deg, rgba(26, 15, 31, 0.95), rgba(20, 15, 25, 0.9));
      border: 1px solid rgba(139, 71, 137, .3);
      border-radius: 18px;
      overflow: hidden;
      backdrop-filter: blur(10px);
      box-shadow: 0 16px 60px rgba(0, 0, 0, 0.7), inset 0 1px 1px rgba(139, 71, 137, .2);
      display: flex;
      flex-direction: column;
      block-size: 100%;
    }
    
    .chat-header {
      padding: 16px 20px;
      border-block-end: 1px solid rgba(139, 71, 137, .3);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: linear-gradient(135deg, rgba(40, 20, 50, 0.8), rgba(26, 15, 31, 0.9));
      box-shadow: 0 2px 10px rgba(0,0,0,.3);
    }
    
    .chat-title {
      font-size: 14px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .project-indicator {
      inline-size: 8px;
      block-size: 8px;
      border-radius: 50%;
      background: var(--accent-pro);
    }
    
    .project-indicator.rag {
      background: var(--accent-rag);
    }
    
    .chat-hint {
      font-size: 11px;
      color: var(--muted);
      border: 1px solid var(--border);
      padding: 6px 10px;
      border-radius: 999px;
    }
    
    /* Sección de respuestas rápidas en el chat */
    .quick-section {
      padding: 8px 12px;
      border-block-end: 1px solid var(--border);
      background: linear-gradient(135deg, rgba(26, 15, 31, .6), rgba(40, 20, 50, .5));
      flex-shrink: 0;
    }
    
    .quick-section .small {
      color: var(--muted);
      font-size: 11px;
      margin-block-end: 10px;
    }
    
    /* Breadcrumb de navegación integrado en tabs */
    .tab-breadcrumb {
      font-size: 10px;
      color: var(--muted);
      opacity: 0.7;
      margin-block-start: 2px;
    }
    
    .msgs {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      scroll-behavior: smooth;
      min-block-size: 0;
    }
    
    .msg {
      display: flex;
      margin-block-end: 14px;
      animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .msg.me { justify-content: flex-end; }
    
    .bubble {
      max-inline-size: 95%;
      border: 1px solid var(--border);
      padding: 12px 16px;
      border-radius: 16px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-wrap: break-word;
      position: relative;
    }
    
    .bubble.bot {
      background: linear-gradient(135deg, rgba(40, 20, 50, 0.8), rgba(26, 15, 31, 0.9));
      border-start-start-radius: 4px;
      border: 1px solid rgba(139, 71, 137, .25);
      box-shadow: 0 2px 8px rgba(0, 0, 0, .4);
    }
    
    .bubble.me {
      background: linear-gradient(135deg, rgba(60, 45, 70, 0.7), rgba(50, 35, 55, 0.8));
      border: 1px solid rgba(184, 134, 11, .3);
      border-start-end-radius: 4px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, .4);
    }
    
    /* Indicador de proyecto en mensajes */
    .bubble::after {
      content: attr(data-project);
      position: absolute;
      inset-block-end: 4px;
      inset-inline-end: 8px;
      font-size: 9px;
      color: var(--muted);
      opacity: 0.5;
    }
    
    .bubble strong { color: #daa520; }
    
    /* Compositor unificado */
    .composer {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-block-start: 1px solid var(--border);
      background: linear-gradient(135deg, rgba(26, 15, 31, .6), rgba(40, 20, 50, .5));
      box-shadow: 0 -2px 10px rgba(0,0,0,.3);
    }
    
    input {
      flex: 1;
      background: rgba(26, 15, 31, .6);
      border: 1px solid rgba(139, 71, 137, .3);
      color: var(--text);
      padding: 13px 16px;
      border-radius: 12px;
      outline: none;
      font-size: 14px;
      transition: all 0.2s;
    }
    
    input:focus {
      border-color: var(--accent-pro);
      box-shadow: 0 0 0 3px rgba(139, 71, 137, .3), 0 0 15px rgba(139, 71, 137, .2);
    }
    
    input:focus.rag-mode {
      border-color: var(--accent-rag);
      box-shadow: 0 0 0 3px rgba(184, 134, 11, .3), 0 0 15px rgba(184, 134, 11, .2);
    }
    
    input:focus.ollama-mode {
      border-color: #6b8e23;
      box-shadow: 0 0 0 3px rgba(107, 142, 35, .3), 0 0 15px rgba(107, 142, 35, .2);
    }
    
    button {
      background: linear-gradient(135deg, #8b4789, #4b0082);
      border: 1px solid rgba(139, 71, 137, .4);
      color: white;
      padding: 13px 24px;
      border-radius: 12px;
      font-weight: 600;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s;
      box-shadow: 0 4px 12px rgba(139, 71, 137, .3);
    }
    
    button.rag-mode {
      background: linear-gradient(135deg, #b8860b, #daa520);
      border: 1px solid rgba(184, 134, 11, .4);
      box-shadow: 0 4px 12px rgba(184, 134, 11, .3);
    }
    
    button.ollama-mode {
      background: linear-gradient(135deg, #6b8e23, #556b2f);
      border: 1px solid rgba(107, 142, 35, .4);
      box-shadow: 0 4px 12px rgba(107, 142, 35, .3);
    }
    
    button:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(139, 71, 137, .6), 0 0 25px rgba(139, 71, 137, .3);
    }
    
    button.rag-mode:hover:not(:disabled) {
      box-shadow: 0 8px 20px rgba(184, 134, 11, .6), 0 0 25px rgba(184, 134, 11, .3);
    }
    
    button.ollama-mode:hover:not(:disabled) {
      box-shadow: 0 8px 20px rgba(107, 142, 35, .6), 0 0 25px rgba(107, 142, 35, .3);
    }
    
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    /* Sidebar unificado */
    .side {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .side-card {
      background: linear-gradient(135deg, rgba(26, 15, 31, .7), rgba(40, 20, 50, .6));
      border: 1px solid rgba(139, 71, 137, .3);
      border-radius: 16px;
      padding: 16px;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 15px rgba(0, 0, 0, .5), inset 0 1px 1px rgba(139, 71, 137, .1);
    }
    
    .side-card h3 {
      margin: 0 0 12px;
      font-size: 15px;
      color: #daa520;
      text-shadow: 0 1px 3px rgba(0,0,0,.5);
    }
    
    .small {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }
    
    .chips {
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      gap: 6px;
      margin-block-start: 10px;
    }
    
    .chip {
      border: 1px solid rgba(139, 71, 137, .3);
      color: var(--text);
      background: rgba(26, 15, 31, .5);
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .chip:hover {
      border-color: var(--accent-pro);
      background: rgba(139, 71, 137, .3);
      transform: translateY(-2px);
      box-shadow: 0 0 15px rgba(139, 71, 137, .4);
    }
    
    .chip.rag-mode:hover {
      border-color: var(--accent-rag);
      background: rgba(184, 134, 11, .3);
      box-shadow: 0 0 15px rgba(184, 134, 11, .4);
    }
    
    .info-grid {
      display: grid;
      gap: 10px;
      margin-block-start: 12px;
    }
    
    .info-item {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      padding: 8px 0;
      border-block-end: 1px solid var(--border);
    }
    
    .info-label { color: var(--muted); }
    .info-value { 
      color: var(--text); 
      font-weight: 500; 
      font-family: monospace;
      font-size: 11px;
    }
    
    hr {
      border: 0;
      border-block-start: 1px solid var(--border);
      margin: 14px 0;
    }
    
    a { color: #ba8bcc; text-decoration: none; }
    a:hover { text-decoration: underline; color: #daa520; }
    
    /* Animación de puntos de escritura */
    .typing-dots {
      display: inline-block;
      margin-inline-start: 4px;
    }
    
    .typing-dots::after {
      content: '...';
      animation: typing 1.4s infinite;
    }
    
    @keyframes typing {
      0%, 20% { content: '.'; }
      40% { content: '..'; }
      60%, 100% { content: '...'; }
    }
    
    #typing-indicator {
      animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <!-- Tabs de selección -->
    <div class="tabs">
      <div class="tab pro active" id="tabPro">
        <span class="tab-title">🔒 Agente Pro</span>
      </div>

    </div>

    <!-- Layout principal -->
    <div class="grid">
      <!-- Chat compartido -->
      <div class="chat">
        <div class="msgs" id="msgs"></div>

        <div class="composer">
          <input id="inp" placeholder="Escribe tu pregunta o comando..."/>
          <button id="btn">Enviar</button>
        </div>
      </div>
    </div>
  </div>

<script src="<?php echo $configJsPath; ?>"></script>
<script>
  // Backend OLLAMA (Puerto 8002)
  // Conexión directa a los backends
  // Agente Bit Pro: puerto 8001
  // Agente Bit RAG: puerto 8000
  // Agente Bit Ollama: puerto 8002

  const API_PRO = CONFIG.API_PRO;  
  const API_RAG = CONFIG.API_RAG;  
  const API_OLLAMA = CONFIG.API_OLLAMA;  // Llama3.2:3b vía Ollama
  
  // Estado global
  let currentProject = 'pro';  // 'pro', 'rag', o 'ollama'
  let sessionId = generateUUID();
  
  // Elementos DOM
  const msgs = document.getElementById("msgs");
  const inp = document.getElementById("inp");
  const btn = document.getElementById("btn");
  const tabPro = document.getElementById("tabPro");
  const tabOllama = document.getElementById("tabOllama");
  const tabRag = document.getElementById("tabRag");
  
  // Estado del breadcrumb
  let breadcrumbPath = [{ icon: '🏠', label: 'Inicio', state: 'ROOT' }];
  // const statusPro = document.getElementById("statusPro");
  // const statusRag = document.getElementById("statusRag");
  // const dotPro = document.getElementById("dotPro");
  // const dotRag = document.getElementById("dotRag");
  // const chatTitle = document.getElementById("chatTitle");
  // const projectIndicator = document.getElementById("projectIndicator");
  // const activeProject = document.getElementById("activeProject");
  // const apiUrl = document.getElementById("apiUrl");
  // const sidDisplay = document.getElementById("sid");
  // const datasetInfo = document.getElementById("datasetInfo");
  // const projectFeatures = document.getElementById("projectFeatures");
  
  // Generar UUID
  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  
  // Inicializar sesión
  sessionId = localStorage.getItem("agentebit_unified_sid") || generateUUID();
  localStorage.setItem("agentebit_unified_sid", sessionId);
  // sidDisplay.textContent = sessionId.substring(0, 8) + "...";
  
  // Agregar mensaje al chat (sin chips)
  function addMsg(who, text, project = currentProject) {
    const wrap = document.createElement("div");
    wrap.className = "msg " + (who === "me" ? "me" : "bot");
    
    const bubble = document.createElement("div");
    bubble.className = "bubble " + (who === "me" ? "me" : "bot");
    const projectLabel = project === 'pro' ? 'PRO' : 
                         project === 'rag' ? 'RAG' : 'OLLAMA';
    bubble.setAttribute("data-project", projectLabel);
    
    // Convertir URLs, emails y teléfonos en enlaces clicables
    if (who === "bot") {
      const processedText = makeLinksClickable(text);
      bubble.innerHTML = processedText;
    } else {
      bubble.textContent = text;
    }
    
    wrap.appendChild(bubble);
    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
    
    return wrap;
  }
  
  // Agregar mensaje del bot con chips integrados
  async function addMsgWithChips(who, text, quickReplies = []) {
    // Para Ollama, usar efecto de escritura tipo máquina
    if (currentProject === 'ollama' && who === 'bot') {
      const msgWrap = addMsg(who, '');
      const bubble = msgWrap.querySelector('.bubble');
      const processedText = makeLinksClickable(text);
      await typeWriterEffect(bubble, processedText, 15);
    } else {
      // Para Pro y RAG, agregar mensaje normal
      addMsg(who, text);
    }
    
    // Siempre mostrar chips si estamos en Pro/RAG/Ollama o si hay quickReplies
    if (quickReplies.length > 0 || currentProject === 'pro' || currentProject === 'rag' || currentProject === 'ollama') {
      const wrap = document.createElement("div");
      wrap.className = "msg bot";
      
      const bubble = document.createElement("div");
      bubble.className = "bubble bot";
      const projectLabel = currentProject === 'pro' ? 'PRO' : 
                           currentProject === 'rag' ? 'RAG' : 'OLLAMA';
      bubble.setAttribute("data-project", projectLabel);
      
      // Contenedor de chips dentro del mensaje
      const chipsContainer = document.createElement("div");
      chipsContainer.style.display = "flex";
      chipsContainer.style.flexWrap = "wrap";
      chipsContainer.style.gap = "8px";
      

      
      // Agregar chip de retorno si estamos en modo RAG u Ollama
      if (currentProject === 'rag' || currentProject === 'ollama') {
        const returnChip = document.createElement("div");
        returnChip.className = "chip";
        returnChip.textContent = "🏠 Volver a Menú";
        returnChip.style.borderColor = "var(--accent-pro)";
        returnChip.style.background = "rgba(139, 71, 137, .2)";
        returnChip.style.cursor = "pointer";
        returnChip.onclick = () => {
          switchProject('pro');
          updateBreadcrumb('ROOT', 'Inicio');
        };
        chipsContainer.appendChild(returnChip);
      }
      
      // Agregar chips de respuestas rápidas
      quickReplies.slice(0, 20).forEach(label => {
        const chip = document.createElement("div");
        chip.className = "chip" + (currentProject === 'rag' ? ' rag-mode' : '');
        chip.textContent = label;
        chip.style.cursor = "pointer";
        chip.onclick = () => send(label);
        chipsContainer.appendChild(chip);
      });
      
      // En modo Ollama, siempre agregar sugerencias inteligentes si no hay quick_replies
      if (currentProject === 'ollama' && quickReplies.length === 0) {
        const suggestions = [
          "¿Qué es ransomware?",
          "¿Cómo proteger mi información personal?",
          "Diferencia entre malware y virus",
          "¿Qué es autenticación de dos factores?",
          "Consejos para navegación segura",
          "¿Cómo identificar un correo falso?"
        ];
        // Mostrar 4 sugerencias aleatorias
        const randomSuggestions = suggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
        randomSuggestions.forEach(label => {
          const chip = document.createElement("div");
          chip.className = "chip";
          chip.textContent = label;
          chip.style.borderColor = "#6b8e23";
          chip.style.background = "rgba(107, 142, 35, .2)";
          chip.style.cursor = "pointer";
          chip.onclick = () => send(label);
          chipsContainer.appendChild(chip);
        });
      }
      
      bubble.appendChild(chipsContainer);
      wrap.appendChild(bubble);
      msgs.appendChild(wrap);
      msgs.scrollTop = msgs.scrollHeight;
    }
  }
  
  // Función para convertir URLs, emails y teléfonos en enlaces clicables
  function makeLinksClickable(text) {
    // Escapar HTML para prevenir XSS
    const escapeHtml = (str) => {
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    };
    
    let processed = escapeHtml(text);
    
    // Convertir URLs (http://, https://)
    processed = processed.replace(
      /(https?:\/\/[^\s<]+[^\s<.,;:!?)])/gi,
      '<a href="$1" target="_blank" rel="noopener noreferrer" style="color: #daa520; text-decoration: underline;">$1</a>'
    );
    
    // Convertir emails
    processed = processed.replace(
      /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/gi,
      '<a href="mailto:$1" style="color: #daa520; text-decoration: underline;">$1</a>'
    );
    
    // Convertir números de teléfono (varios formatos)
    processed = processed.replace(
      /\b(\d{10}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\(\d{3}\)\s*\d{3}[-.\s]?\d{4}|\d{2}[-.\s]?\d{2}[-.\s]?\d{4})\b/g,
      '<a href="tel:$1" style="color: #daa520; text-decoration: underline;">$1</a>'
    );
    
    return processed;
  }
  
  // Actualizar breadcrumb de navegación (ahora en el tab)
  function updateBreadcrumb(state, label) {
    // console.log('updateBreadcrumb:', state, label);
    
    // Mapeo de estados a iconos
    const stateIcons = {
      'ROOT': '🏠',
      'MENU': '📋',
      'CONSEJOS': '�',
      'AMENAZAS': '⚠️',
      'REPORTE': '📝',
      'CIBERATAQUES': '🔒',
      'DIRECTORIO': '📞',
      'CATEGORIA': '📂',
      'PREGUNTA': '❓',
      'GLOSARY': '📖'
    };
    
    // Función para obtener icono contextual basado en el label
    const getContextualIcon = (text) => {
      const lower = text.toLowerCase();
      
      // Términos de ciberseguridad
      if (lower.includes('malware') || lower.includes('virus')) return '🦠';
      if (lower.includes('phishing') || lower.includes('suplantación')) return '🎣';
      if (lower.includes('ransomware') || lower.includes('rescate')) return '🔐';
      if (lower.includes('firewall') || lower.includes('cortafuegos')) return '🔥';
      if (lower.includes('contraseña') || lower.includes('password')) return '🔑';
      if (lower.includes('cifrado') || lower.includes('encriptación')) return '🔒';
      if (lower.includes('vulnerabilidad') || lower.includes('exploit')) return '🛡️';
      if (lower.includes('ataque') || lower.includes('attack')) return '⚔️';
      if (lower.includes('ddos') || lower.includes('denegación')) return '💥';
      if (lower.includes('backdoor') || lower.includes('puerta trasera')) return '🚪';
      if (lower.includes('spyware') || lower.includes('espía')) return '👁️';
      if (lower.includes('trojan') || lower.includes('troyano')) return '🐴';
      if (lower.includes('bot') || lower.includes('zombie')) return '🤖';
      if (lower.includes('hacke') || lower.includes('intrus')) return '💻';
      if (lower.includes('seguridad') || lower.includes('security')) return '🛡️';
      if (lower.includes('autenticación') || lower.includes('authentication')) return '✅';
      if (lower.includes('vpn') || lower.includes('red privada')) return '🔗';
      if (lower.includes('cookie') || lower.includes('rastreo')) return '🍪';
      if (lower.includes('certificado') || lower.includes('ssl')) return '📜';
      if (lower.includes('backup') || lower.includes('respaldo')) return '💾';
      
      // Términos de dispositivos y tecnología
      if (lower.includes('móvil') || lower.includes('celular') || lower.includes('smartphone')) return '📱';
      if (lower.includes('computadora') || lower.includes('pc') || lower.includes('laptop')) return '💻';
      if (lower.includes('tablet')) return '📱';
      if (lower.includes('red') || lower.includes('network') || lower.includes('wifi')) return '🌐';
      if (lower.includes('servidor') || lower.includes('server')) return '🖥️';
      if (lower.includes('nube') || lower.includes('cloud')) return '☁️';
      if (lower.includes('correo') || lower.includes('email') || lower.includes('mail')) return '📧';
      if (lower.includes('navegador') || lower.includes('browser')) return '🌐';
      if (lower.includes('software') || lower.includes('aplicación') || lower.includes('app')) return '⚙️';
      
      // Términos de información y documentación
      if (lower.includes('glosario') || lower.includes('diccionario')) return '📖';
      if (lower.includes('ayuda') || lower.includes('help') || lower.includes('soporte')) return '❓';
      if (lower.includes('documentación') || lower.includes('manual')) return '📚';
      if (lower.includes('tutorial') || lower.includes('guía')) return '📝';
      if (lower.includes('tip') || lower.includes('consejo')) return '💡';
      if (lower.includes('alerta') || lower.includes('warning')) return '⚠️';
      if (lower.includes('error') || lower.includes('problema')) return '❌';
      if (lower.includes('éxito') || lower.includes('success')) return '✅';
      if (lower.includes('info') || lower.includes('información')) return 'ℹ️';
      
      // Términos de categorías y organización
      if (lower.includes('categoría') || lower.includes('category')) return '📂';
      if (lower.includes('lista') || lower.includes('list')) return '📋';
      if (lower.includes('búsqueda') || lower.includes('search')) return '🔍';
      if (lower.includes('configuración') || lower.includes('settings')) return '⚙️';
      if (lower.includes('perfil') || lower.includes('profile') || lower.includes('usuario')) return '👤';
      
      // Términos de acciones
      if (lower.includes('descargar') || lower.includes('download')) return '⬇️';
      if (lower.includes('subir') || lower.includes('upload')) return '⬆️';
      if (lower.includes('compartir') || lower.includes('share')) return '📤';
      if (lower.includes('eliminar') || lower.includes('delete')) return '🗑️';
      if (lower.includes('editar') || lower.includes('edit')) return '✏️';
      if (lower.includes('guardar') || lower.includes('save')) return '💾';
      
      // Estados de México (para el directorio de policía)
      if (lower.includes('querétaro')) return '🏛️';
      if (lower.includes('cdmx') || lower.includes('ciudad de méxico')) return '🏙️';
      if (lower.includes('guadalajara') || lower.includes('jalisco')) return '🌆';
      if (lower.includes('monterrey') || lower.includes('nuevo león')) return '🏔️';
      if (lower.includes('puebla')) return '⛪';
      if (lower.includes('cancún') || lower.includes('quintana roo')) return '🏖️';
      
      // Por defecto, usar un icono genérico según el tipo de texto
      if (/^[A-Z_]+$/.test(text)) return '🔹'; // Estados en mayúsculas
      if (text.length < 15) return '📌'; // Textos cortos
      return '💬'; // Textos largos o preguntas
    };
    
    const icon = stateIcons[state] || getContextualIcon(label);
    
    // Si es ROOT, reiniciar el breadcrumb
    if (state === 'ROOT') {
      breadcrumbPath = [{ icon: '🏠', label: 'Inicio', state: 'ROOT' }];
    } else {
      // Verificar si el estado ya existe en el path
      const existingIndex = breadcrumbPath.findIndex(item => item.state === state);
      
      if (existingIndex !== -1) {
        // Truncar el path hasta ese punto
        breadcrumbPath = breadcrumbPath.slice(0, existingIndex + 1);
      } else {
        // Agregar nuevo nivel
        breadcrumbPath.push({ icon, label, state });
      }
    }
    
    // Renderizar breadcrumb en el tab superior
    if (tabPro) {
      const currentItem = breadcrumbPath[breadcrumbPath.length - 1];
      let breadcrumbText = '';
      
      // Construir ruta del breadcrumb
      if (breadcrumbPath.length > 1) {
        breadcrumbText = breadcrumbPath.map(item => `${item.icon} ${item.label}`).join(' › ');
      } else {
        breadcrumbText = `${currentItem.icon} ${currentItem.label}`;
      }
      
      // Actualizar el tab con el breadcrumb
      tabPro.innerHTML = `<span class="tab-title">${breadcrumbText}</span>`;
      
      // Agregar funcionalidad de clic para volver al inicio si no estamos en ROOT
      if (state !== 'ROOT') {
        tabPro.style.cursor = 'pointer';
        tabPro.onclick = () => {
          switchProject('pro');
          updateBreadcrumb('ROOT', 'Inicio');
        };
      } else {
        tabPro.style.cursor = 'default';
        tabPro.onclick = null;
      }
    }
  }
  

  
  // Cambiar proyecto activo
  function switchProject(project) {
    // console.log('switchProject called:', project);
    if (currentProject === project) return;
    
    currentProject = project;
    
    // Actualizar tabs
    if (tabPro) {
      tabPro.classList.toggle('active', project === 'pro');
    }
    if (tabRag) {
      tabRag.classList.toggle('active', project === 'rag');
    }
    if (tabOllama) {
      tabOllama.classList.toggle('active', project === 'ollama');
    }
    
    // Limpiar mensajes del chat al cambiar de proyecto
    msgs.innerHTML = '';
    
    // Actualizar indicador (elementos removidos del DOM)
    // projectIndicator.classList.toggle('rag', project === 'rag');
    // chatTitle.textContent = project === 'pro' ? 'Agente Bit Pro' : 'Agente Bit RAG';
    
    // Actualizar estilos de inputs
    inp.classList.toggle('rag-mode', project === 'rag');
    btn.classList.toggle('rag-mode', project === 'rag');
    inp.classList.toggle('ollama-mode', project === 'ollama');
    btn.classList.toggle('ollama-mode', project === 'ollama');
    
    // Actualizar placeholders
    if (project === 'pro') {
      inp.placeholder = 'Escribe tu comando... (ej: Reportar un incidente, Directorio)';
    } else if (project === 'rag') {
      inp.placeholder = 'Pregunta sobre términos de ciberseguridad...';
    } else if (project === 'ollama') {
      inp.placeholder = 'Pregunta lo que quieras al Asistente IA...';
    }
    
    // Actualizar información del proyecto
    updateProjectInfo();
    
    // Enviar comando menu para obtener las categorías/respuestas rápidas del proyecto
    // En modo Ollama, mostrar mensaje de bienvenida sin enviar automáticamente
    setTimeout(() => {
      if (project === 'ollama') {
        // Mostrar mensaje de bienvenida del asistente IA
        const welcomeMsg = "Soy tu Asistente de ciberseguridad. Puedo ayudarte con cualquier pregunta sobre seguridad digital, amenazas, protección de datos y más. ¿En qué puedo ayudarte hoy?";
        addMsgWithChips("bot", welcomeMsg, []);
      } else {
        send("menu");
      }
    }, 200);
  }
  
  // Actualizar información del proyecto (deshabilitado - sidebar removido)
  function updateProjectInfo() {
    // if (currentProject === 'pro') {
    //   projectFeatures.innerHTML = `
    //     • Menús interactivos<br/>
    //     • Formularios de reporte<br/>
    //     • Directorio de Policía Cibernética<br/>
    //     • Recomendaciones personalizadas
    //   `;
    //   datasetInfo.textContent = "Menús dinámicos";
    // } else {
    //   projectFeatures.innerHTML = `
    //     • Búsqueda RAG semántica<br/>
    //     • 2366 preguntas/respuestas<br/>
    //     • 8 categorías temáticas<br/>
    //     • Precisión 55%-75%
    //   `;
    //   datasetInfo.textContent = "2366 entradas";
    // }
  }
  
  // Ping a todos los backends - DESHABILITADO
  /*
  async function pingBackends() {
    // Ping Agente Bit Pro
    try {
      const r = await fetch(API_PRO + "/health", { mode: "cors" });
      //console.log('Agente Bit Pro health:', r.ok);
      // if (r.ok) { dotPro.classList.add('connected'); }
      // else { dotPro.classList.remove('connected'); }
    } catch(e) {
      //console.error('Agente Bit Pro ping error:', e);
      // dotPro.classList.remove('connected');
    }
    
    // Ping Agente Bit RAG
    try {
      const r = await fetch(API_RAG + "/health", { mode: "cors" });
      //console.log('Agente Bit RAG health:', r.ok);
      // if (r.ok) { dotRag.classList.add('connected'); }
      // else { dotRag.classList.remove('connected'); }
    } catch(e) {
      //console.error('Agente Bit RAG ping error:', e);
      // dotRag.classList.remove('connected');
    }
    
    // Ping Agente Bit Ollama
    try {
      const r = await fetch(API_OLLAMA + "/health", { mode: "cors" });
      //console.log('Agente Bit Ollama health:', r.ok);
      if (r.ok) {
        const data = await r.json();
        //console.log('Ollama model:', data.model, '- loaded:', data.model_loaded);
      }
    } catch(e) {
      //console.error('Agente Bit Ollama ping error:', e);
    }
  }
  */
  
  // Agregar indicador de escritura
  function addTypingIndicator() {
    const wrap = document.createElement("div");
    wrap.className = "msg bot";
    wrap.id = "typing-indicator";
    
    const bubble = document.createElement("div");
    bubble.className = "bubble bot";
    bubble.setAttribute("data-project", "OLLAMA");
    bubble.innerHTML = '<span style="opacity: 0.6;">🤖 Pensando</span><span class="typing-dots"></span>';
    
    wrap.appendChild(bubble);
    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
    
    return wrap;
  }
  
  // Efecto de escritura tipo máquina para Ollama
  function typeWriterEffect(element, text, speed = 20) {
    return new Promise((resolve) => {
      let i = 0;
      element.innerHTML = '';
      
      function type() {
        if (i < text.length) {
          element.innerHTML += text.charAt(i);
          i++;
          msgs.scrollTop = msgs.scrollHeight;
          setTimeout(type, speed);
        } else {
          resolve();
        }
      }
      
      type();
    });
  }
  
  // Enviar mensaje
  async function send(text) {
    if (!text) return;
    
    addMsg("me", text);
    inp.value = "";
    btn.disabled = true;
    inp.disabled = true;
    
    // Mostrar indicador de escritura para Ollama
    let typingIndicator = null;
    if (currentProject === 'ollama') {
      typingIndicator = addTypingIndicator();
    }
    
    // Para Pro: puerto 8001 /api/chat
    // Para RAG: puerto 8000 /api/chat
    // Para Ollama: puerto 8002 /api/chat
    let apiEndpoint;
    if (currentProject === 'pro') {
      apiEndpoint = API_PRO + "/api/chat";
    } else if (currentProject === 'rag') {
      apiEndpoint = API_RAG + "/api/chat";
    } else if (currentProject === 'ollama') {
      apiEndpoint = API_OLLAMA + "/api/chat";
    }
    
    try {
      const response = await fetch(apiEndpoint, {
        method: "POST",
        mode: "cors",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          session_id: sessionId, 
          message: text 
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      // console.log('Response data:', data);
      // console.log('Quick replies:', data.quick_replies);
      
      // Remover indicador de escritura
      if (typingIndicator) {
        typingIndicator.remove();
      }
      
      // Agregar mensaje del bot con chips integrados
      // En modo Ollama no hay quick_replies estructurados del backend
      const quickReplies = currentProject === 'ollama' ? [] : (data.quick_replies || []);
      await addMsgWithChips("bot", data.reply || "...", quickReplies);
      
      // Actualizar breadcrumb si hay información de estado
      if (currentProject === 'ollama') {
        // En modo Ollama, actualizar breadcrumb con el tema de la conversación
        // Solo si es una pregunta específica
        if (text.length > 20 && text.includes('?')) {
          const shortQuestion = text.length > 30 ? text.substring(0, 30) + '...' : text;
          updateBreadcrumb('PREGUNTA', shortQuestion);
        }
      } else if (data.state) {
        const stateLabels = {
          'ROOT': 'Inicio',
          'MENU': 'Menú Principal',
          'CONSEJOS': 'Consejos de Seguridad',
          'AMENAZAS': 'Detectar Amenazas',
          'REPORTE': 'Reportar Incidente',
          'CIBERATAQUES': 'Ciberataques',
          'DIRECTORIO': 'Directorio Policía',
          'CATEGORIA': text,
          'PREGUNTA': text
        };
        const label = stateLabels[data.state] || data.state;
        updateBreadcrumb(data.state, label);
      }
      
      // Actualizar estado de conexión (elementos removidos)
      // if (currentProject === 'pro') { dotPro.classList.add('connected'); }
      // else { dotRag.classList.add('connected'); }
      
    } catch(e) {
      console.error("Error en send:", e);
      
      // Remover indicador de escritura si existe
      if (typingIndicator) {
        typingIndicator.remove();
      }
      
      const backendName = currentProject === 'pro' ? 'Agente Bit Pro' : 
                          currentProject === 'rag' ? 'Agente Bit RAG' : 
                          'Agente Bit Ollama';
      addMsg("bot", `❌ Error: ${e.message}\n\nVerifica que el backend ${backendName} esté ejecutándose.`);
      
      // Actualizar estado de conexión (elementos removidos)
      // if (currentProject === 'pro') { dotPro.classList.remove('connected'); }
      // else { dotRag.classList.remove('connected'); }
    } finally {
      btn.disabled = false;
      inp.disabled = false;
      inp.focus();
    }
  }
  
  // Event listeners
  btn.onclick = () => send(inp.value.trim());
  inp.addEventListener("keydown", (e) => {
    if (e.key === "Enter") send(inp.value.trim());
  });
  
  // Tab listeners
  if (tabPro) {
    tabPro.onclick = () => switchProject('pro');
  }
  
  // Inicialización
  (async () => {
    // console.log('=== Inicializando Agente Bit Unified ===');
    // console.log('Proyecto actual:', currentProject);
    // console.log('API PRO:', API_PRO);
    // console.log('API RAG:', API_RAG);
    // console.log('API OLLAMA:', API_OLLAMA);
    
    // Ping inicial - DESHABILITADO
    // await pingBackends();
    
    // Actualizar info del proyecto
    updateProjectInfo();
    
    // Auto-start
    // console.log('Enviando comando menu inicial...');
    setTimeout(() => send("menu"), 500);
    
    // Ping periódico - DESHABILITADO
    // setInterval(pingBackends, 5000);
  })();
  
  // ===== Listener para chips del header del widget padre (rc.php) =====
  // Recibe postMessage y ejecuta switchProject + updateBreadcrumb igual que los chips internos
  window.addEventListener('message', (e) => {
    if (!e.data || e.data.type !== 'nova-switch-project') return;
    const { project, breadcrumb } = e.data;
    if (!project) return;
    switchProject(project);
    if (breadcrumb && breadcrumb.state && breadcrumb.label) {
      updateBreadcrumb(breadcrumb.state, breadcrumb.label);
    }
  });
</script>
</body>
</html>
