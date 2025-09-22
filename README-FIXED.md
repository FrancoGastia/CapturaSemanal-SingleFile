# 📸 Captura Semanal Automatizada

Sistema **100% automatizado** para capturar páginas web semanalmente usando **GitHub Actions** y **SingleFile CLI**.

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-blue?logo=github-actions)](https://github.com/features/actions)
[![SingleFile CLI](https://img.shields.io/badge/SingleFile-CLI-green?logo=npm)](https://www.npmjs.com/package/single-file-cli)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Características Principales

- ✅ **Completamente automático** - Se ejecuta cada lunes sin intervención
- ✅ **GitHub Actions gratis** - 2000 minutos mensuales incluidos  
- ✅ **SingleFile CLI** - Capturas completas con CSS, JS, imágenes
- ✅ **Historial organizado** - Capturas guardadas por semanas
- ✅ **Reportes automáticos** - Estadísticas detalladas de cada ejecución
- ✅ **Descarga fácil** - Archivos ZIP disponibles por 30 días
- ✅ **Sin mantenimiento** - Funciona completamente solo
- ✅ **Acceso mundial** - Desde cualquier lugar con internet

## 📊 Último Reporte

<!-- REPORTE_INICIO -->
*El reporte se actualizará automáticamente después de cada captura semanal*

Para ver el primer reporte, ejecuta manualmente el workflow desde la pestaña Actions.

🚀 **Estado**: Listo para primera ejecución  
📅 **Próxima captura automática**: Próximo lunes 9:00 AM UTC  
🔧 **Configuración**: Edita `config/urls.json` con tus URLs
<!-- REPORTE_FIN -->

## ⚙️ Configuración Inicial

### 1️⃣ Fork o clona este repositorio

```bash
git clone https://github.com/TU_USUARIO/captura-semanal.git
cd captura-semanal
```

### 2️⃣ Configura tus URLs a capturar

Edita el archivo `config/urls.json`:

```json
{
  "urls": {
    "mi_sitio_principal": "https://mi-sitio.com",
    "competidor_1": "https://competidor1.com", 
    "landing_productos": "https://mi-empresa.com/productos",
    "blog_corporativo": "https://mi-empresa.com/blog",
    "portal_noticias": "https://noticias-industria.com"
  }
}
```

**💡 Consejos para URLs:**
- Usa nombres descriptivos sin espacios
- Máximo recomendado: 30-50 URLs
- Solo URLs públicamente accesibles
- Evita sitios que requieran login

### 3️⃣ Activa GitHub Actions

1. Ve a la pestaña **Actions** en tu repositorio
2. Si está deshabilitado, click **"I understand my workflows, go ahead and enable them"**
3. El sistema se ejecutará automáticamente cada lunes a las 9:00 AM UTC

### 4️⃣ (Opcional) Ejecuta primera captura manualmente

1. **Actions** → **📸 Captura Semanal Automatizada**
2. Click **"Run workflow"**
3. Selecciona opciones si deseas:
   - Número de capturas simultáneas (1-3)
4. Click **"Run workflow"**
5. ¡Espera 3-8 minutos y revisa los resultados!

## 🏃‍♂️ Uso Diario

### Ejecución Automática
- **Cuándo**: Cada lunes a las 9:00 AM UTC (6:00 AM Argentina)
- **Duración**: 3-8 minutos típicamente
- **Resultado**: ZIP descargable + reportes actualizados

### Ejecución Manual
Cuando necesites capturas inmediatas:
1. **Actions** → **Workflow** → **"Run workflow"**
2. Selecciona configuraciones opcionales
3. Los resultados estarán listos en minutos

### Monitoreo
- **Logs en vivo**: Ve el progreso en tiempo real en Actions
- **Notificaciones**: GitHub te avisa por email si algo falla
- **Historial**: Todas las ejecuciones quedan registradas

## 📁 Estructura de Resultados

```
📦 Capturas Organizadas Automáticamente
├── 📁 capturas/
│   ├── 📁 latest/                    # 👈 Siempre la captura más reciente
│   │   ├── 📄 report.json           # Estadísticas detalladas JSON
│   │   └── 📄 summary.md            # Resumen legible en Markdown
│   ├── 📁 semana_2024-01-15/        # Capturas por semana
│   │   ├── 📄 mi_sitio.html         # Página completa con CSS/JS/imágenes
│   │   ├── 📄 competidor.html       # Cada URL = 1 archivo HTML
│   │   ├── 📄 landing.html
│   │   ├── 📄 report.json           # Reporte de esta semana específica
│   │   └── 📄 summary.md            # Resumen de esta semana
│   └── 📁 semana_2024-01-22/
│       └── ... (próximas capturas)
```

## 📦 Descarga de Capturas

### 🥇 Método Recomendado: GitHub Artifacts

1. **Actions** → Click en la ejecución más reciente exitosa
2. Scroll hasta **"Artifacts"** 
3. Descarga `capturas-XXX.zip` (contiene todos los HTML)
4. Descomprime y abre archivos HTML en tu navegador

### 📊 Solo Reportes: Directamente en GitHub

- `capturas/latest/summary.md` - Resumen de última captura
- `capturas/latest/report.json` - Estadísticas completas
- Accesibles directamente desde el repositorio

## ⚙️ Configuración Avanzada

### 🕐 Cambiar Horario de Ejecución

Edita `.github/workflows/weekly-capture.yml`:

```yaml
schedule:
  # Formato: minuto hora día_semana
  - cron: '0 15 * * 3'  # Miércoles 3:00 PM UTC
  - cron: '30 9 * * 1'  # Lunes 9:30 AM UTC  
  - cron: '0 6 * * 5'   # Viernes 6:00 AM UTC
```

### ⚡ Ajustar Rendimiento

**Para sitios lentos:**
- Ejecución manual → Seleccionar 1 worker
- Reduce número de URLs simultáneas

**Para sitios rápidos:**
- Ejecución manual → Seleccionar 3 workers
- Máxima velocidad de captura

### 🔧 Personalizar Opciones de Captura

Edita `scripts/capture.py` para modificar:

```python
# Tiempo de espera para contenido dinámico
'--wait-for', '5000',  # 5 segundos (default: 3000)

# Tamaño máximo por recurso  
'--max-resource-size', '50',  # 50MB (default: 25MB)

# Timeout total por página
timeout=120  # 2 minutos (default: 90s)
```

## 🔧 Solución de Problemas

### ❌ "Config file not found"
```bash
# Verifica que config/urls.json existe y es JSON válido
cat config/urls.json | python -m json.tool
```

### ❌ "SingleFile CLI failed"
- **Causa común**: URL inaccesible o bloquea bots
- **Solución**: Revisa logs específicos en GitHub Actions
- **Verificación**: Abre la URL manualmente en navegador

### ❌ Capturas muy pequeñas (< 2KB)
- **Causa**: Página requiere JavaScript o está bloqueada  
- **Solución**: Aumentar `--wait-for` en `scripts/capture.py`
- **Alternativa**: Verificar que la URL sea la correcta

### ❌ "README.md no existe" o marcadores faltantes
- **Causa**: README.md no tiene los marcadores necesarios
- **Solución**: Asegúrate de que README.md contiene:
  ```html
  <!-- REPORTE_INICIO -->
  <!-- REPORTE_FIN -->
  ```

## 💡 Consejos y Mejores Prácticas

### 🎯 **Optimización de URLs**
- **Agrupa por importancia**: URLs críticas vs. monitoreo general
- **Evita redirects**: Usa URLs finales directamente
- **Prefiere HTTPS**: Mejor compatibilidad y seguridad
- **Testa individualmente**: Verifica cada URL manualmente primero

### ⚡ **Optimización de Rendimiento**
- **Menos es más**: Empieza con 10-15 URLs y ve agregando
- **Monitorea tiempos**: Si supera 10 minutos, reduce carga
- **Usa workers inteligentemente**: 1 para sitios lentos, 3 para rápidos
- **Revisa regularmente**: Elimina URLs que ya no necesites

## 📊 Límites y Costos

| Recurso | Límite Gratuito | Notas |
|---------|----------------|-------|
| **GitHub Actions** | 2000 min/mes | Suficiente para 300+ capturas |
| **Almacenamiento** | 500MB artifacts | Se renuevan cada 30 días |
| **Repositorio** | Ilimitado | Para reportes JSON/MD |
| **Tiempo por job** | 6 horas | Más que suficiente |
| **Jobs simultáneos** | 20 | Un workflow usa 1 job |

**💰 Costo estimado para 30 URLs semanales:** **¡GRATIS!**

## 🤝 Contribuir al Proyecto

### 🛠️ **Cómo Contribuir**
1. Fork el repositorio
2. Crea una rama: `git checkout -b mi-mejora-increible`
3. Commit cambios: `git commit -m "Agrega funcionalidad X"`
4. Push: `git push origin mi-mejora-increible`
5. Crea un Pull Request

### 🐛 **Reportar Bugs**
1. Ve a **Issues** → **New Issue**
2. Usa la plantilla de bug report
3. Incluye logs de GitHub Actions si es relevante
4. Describe pasos para reproducir

## 📝 Licencia

MIT License - Úsalo libremente para proyectos personales y comerciales.

---

## ⭐ ¿Te Resulta Útil?

Si este proyecto te ayuda en tu trabajo:

1. ⭐ **Dale una estrella** al repositorio
2. 🔄 **Compártelo** con tu equipo
3. 🐛 **Reporta bugs** para mejorarlo
4. 💡 **Sugiere mejoras** en Issues
5. 🤝 **Contribuye** con código

---

<div align="center">

**🐙 Creado con GitHub Actions** • **📸 Powered by SingleFile CLI** • **🤖 100% Automatizado**

Made with ❤️ for the web monitoring community

</div>
