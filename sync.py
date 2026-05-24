#!/usr/bin/env python3
import os
import subprocess
import time
import sys

# Mapeo de contenedores y directorios locales a vigilar
WATCH_DIRS = {
    "kowa-backend": "./backend",
    "kowa-frontend": "./frontend"
}

# Patrones para ignorar durante el escaneo
IGNORE_PATTERNS = [
    "node_modules",
    ".git",
    "dist",
    "tmp",
    "bin",
    "__pycache__",
    ".idea",
    ".vscode",
    ".env",
    "go-build-cache",
    ".dockerignore",
    "sync.py"
]

def should_ignore(path):
    parts = path.split(os.sep)
    for pattern in IGNORE_PATTERNS:
        if pattern in parts:
            return True
    return False

def scan_files(directory):
    files_map = {}
    for root, dirs, files in os.walk(directory):
        # Pruning de directorios para optimizar os.walk
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        
        for file in files:
            full_path = os.path.join(root, file)
            if should_ignore(full_path):
                continue
            try:
                mtime = os.stat(full_path).st_mtime
                files_map[full_path] = mtime
            except OSError:
                pass
    return files_map

def sync_file(container, local_path, watch_dir):
    # Calcular la ruta relativa e interna del contenedor
    rel_path = os.path.relpath(local_path, watch_dir)
    container_path = f"/app/{rel_path}"
    container_dir = os.path.dirname(container_path)
    
    try:
        # Asegurarse de que el directorio padre existe dentro del contenedor
        subprocess.run(
            ["docker", "exec", container, "mkdir", "-p", container_dir],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # Copiar el archivo al contenedor
        subprocess.run(
            ["docker", "cp", local_path, f"{container}:{container_path}"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"\033[92m[SYNC]\033[0m Sincronizado {local_path} -> {container}:{container_path}")
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[ERROR]\033[0m Fallo al sincronizar {local_path} con {container}: {e}")

def main():
    print("\033[96m====================================================\033[0m")
    print("\033[96m     KowaMusicStream - Dev File Sync Engine         \033[0m")
    print("\033[96m====================================================\033[0m")
    
    # Comprobar si los contenedores están activos
    started_any = False
    for container in WATCH_DIRS.keys():
        res = subprocess.run(
            ["docker", "ps", "-q", "-f", f"name={container}"],
            capture_output=True, text=True
        )
        if not res.stdout.strip():
            print(f"\033[93m[AVISO]\033[0m El contenedor '{container}' no está activo. Iniciando stack...")
            subprocess.run(["docker", "compose", "up", "-d", "--build"], check=True)
            started_any = True
            break
            
    if not started_any:
        print("\033[92m[OK]\033[0m Todos los contenedores ya están corriendo.")

    print("\033[92m[INIT]\033[0m Escaneando directorios locales...")
    baselines = {}
    for container, directory in WATCH_DIRS.items():
        baselines[container] = scan_files(directory)
        print(f"       Monitoreando {len(baselines[container])} archivos en '{directory}' para '{container}'")
        
    print("\033[92m[LISTO]\033[0m Vigilando cambios en tiempo real. Presiona Ctrl+C para detener.")
    
    try:
        while True:
            time.sleep(0.5)
            for container, directory in WATCH_DIRS.items():
                current = scan_files(directory)
                old = baselines[container]
                
                # Buscar archivos modificados o nuevos
                for path, mtime in current.items():
                    if path not in old or mtime > old[path]:
                        sync_file(container, path, directory)
                        
                baselines[container] = current
    except KeyboardInterrupt:
        print("\n\033[96m[SALIDA]\033[0m Sincronizador dev apagado.")

if __name__ == "__main__":
    main()
