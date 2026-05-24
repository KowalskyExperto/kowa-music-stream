# Plan de Implementación: App de Streaming de Música Personal

Este documento centraliza los requerimientos funcionales, las decisiones arquitectónicas tomadas y el roadmap de desarrollo para la aplicación. 

## 1. Decisiones Arquitectónicas Aprobadas

| Componente | Decisión Técnica | Detalles |
| :--- | :--- | :--- |
| **Repositorio** | **Monorepo** | Un solo repositorio de GitHub que contiene `/frontend`, `/backend`, e `/infra`. |
| **CI/CD** | **GitHub Actions** | Flujo `local -> dev -> qa -> master`. Pipeline con *Path Filtering* para desplegar Front, Back e IaC de forma independiente. Uso de GitHub Environments para aprobación manual en QA y Prod. |
| **Frontend** | **React + Vite (SPA)** | Single Page Application alojada en S3 + CloudFront. Garantiza que el reproductor de audio no se interrumpa al navegar. |
| **Backend** | **Go (Golang)** | API RESTful rápida y ligera. Implementará un sistema propio de autenticación JWT (basado en email/contraseña) para los 10 usuarios. |
| **Base de Datos** | **DynamoDB** | En local: contenedor `dynamodb-local` vía Docker Compose. En la nube: Tablas de DynamoDB (Serverless). |
| **Almacenamiento** | **Local + AWS S3** | Abstracción en el código (`Storage Interface`). Localmente usará el disco, en AWS usará S3. Se usarán **S3 Presigned URLs** para la subida y **CloudFront Signed Cookies** para la transmisión directa del stream de música, evitando saturar el servidor y eliminando problemas de expiración. |
| **Transcodificación**| **S3 + AWS Lambda** | Los audios en alta calidad (`.flac`, `.wav`) se suben a S3. Un evento dispara una Lambda (con FFmpeg) que genera versiones web optimizadas (`.mp3` o `.m4a`), almacenándolas junto al original para su descarga o streaming. |
| **Infraestructura** | **Manual ➔ AWS CDK (Python)** | La Fase 1 se configurará manualmente en la consola para aprender y validar. Luego, se automatizará usando AWS CDK en Python. |

## 2. Requerimientos Funcionales (Roadmap de Tareas)

A continuación, la lista de tareas dividida en Backend y Frontend para la primera fase (MVP Serverless).

### 🌐 Backend (Go & AWS)
- [ ] **R-BACK-01 (Arquitectura Base):** Estructurar el proyecto en Go (Clean Architecture), configurar router (Gin/Fiber) y cargar variables de entorno (`.env`).
- [ ] **R-BACK-02 (Autenticación JWT & Cookies):** Crear endpoints de registro y login. Generar JWT para la sesión y firmar las **CloudFront Signed Cookies** con expiración de 12-24h para el streaming.
- [ ] **R-BACK-03 (Conexión a DynamoDB):** Implementar el cliente de DynamoDB con AWS SDK for Go v2. Crear esquema base (usuarios, canciones, playlists).
- [ ] **R-BACK-04 (Módulo de Almacenamiento y Subidas):** Crear endpoints que generen **S3 Presigned URLs** de escritura para que el cliente (Frontend) suba las canciones directamente a S3 de forma segura.
- [ ] **R-BACK-05 (Webhook/Sincronización de Metadatos):** Crear un endpoint o mecanismo que, una vez que el archivo se subió a S3, extraiga los metadatos ID3 y los guarde en DynamoDB.
- [ ] **R-BACK-06 (Playlists y Catálogo):** Endpoints CRUD para listar canciones, buscar, crear playlists y agregar/quitar canciones de ellas.
- [ ] **R-BACK-07 (Transcodificación Serverless - Python Lambda):** Escribir una función AWS Lambda en Python (con capa de FFmpeg) que se active con eventos S3 `ObjectCreated`, transcodifique `.flac/.wav` a `.mp3 320kbps`, y suba el resultado a S3.

### 🎨 Frontend (React + Vite)
- [ ] **R-FRONT-01 (Configuración y Estilos):** Inicializar Vite, configurar TailwindCSS (o CSS modules) y el sistema de ruteo cliente (`react-router-dom`).
- [ ] **R-FRONT-02 (Pantalla de Autenticación):** Login y manejo del estado global del usuario (Zustand o Context API) e interceptores Axios para el JWT. Las cookies de CloudFront se guardarán automáticamente en el navegador.
- [ ] **R-FRONT-03 (Reproductor Global Persistente):** Componente anclado en la parte inferior de la pantalla. Debe manejar estado `Playing`, `Paused`, volumen, progreso, y reproducir el audio directamente apuntando al CDN de CloudFront (autorizado por las Cookies).
- [ ] **R-FRONT-04 (Subida de Archivos):** Interfaz para seleccionar archivos locales (Flac, Wav, Mp3), pedir la Presigned URL al backend en Go, y hacer el upload directo a S3 (PUT request).
- [ ] **R-FRONT-05 (Explorador y Buscador):** Vistas responsivas con "glassmorphism" para listar canciones, crear playlists y buscar en el catálogo.

### 🛠️ Infraestructura y DevOps
- [ ] **R-INFRA-01 (Monorepo Setup):** Crear carpetas, `.gitignore` y configurar el workspace.
- [ ] **R-INFRA-02 (Docker Compose Local):** Archivo `docker-compose.yml` que levante el backend de Go y `dynamodb-local` para desarrollo.
- [ ] **R-INFRA-03 (GitHub Actions - Filtros):** Escribir los workflows de CI (Linters y Tests) separados por `paths: frontend/**` y `paths: backend/**`.
- [ ] **R-INFRA-04 (Pase a AWS CDK):** Una vez que el despliegue manual funcione, crear el proyecto CDK en Python para definir la API, S3, DynamoDB, y CloudFront.

## 3. Revisión del Usuario Requerida
El plan está estructurado considerando todas tus directrices. Si estás de acuerdo con las tareas y el roadmap, podemos proceder a inicializar el repositorio y crear la estructura base en el siguiente turno. Puedes dar tu aprobación o comentar si deseas agregar algo más antes de empezar con el código.
