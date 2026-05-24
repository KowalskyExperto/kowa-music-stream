# KowaMusicStream: Personal Music Streaming Platform

Este archivo es la **Guía Global del Proyecto** y sirve como el punto de partida y contexto centralizado para todos los agentes de IA y desarrolladores que trabajen en este repositorio.

---

## 1. Visión General del Proyecto
**KowaMusicStream** es una plataforma personal de streaming de música (estilo Spotify/Apple Music) diseñada para alojar, transcodificar y transmitir una biblioteca musical privada de forma altamente eficiente, segura y escalable en la nube (AWS), optimizando costos mediante una arquitectura Serverless en su primera fase.

### Tecnologías Core
*   **Backend:** Go (Golang) con arquitectura limpia (Clean Architecture).
*   **Frontend:** React + Vite (Single Page Application) para un reproductor persistente y fluido.
*   **Base de Datos:** DynamoDB (Single Table Design).
*   **Almacenamiento y CDN:** AWS S3 (Bucket de música original y web optimizada) + AWS CloudFront (CDN).
*   **Seguridad:** Autenticación JWT en la API y **Cookies Firmadas de CloudFront** para el streaming continuo sin expiraciones por pausa.
*   **Transcodificación:** AWS Lambda (Python + FFmpeg) activada por eventos de S3.

---

## 2. Estructura del Monorepo
El repositorio está organizado en las siguientes carpetas principales:
```bash
kowa-music-stream/
├── README.md               # Este documento (Idea global y especificaciones)
├── implementation_plan.md  # Checklist de tareas y roadmap de desarrollo
├── architecture_blueprint.md# Detalles del diseño cloud de AWS y esquema de base de datos
├── /backend/               # Código fuente del API en Go
├── /frontend/              # Código fuente del cliente en React (Vite)
└── /infra/                 # Código de Infraestructura como Código (AWS CDK en Python)
```

---

## 3. Guía de Trabajo para Agentes Dedicados

Este repositorio está diseñado para ser desarrollado por agentes de IA especializados que cooperan de forma independiente.

### 🎨 Agente de Frontend
*   **Directorio de trabajo:** `/frontend/`
*   **Misión:** Construir la interfaz de usuario web responsiva, moderna (glassmorphism) y fluida.
*   **Responsabilidades Clave:**
    *   Implementar la pantalla de Login conectándose a `/backend` para recibir el JWT y configurar automáticamente las Cookies de CloudFront en el navegador.
    *   Crear el **Reproductor de Audio Persistente** que reproduzca los streams directo desde CloudFront (`https://media.kowamusicstream.com/...`).
    *   Desarrollar el módulo de subidas directas a S3 utilizando las **S3 Presigned URLs** (PUT request) obtenidas desde el backend de Go, evitando saturar la API con archivos binarios.
    *   Gestionar el estado global de reproducción (Zustand/Context API) y cola de música.

### 🌐 Agente de Backend
*   **Directorio de trabajo:** `/backend/`
*   **Misión:** Desarrollar una API RESTful en Go, extremadamente veloz, escalable y con altos estándares de seguridad.
*   **Responsabilidades Clave:**
    *   Implementar autenticación local por correo/contraseña y generación de JWT de sesión.
    *   Implementar el endpoint para generar cabeceras de **CloudFront Signed Cookies** para autorizar al navegador por 12-24 horas.
    *   Conectarse y operar con la base de datos **DynamoDB** (local en Docker y remota en AWS).
    *   Generar **S3 Presigned URLs** de escritura (PUT) y exponer endpoints para la gestión de playlists, catálogo e ingestión de metadatos.

---

## 4. Especificación para el Agente de Docker (Desarrollo Local)

*Nota para el Agente de Docker: No debes generar el archivo `docker-compose.yml` en esta interacción; será creado por un agente especialista dedicado a contenedores. Sin embargo, debes seguir estrictamente los siguientes lineamientos de diseño:*

### Requerimiento del Ecosistema Docker Local
Para garantizar un entorno de desarrollo idéntico al de producción, el archivo `docker-compose.yml` en la raíz del proyecto debe levantar un ecosistema compuesto por **tres contenedores principales** interconectados en una red bridge propia:

1.  **Contenedor del Backend (`kowa-backend`):**
    *   **Tecnología:** Imagen de Go (preferiblemente usando `air` para hot-reload de código).
    *   **Puerto expuesto:** Por ejemplo, `8080:8080`.
    *   **Variables de Entorno:** Conexión a DynamoDB apuntando al contenedor de la base de datos en lugar de AWS, y almacenamiento local simulado en disco en lugar de S3.
    *   **Dependencia:** Debe esperar a que el contenedor de base de datos esté listo (`depends_on`).

2.  **Contenedor del Frontend (`kowa-frontend`):**
    *   **Tecnología:** Node.js (corriendo el servidor de desarrollo de Vite con soporte para Hot Module Replacement).
    *   **Puerto expuesto:** Por ejemplo, `5173:5173`.
    *   **Configuración:** Debe apuntar las llamadas de API al puerto del contenedor `kowa-backend` (o usar el proxy de Vite para evitar problemas de CORS en local).

3.  **Contenedor de Base de Datos Local (`kowa-db`):**
    *   **Tecnología:** Imagen oficial `amazon/dynamodb-local`.
    *   **Puerto expuesto:** `8000:8000`.
    *   **Persistencia:** Debe usar un volumen de Docker para que los datos de prueba (canciones creadas localmente, usuarios y playlists) no se pierdan al apagar el contenedor.

### Red y Volumes
*   **Network:** Crear una red de puente llamada `kowa-network` para comunicación directa entre contenedores.
*   **Volumes:** Mapear un volumen para la data persistente de DynamoDB Local y un volumen de montura local (`bind mount`) para la carga de música de desarrollo local en el backend.
