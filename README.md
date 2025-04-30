# ChatTDP

**ChatTDP** es una aplicación Flutter diseñada para ayudar a árbitros de la Tercera División Profesional a generar informes de incidencias de partido de forma rápida y estructurada. Utiliza la API de OpenAI para crear un asistente conversacional que recepciona datos de juego y devuelve bloques de texto listos para incluirse en el informe arbitral.

---

## 📋 Características

- **Asistente conversacional** impulsado por OpenAI GPT: genera descripciones de incidencias (faltas, tarjetas, goles, cambios, etc.).  
- **Interfaz limpia y sencilla**: formulario de entrada + chat.  
- **Arquitectura MVVM**: separación de lógica (viewmodel), servicios de API y UI.  
- **Configuración flexible**: gestiona tu propia API Key de OpenAI.  
- **Multi-plataforma**: Android, iOS, Web y Desktop.  

---

## 🚀 Requisitos

- **Flutter** 3.x o superior  
- **Dart** 2.17 o superior  
- **Cuenta y API Key** de OpenAI  
- **Conexión a internet**  

---

## 🔧 Instalación

1. **Clona el repositorio**  
   ```bash
   git clone https://github.com/rickyma18/ChatTDP.git
   cd ChatTDP
Instala dependencias

bash
flutter pub get
Configura tu API Key

Renombra el fichero de ejemplo:

mv lib/services/.env.example lib/services/.env
Abre lib/services/.env y añade:

ini
OPENAI_API_KEY=tu_api_key_aquí
Genera código Firebase (opcional)

flutterfire configure
▶️ Uso
flutter run
Ingresa un texto breve en la caja de chat, por ejemplo:

“tarjeta amarilla al 23’ por derribo, Penales: Leones 4-5 Chapala”

Pulsa Enviar.

Copia la descripción generada por OpenAI y pégala en tu informe arbitral.

📂 Estructura de Carpetas
  lib/
  ├── model/
  ├── services/
  │   └── openai_service.dart
  ├── view/
  │   └── chat_page.dart
  ├── viewmodel/
  │   └── chat_viewmodel.dart
  ├── firebase_options.dart
  └── main.dart
  └── theme.dart
  
🤝 Contribuciones
¡Bienvenidas! Si encuentras errores o quieres añadir mejoras:

  
Haz un fork del proyecto.

Crea una rama feature/descripcion-cambios.

Envía tu pull request describiendo tu aporte.

📄 Licencia
Este proyecto es de código abierto bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

<img src="https://github.com/user-attachments/assets/6a8b9d26-ec98-493c-a9fb-487989fefec5" alt="Imagen 1" width="300" />  
<img src="https://github.com/user-attachments/assets/9f2843ff-f0b0-4aef-8d46-3c617481e77e" alt="Imagen 2" width="300" />  
<img src="https://github.com/user-attachments/assets/dc407f9b-e625-4f75-b18d-285a5b66b4c0" alt="Imagen 3" width="300" />

