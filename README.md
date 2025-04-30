# ChatTDP

**ChatTDP** es una aplicación Flutter diseñada para ayudar a árbitros de la Tercera División Profesional a generar informes de incidencias de partido de forma rápida y estructurada. Utiliza la API de OpenAI para crear un asistente conversacional que recepciona datos de juego y devuelve bloques de texto listos para incluirse en el informe arbitral.

---

## 📋 Características

- **Asistente conversacional** impulsado por OpenAI GPT: genera descripciones de incidencias (faltas, tarjetas, goles, cambios, etc.).
- **Interfaz limpia y sencilla**: formulario de entrada + chat.
- **Modelo MVVM**: separación de lógica (viewmodel), servicios de API y UI.
- **Configuración flexible**: gestiona tu propia API Key de OpenAI.
- **Multi-plataforma**: Android, iOS, Web y Desktop.

---

## 🚀 Requisitos

- Flutter 3.x o superior  
- Dart 2.17 o superior  
- Cuenta y API Key de OpenAI  
- Conexión a internet  

---

## 🔧 Instalación

1. **Clona el repositorio**  
   ```bash
   git clone https://github.com/rickyma18/ChatTDP.git
   cd ChatTDP
   
2. Instala dependencias
   flutter pub get

3. Configura tu API Key

Renombra el archivo

bash
Copiar
Editar
lib/services/.env.example → lib/services/.env
Abre lib/services/.env y añade tu clave:

ini
Copiar
Editar
OPENAI_API_KEY=tu_api_key_aquí

4. Genera código Firebase (si aplica)
Si utilizas Firebase en tu proyecto, asegúrate de:
flutterfire configure

▶️ Uso
Android/iOS/Web


flutter run
Enfoca tu UI en el asistente: ingresa un texto breve (“tarjeta amarilla al 23’ por derribo, Penales: Leones 4 - 5 Chapala”) y presiona enviar.

Recibe la respuesta generada por OpenAI y cópiala en tu informe arbitral.

🗂️ Estructura de carpetas

lib/
├── model/               # Entidades y modelos de datos
├── services/            # Comunicación con OpenAI y API clients
│   └── openai_service.dart
├── view/                # Widgets y pantallas
│   └── chat_page.dart
├── viewmodel/           # Lógica de estado (ChangeNotifier / Provider / Riverpod)
│   └── chat_viewmodel.dart
├── firebase_options.dart# Configuración Firebase (opcional)
├── main.dart            # Punto de entrada
└── theme.dart           # Temas y paleta de colores.

🤝 Contribuciones
¡Bienvenidas! Si encuentras errores o quieres añadir mejoras:

Haz un fork del proyecto.

Crea una rama feature/descripcion-cambios.

Envía tu PR describiendo lo que aportas.

📄 Licencia
Este proyecto es de código abierto bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.
