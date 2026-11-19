# Proyecto-INS-600

## Descripción

Repositorio correspondiente al proyecto desarrollado para la asignatura de Ingeniería de Software (INS-600).

## Requisitos

- Python 3.11 instalado.
- Git instalado.
- Visual Studio Code (recomendado).

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/ivasucojayo161inf-afk/Proyecto-INS-600.git
```

### 2. Ingresar a la carpeta del proyecto

```bash
cd Proyecto-INS-600
```

### 3. Crear el entorno virtual

Ejecutar el siguiente comando:

```bash
python -m venv venv
```

Esto creará una carpeta llamada `venv`, donde se instalarán las bibliotecas necesarias para el proyecto.

### 4. Activar el entorno virtual

Si utilizas Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Si aparece un mensaje indicando que la ejecución de scripts está deshabilitada, ejecutar primero:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Después, volver a ejecutar:

```powershell
.\venv\Scripts\Activate.ps1
```

Si utilizas CMD:

```cmd
venv\Scripts\activate.bat
```

**Verificación:** cuando el entorno virtual esté activado, aparecerá `(venv)` al inicio de la línea de comandos.

### 5. Actualizar pip

Con el entorno virtual activado:

```bash
python -m pip install --upgrade pip
```

### 6. Instalar las dependencias

Ejecutar:

```bash
pip install -r requirements.txt
```

Este comando instalará todas las bibliotecas y versiones especificadas en el archivo `requirements.txt`.

## Ejecución

Una vez completada la instalación y con el entorno virtual activado, ejecutar:

```bash
python main.py
```

## Importante

- El entorno virtual debe activarse cada vez que se abra una nueva terminal para trabajar en el proyecto.
- Las dependencias deben instalarse dentro del entorno virtual.
- No se debe eliminar el archivo `requirements.txt`.
- La carpeta `venv` no se encuentra incluida en GitHub, ya que cada usuario debe crear su propio entorno virtual.
- No es necesario subir la carpeta `venv` al repositorio.

## Autoría

**Asignatura:** Ingeniería de Software  
**Código:** INS-600  
**Institución:** Escuela Industrial Superior "Pedro Domingo Murillo"  
**Carrera:** Informática Industrial  
**Ubicación:** La Paz – Bolivia
