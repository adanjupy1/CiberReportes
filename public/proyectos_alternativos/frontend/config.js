
const CONFIG = {
  // URL base del servidor (detecta automáticamente)
  SERVER_URL: window.location.origin,  
  
  // URLs de los backends via proxy reverso (Apache) - usando rutas relativas
  API_RAG: '/api/backend-rag',        // Puerto 8000 - chatbot_rag_menu
  API_PRO: '/api/backend-pro',        // Puerto 8001 - uiibot_pro
  API_OLLAMA: '/api/backend-ollama',  // Puerto 8002 - uiibot_unified
  
  // Puertos de cada backend (para referencia)
  API_PORT_RAG: '8000',    // chatbot_rag_menu
  API_PORT_PRO: '8001',    // uiibot_pro
  API_PORT_OLLAMA: '8002', // uiibot_unified
  
  // Alias para compatibilidad con código existente
  get API_BASE() {
    // Por defecto retorna la API según el proyecto que lo use
    // Los proyectos individuales pueden definir cuál usar
    return this.API_RAG; // default
  },
  get API_PORT() {
    return this.API_PORT_RAG; // default
  },
  
  // Aliases para uiibot_unified
  get API_PRO_PORT() {
    return this.API_PORT_PRO;
  },
  get API_RAG_PORT() {
    return this.API_PORT_RAG;
  },
  get API_OLLAMA_PORT() {
    return this.API_PORT_OLLAMA;
  }
};

// Sobrescribir con valores de localStorage si existen
if (localStorage.getItem('SERVER_URL')) {
  CONFIG.SERVER_URL = localStorage.getItem('SERVER_URL');
}
if (localStorage.getItem('API_PORT_RAG')) {
  CONFIG.API_PORT_RAG = localStorage.getItem('API_PORT_RAG');
}
if (localStorage.getItem('API_PORT_PRO')) {
  CONFIG.API_PORT_PRO = localStorage.getItem('API_PORT_PRO');
}
if (localStorage.getItem('API_PORT_OLLAMA')) {
  CONFIG.API_PORT_OLLAMA = localStorage.getItem('API_PORT_OLLAMA');
}

// Compatibilidad con nombres antiguos
if (localStorage.getItem('API_PORT')) {
  CONFIG.API_PORT_RAG = localStorage.getItem('API_PORT');
}
if (localStorage.getItem('API_PRO_PORT')) {
  CONFIG.API_PORT_PRO = localStorage.getItem('API_PRO_PORT');
}
if (localStorage.getItem('API_RAG_PORT')) {
  CONFIG.API_PORT_RAG = localStorage.getItem('API_RAG_PORT');
}
if (localStorage.getItem('API_OLLAMA_PORT')) {
  CONFIG.API_PORT_OLLAMA = localStorage.getItem('API_OLLAMA_PORT');
}

//console.log('CONFIG cargado:', {
  //SERVER_URL: CONFIG.SERVER_URL,
  //API_RAG: CONFIG.API_RAG,
  //API_PRO: CONFIG.API_PRO,
  //API_OLLAMA: CONFIG.API_OLLAMA
//});
