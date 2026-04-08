# Metodología de Integración y Control de Versiones (SGI Suite)

Este documento define el flujo de trabajo estándar para el versionado y la publicación de código en el repositorio GitHub de **SGI Suite**. 

El objetivo principal es mantener un "Árbol de Git" (Git Tree) completamente limpio, lineal, ordenado y con la menor cantidad de envíos (pushes) "basura" o intermedios en la rama principal (`main`).

---

## 🛑 Regla de Oro
**NUNCA realizar commits ni desarrollar directamente en la rama `main`.**
La rama `main` es sagrada: solo recibe bloques de trabajo 100% terminados, unificados y funcionales.

---

## 🔄 El Flujo de Trabajo: "Code, Squash & Merge"

Para cualquier funcionalidad (Ej: Módulo de Facturación, arreglar un botón, rediseñar el Dashboard), los pasos obligatorios son:

### PASO 1: Crear una rama aislada (Feature Branch)
Asegúrate de estar en `main` y con el código actualizado, luego crea una rama nueva para trabajar.
```bash
git checkout main
git pull origin main
git checkout -b feat/lo-que-voy-a-hacer  # Ej: feat/modulo-pdf
```

### PASO 2: Desarrollo libre (Commits locales)
En esta rama, eres libre de guardar cambios tantas veces como quieras. No importa si los mensajes están mal escritos o si el código se rompe a la mitad. Estos son tus puntos de guardado locales.
```bash
git add .
git commit -m "wip: iniciando validaciones"
# ... días después ...
git add .
git commit -m "wip: ahora si funciona"
```

### PASO 3: Unificación y Merge a Main (Squash)
Una vez que has **completado y probado** todo tu bloque de trabajo, vamos a comprimir (squash) todos esos cambios en uno solo y a moverlo a `main`.
```bash
# 1. Regresar a la rama principal
git checkout main

# 2. Traer todos los cambios de tu rama, pero fusionándolos como si estuvieran sin commit
git merge --squash feat/lo-que-voy-a-hacer

# 3. Hacer un ÚNICO commit profesional oficial
git commit -m "feat: [Título del cambio]

[Descripción clara del porqué y qué cambió]

Arquitecto de IA: Sistemas Multi-Agente y Framework de Inteligencia de Enjambre / AI Architect: Multi-Agent Systems & Swarm Intelligence Framework"
```
*(Tip: Usa `feat:` para nuevas características, `fix:` para arreglar errores, `docs:` para documentación).*

### PASO 4: Subir a GitHub
Ahora tienes un único punto súper limpio para subir a GitHub. Si este punto representa una nueva versión, se recomienda etiquetarlo.
```bash
# Opcional: Crear una etiqueta de versión si es relevante
git tag vX.Y.Z 

# Enviar los cambios (y las etiquetas) al repositorio remoto
git push origin main
git push origin main --tags
```

### PASO 5: Limpieza (Opcional pero recomendada)
Borramos la rama local vieja, pues ya está todo el trabajo condensado en `main`.
```bash
git branch -D feat/lo-que-voy-a-hacer
```

---

## 🛠️ Método Alternativo: Web de GitHub (Pull Requests)
Si prefieres un flujo de trabajo más visual, puedes usar la plataforma de GitHub, y resulta mucho más seguro:

1. Trabaja en tu rama `feat/tu-trabajo` como en el Paso 1 y Paso 2.
2. Sube la rama directo a Github: `git push origin feat/tu-trabajo`
3. En la web de GitHub, la página te ofrecerá crear un **Pull Request**.
4. Aprueba el Pull Request usando **obligatoriamente el botón "Squash and Merge"** (aplastar y fusionar). No uses el botón verde normal de "Merge".
5. En tu terminal, actualiza tu sistema descargando la rama maestra limpia: 
   ```bash
   git checkout main
   git pull origin main
   ```

---

## 📌 Control de Versiones Semántico (SemVer)
Al crear los tags (`git tag v1.0.1`), seguir el formato oficial:

*   **v1.X.X (MAJOR)**: Cambios arquitectónicos masivos que requerirían reiniciar la base de datos o que rompen dependencias absolutas con versiones antiguas.
*   **vX.1.X (MINOR)**: Gran cantidad de características, pantallas y nuevas funcionales completas (Entregar todo un módulo como farmacia/facturación agregaría un punto acá).
*   **vX.X.1 (PATCH)**: Solución simple de fallos tipográficos, configuraciones, vistas o parches de pequeños errores en el entorno de producción actual.

---

## ✒️ Estándar de Atribución (Firma)
Todas las contribuciones realizadas por el sistema de IA deberán incluir la siguiente firma informativa al final del mensaje de commit para mantener la transparencia tecnológica sin afectar la autoría principal del usuario:

`Arquitecto de IA: Sistemas Multi-Agente y Framework de Inteligencia de Enjambre / AI Architect: Multi-Agent Systems & Swarm Intelligence Framework`

> **Resumen para IA Assitants:** Al interactuar con este repositorio, se te insta a **revisar este documento** para asegurar que no inflarás el historial de git de `main` con commits excesivos y que empaquetarás de forma atómica y semántica los avances.
