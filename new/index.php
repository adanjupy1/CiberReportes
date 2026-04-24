<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot - Data Base</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 90vh;
            background: #0f1419;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid #2d3748;
        }
        .chat-header {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 10px;
            text-align: center;
            border-bottom: 2px solid #4c1d95;
        }
        .chat-header h1 {
            font-size: 1.2rem;
            margin: 0;
        }
        .chat-header p {
            font-size: 0.9rem;
            margin: 5px 0;
        }
        .chat-header small {
            font-size: 0.75rem;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #1a202c;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
        }
        .message.user {
            align-items: flex-end;
        }
        .message.bot {
            align-items: flex-start;
        }
        .message-content {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.user .message-content {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        }
        .message.bot .message-content {
            background: #2d3748;
            color: #e2e8f0;
            border: 1px solid #4a5568;
        }
        .welcome-menu {
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            gap: 16px;
            max-width: 90%;
            background: #2d3748;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            border: 1px solid #4a5568;
        }
        .welcome-title {
            font-size: 18px;
            font-weight: bold;
            color: #a78bfa;
            margin-bottom: 15px;
            text-align: center;
        }
        .menu-option {
            padding: 15px;
            margin: 10px 0;
            background: #1a202c;
            border: 2px solid #4a5568;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
            color: #cbd5e0;
        }
        .menu-option:hover {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border-color: #6366f1;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(99, 102, 241, 0.4);
        }
        .menu-option::before {
            content: '💬';
            font-size: 24px;
            flex-shrink: 0;
        }
        .menu-option-text {
            flex: 1;
            font-weight: 500;
        }
        .menu-option-icon {
            font-size: 20px;
            opacity: 0.5;
        }
        .menu-option:hover .menu-option-icon {
            opacity: 1;
        }
        .related-options {
            max-width: 85%;
            margin-top: 10px;
            padding: 15px;
            background: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .related-title {
            font-weight: bold;
            color: #a78bfa;
            margin-bottom: 10px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .option-item {
            padding: 10px 15px;
            margin: 8px 0;
            background: #1a202c;
            border: 1px solid #4a5568;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            color: #cbd5e0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .option-item:hover {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border-color: #6366f1;
            transform: translateX(5px);
        }
        .option-item::before {
            content: '💡';
            font-size: 16px;
        }
        .option-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 500;
            margin-left: auto;
            background: #4a5568;
            color: #cbd5e0;
        }
        .option-item:hover .option-badge {
            background: rgba(255,255,255,0.3);
            color: white;
        }
        .chat-input {
            display: flex;
            padding: 20px;
            background: #0f1419;
            border-top: 1px solid #2d3748;
        }
        .chat-input input {
            flex: 1;
            padding: 12px;
            border: 1px solid #4a5568;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            background: #2d3748;
            color: #e2e8f0;
        }
        .chat-input input::placeholder {
            color: #718096;
        }
        .chat-input input:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }
        .chat-input button {
            margin-left: 10px;
            padding: 12px 25px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .chat-input button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        }
        .chat-input button:disabled {
            background: #4a5568;
            cursor: not-allowed;
            opacity: 0.5;
        }
        .loading {
            display: none;
            padding: 10px;
            text-align: center;
            color: #a78bfa;
        }
        .metadata {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 5px;
            color: #a0aec0;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>💬 Chatbot Formulario de Reportes Cíbernéticos</h1>
            <p>Pregúntame sobre reportes cibernéticos</p>
            <small style="opacity: 0.8;">🔒 Conexión SSL segura (Puerto 4433)</small>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-content">
                    ¡Hola! Soy tu asistente virtual para reportes cibernéticos. ¿En qué puedo ayudarte?
                </div>
            </div>
            <div class="message bot">
                <div class="welcome-menu">
                    <div class="welcome-title">🚀 Preguntas Frecuentes</div>
                    <div class="menu-option" data-question="Explícame registro de reportes cibernéticos como si fuera la primera vez que lleno el formulario.">
                        <span class="menu-option-text">¿Cómo registro un reporte cibernético?</span>
                        <span class="menu-option-icon">→</span>
                    </div>
                    <div class="menu-option" data-question="¿Qué es el folio?">
                        <span class="menu-option-text">¿Qué es el folio del reporte?</span>
                        <span class="menu-option-icon">→</span>
                    </div>
                    <div class="menu-option" data-question="¿Qué pongo en la descripción del incidente?">
                        <span class="menu-option-text">¿Cómo describo mi incidente?</span>
                        <span class="menu-option-icon">→</span>
                    </div>
                    <div class="menu-option" data-question="¿Qué puedo subir como evidencia?">
                        <span class="menu-option-text">¿Qué evidencias puedo adjuntar?</span>
                        <span class="menu-option-icon">→</span>
                    </div>
                    <div class="menu-option" data-question="¿Cómo completar el registro?">
                        <span class="menu-option-text">¿Cómo finalizo mi registro?</span>
                        <span class="menu-option-icon">→</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="loading" id="loading">Escribiendo...</div>
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Escribe tu mensaje aquí o selecciona una opción arriba..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()" id="sendBtn">Enviar</button>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const loading = document.getElementById('loading');

        // Control de animación typewriter
        let currentTypewriterController = null;
        const TYPEWRITER_SPEED = 15; // milisegundos por carácter

        // Verificar si el usuario prefiere reducir movimiento
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // Agregar event listeners a las opciones del menú
        document.addEventListener('DOMContentLoaded', function() {
            const menuOptions = document.querySelectorAll('.menu-option');
            menuOptions.forEach(option => {
                option.addEventListener('click', function() {
                    const question = this.getAttribute('data-question');
                    messageInput.value = question;
                    sendMessage();
                });
            });
        });

        // Función para animar texto con efecto typewriter
        async function typewriterEffect(element, text, controller) {
            // Si el usuario prefiere reducir movimiento, mostrar todo de inmediato
            if (prefersReducedMotion) {
                element.innerHTML = text;
                return;
            }

            element.innerHTML = '';
            const chars = text.split('');
            
            for (let i = 0; i < chars.length; i++) {
                // Verificar si la animación fue cancelada
                if (controller.signal.aborted) {
                    element.innerHTML = text; // Mostrar texto completo al cancelar
                    return;
                }
                
                element.innerHTML += chars[i];
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Esperar antes del siguiente carácter
                await new Promise(resolve => setTimeout(resolve, TYPEWRITER_SPEED));
            }
        }

        // Función mejorada para agregar mensajes con efecto typewriter
        async function addMessage(content, isUser = false, metadata = null) {
            // Cancelar animación anterior si existe (solo para mensajes del bot)
            if (!isUser && currentTypewriterController) {
                currentTypewriterController.abort();
            }

            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // Aplicar efecto typewriter solo a mensajes del bot
            if (!isUser) {
                currentTypewriterController = new AbortController();
                messageDiv.appendChild(contentDiv);
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Animar el texto
                await typewriterEffect(contentDiv, content, currentTypewriterController);
            } else {
                // Mensajes del usuario se muestran instantáneamente
                contentDiv.innerHTML = content;
                messageDiv.appendChild(contentDiv);
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Agregar metadata si existe (score, topic, etc.)
            if (metadata && !isUser) {
                const metaDiv = document.createElement('div');
                metaDiv.className = 'message-content metadata';
                let metaText = [];
                if (metadata.score) metaText.push(`Confianza: ${(metadata.score * 100).toFixed(1)}%`);
                if (metadata.topic) metaText.push(`Tema: ${metadata.topic}`);
                if (metadata.difficulty) metaText.push(`Dificultad: ${metadata.difficulty}`);
                metaDiv.textContent = metaText.join(' • ');
                messageDiv.appendChild(metaDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }

        function addRelatedOptions(relatedItems) {
            if (!relatedItems || relatedItems.length === 0) return;
            
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot';
            
            const optionsDiv = document.createElement('div');
            optionsDiv.className = 'related-options';
            
            const titleDiv = document.createElement('div');
            titleDiv.className = 'related-title';
            titleDiv.innerHTML = '🔍 ¿Te refieres a alguna de estas opciones?';
            optionsDiv.appendChild(titleDiv);
            
            relatedItems.forEach((item, index) => {
                const optionDiv = document.createElement('div');
                optionDiv.className = 'option-item';
                
                const questionText = document.createElement('span');
                questionText.textContent = item.q || item.question || 'Opción ' + (index + 1);
                optionDiv.appendChild(questionText);
                
                // Badge con información adicional
                if (item.topic || item.difficulty) {
                    const badge = document.createElement('span');
                    badge.className = 'option-badge';
                    badge.textContent = item.topic || item.difficulty || '';
                    optionDiv.appendChild(badge);
                }
                
                // Hacer clickeable
                optionDiv.onclick = () => {
                    messageInput.value = item.q || item.question || '';
                    sendMessage();
                };
                
                optionsDiv.appendChild(optionDiv);
            });
            
            messageDiv.appendChild(optionsDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // Agregar mensaje del usuario
            await addMessage(message, true);
            messageInput.value = '';
            
            // Deshabilitar input y botón
            messageInput.disabled = true;
            sendBtn.disabled = true;
            loading.style.display = 'block';

            try {
                const formData = new FormData();
                formData.append('mensaje', message);

                const response = await fetch('chat.php', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (response.ok) {
                    // Mostrar respuesta principal con efecto typewriter
                    const answer = data.answer || data.response || 'No se encontró respuesta';
                    const metadata = {
                        score: data.score,
                        topic: data.topic,
                        difficulty: data.difficulty
                    };
                    await addMessage(answer, false, metadata);
                    
                    // Mostrar opciones relacionadas si existen
                    if (data.related && Array.isArray(data.related) && data.related.length > 0) {
                        addRelatedOptions(data.related);
                    }
                } else {
                    await addMessage('❌ Error: ' + (data.error || 'No se pudo procesar la solicitud'));
                }
            } catch (error) {
                await addMessage('❌ Error de conexión: ' + error.message);
            } finally {
                // Habilitar input y botón
                messageInput.disabled = false;
                sendBtn.disabled = false;
                loading.style.display = 'none';
                messageInput.focus();
            }
        }
    </script>
</body>
</html>
