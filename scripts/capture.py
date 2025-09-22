#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Captura semanal automatizada para GitHub Actions
Optimizado para ejecutarse en Ubuntu con SingleFile CLI
"""

import os
import json
import subprocess
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time
import concurrent.futures
from urllib.parse import urlparse

class GitHubCapture:
    def __init__(self, base_folder="capturas"):
        self.base_folder = Path(base_folder)
        self.setup_logging()
        self.setup_folders()
        
    def setup_logging(self):
        """Configurar logging para GitHub Actions"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_folders(self):
        """Crear estructura de carpetas"""
        self.base_folder.mkdir(exist_ok=True)
        (self.base_folder / "latest").mkdir(exist_ok=True)
        
        # Carpeta para la semana actual
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_name = f"semana_{week_start.strftime('%Y-%m-%d')}"
        self.week_folder = self.base_folder / week_name
        self.week_folder.mkdir(exist_ok=True)
        
        self.logger.info(f"📁 Carpeta de la semana: {self.week_folder}")
        
    def load_urls_config(self):
        """Cargar URLs desde archivo de configuración"""
        config_file = Path("config/urls.json")
        
        if not config_file.exists():
            self.logger.error(f"❌ Archivo de configuración no encontrado: {config_file}")
            return {}
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            urls = config.get('urls', {})
            self.logger.info(f"📋 URLs cargadas: {len(urls)}")
            
            # Mostrar primeras 3 URLs como muestra
            for i, (name, url) in enumerate(list(urls.items())[:3]):
                self.logger.info(f"   {i+1}. {name}: {url}")
            
            if len(urls) > 3:
                self.logger.info(f"   ... y {len(urls) - 3} URLs más")
                
            return urls
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Error en formato JSON: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"❌ Error leyendo configuración: {e}")
            return {}
            
    def sanitize_filename(self, url, custom_name=None):
        """Crear nombre de archivo válido para GitHub"""
        if custom_name:
            # Limpiar nombre personalizado
            filename = "".join(c for c in custom_name if c.isalnum() or c in (' ', '-', '_'))
            filename = filename.replace(' ', '_').strip('_')
        else:
            # Generar desde URL
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            path = parsed.path.replace('/', '_').strip('_')
            filename = f"{domain}_{path}" if path else domain
            
        # Limpiar caracteres problemáticos
        filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_'))
        
        # Limitar longitud y asegurar que no esté vacío
        filename = filename[:80] if filename else "sitio_sin_nombre"
        
        return filename
        
    def capture_single_page(self, url, filename):
        """Capturar una sola página usando SingleFile CLI en GitHub Actions"""
        try:
            output_path = self.week_folder / f"{filename}.html"
            
            # Comando optimizado para GitHub Actions (Ubuntu)
            cmd = [
                'single-file',
                url,
                str(output_path),
                '--browser-executable-path', '/usr/bin/google-chrome',
                '--browser-args', '--no-sandbox --disable-dev-shm-usage --headless --disable-gpu --disable-extensions',
                '--wait-for', '3000',  # Esperar 3 segundos
                '--load-deferred-images', 'true',
                '--max-resource-size', '25',  # 25MB max por recurso
                '--compress-CSS', 'true',
                '--compress-HTML', 'true',
                '--remove-unused-styles', 'true',
                '--remove-unused-fonts', 'true',
                '--remove-alternative-medias', 'true'
            ]
            
            self.logger.info(f"📥 Capturando: {url}")
            
            # Ejecutar comando con timeout
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=90,  # 90 segundos timeout
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                # Verificar que el archivo se creó correctamente
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    
                    if file_size > 2000:  # Al menos 2KB
                        size_mb = file_size / 1024 / 1024
                        self.logger.info(f"✅ {filename}.html - {size_mb:.2f}MB")
                        return {
                            "status": "success",
                            "filename": filename,
                            "url": url,
                            "size": file_size,
                            "size_mb": round(size_mb, 2)
                        }
                    else:
                        self.logger.warning(f"⚠️ Archivo muy pequeño: {filename} ({file_size} bytes)")
                        return {
                            "status": "error",
                            "filename": filename,
                            "url": url,
                            "error": f"Archivo muy pequeño ({file_size} bytes)"
                        }
                else:
                    self.logger.error(f"❌ Archivo no creado: {filename}")
                    return {
                        "status": "error",
                        "filename": filename,
                        "url": url,
                        "error": "Archivo no fue creado"
                    }
            else:
                # Error en SingleFile
                error_msg = result.stderr.strip() or result.stdout.strip() or "Error desconocido"
                self.logger.error(f"❌ Error en {filename}: {error_msg}")
                return {
                    "status": "error",
                    "filename": filename,
                    "url": url,
                    "error": error_msg[:200]  # Limitar longitud del error
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ Timeout en {filename} (90s)")
            return {
                "status": "error",
                "filename": filename,
                "url": url,
                "error": "Timeout (90 segundos)"
            }
        except Exception as e:
            self.logger.error(f"❌ Excepción en {filename}: {str(e)}")
            return {
                "status": "error",
                "filename": filename,
                "url": url,
                "error": str(e)[:200]
            }
            
    def capture_all_urls(self, max_workers=2):
        """Capturar todas las URLs configuradas"""
        urls_dict = self.load_urls_config()
        
        if not urls_dict:
            self.logger.error("❌ No hay URLs para capturar")
            self.logger.info("💡 Verifica config/urls.json")
            return {"error": "No URLs configuradas"}
            
        self.logger.info(f"🚀 Iniciando captura de {len(urls_dict)} URLs")
        self.logger.info(f"⚙️ Workers simultáneos: {max_workers}")
        
        results = []
        start_time = time.time()
        
        # Preparar trabajos
        jobs = []
        for name, url in urls_dict.items():
            filename = self.sanitize_filename(url, name)
            jobs.append((url, filename))
            
        # Ejecutar capturas en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todos los trabajos
            future_to_job = {
                executor.submit(self.capture_single_page, url, filename): (url, filename)
                for url, filename in jobs
            }
            
            # Procesar resultados conforme van completándose
            for future in concurrent.futures.as_completed(future_to_job):
                url, filename = future_to_job[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"❌ Error en worker para {filename}: {e}")
                    results.append({
                        "status": "error",
                        "filename": filename,
                        "url": url,
                        "error": f"Worker error: {str(e)}"
                    })
        
        elapsed_time = time.time() - start_time
        
        # Generar estadísticas
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        
        self.logger.info(f"⏱️ Tiempo total: {elapsed_time:.1f} segundos")
        self.logger.info(f"✅ Exitosas: {len(successful)}")
        self.logger.info(f"❌ Fallidas: {len(failed)}")
        
        # Generar reportes
        self.generate_reports(results, elapsed_time)
        
        return {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "time": elapsed_time,
            "folder": str(self.week_folder)
        }
        
    def generate_reports(self, results, elapsed_time):
        """Generar reportes detallados"""
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        total_size = sum(r.get('size', 0) for r in successful)
        
        # Reporte JSON completo
        report = {
            "fecha_ejecucion": datetime.now().isoformat(),
            "fecha_semana": str(self.week_folder.name),
            "estadisticas": {
                "total_urls": len(results),
                "exitosas": len(successful),
                "fallidas": len(failed),
                "tiempo_total_segundos": round(elapsed_time, 2),
                "tamaño_total_bytes": total_size,
                "tamaño_total_mb": round(total_size / 1024 / 1024, 2),
                "promedio_mb_por_pagina": round((total_size / len(successful)) / 1024 / 1024, 2) if successful else 0
            },
            "capturas_exitosas": [
                {
                    "filename": r['filename'],
                    "url": r['url'],
                    "size_bytes": r.get('size', 0),
                    "size_mb": r.get('size_mb', 0)
                }
                for r in successful
            ],
            "capturas_fallidas": [
                {
                    "filename": r['filename'],
                    "url": r['url'],
                    "error": r['error']
                }
                for r in failed
            ]
        }
        
        # Guardar reporte JSON en ambas ubicaciones
        for folder in [self.week_folder, self.base_folder / "latest"]:
            report_file = folder / "report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"📄 Reporte JSON: {report_file}")
                
        # Generar resumen en Markdown
        summary_md = self.generate_summary_markdown(report)
        
        # Guardar resumen en ambas ubicaciones
        for folder in [self.week_folder, self.base_folder / "latest"]:
            summary_file = folder / "summary.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_md)
            self.logger.info(f"📄 Resumen MD: {summary_file}")
                
        self.logger.info(f"📊 Reportes generados exitosamente")
        
    def generate_summary_markdown(self, report):
        """Generar resumen en formato Markdown"""
        stats = report['estadisticas']
        
        summary = f"""# 📸 Captura Semanal - {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 📊 Estadísticas Generales

| Métrica | Valor |
|---------|-------|
| 🎯 **Total URLs** | {stats['total_urls']} |
| ✅ **Exitosas** | {stats['exitosas']} |
| ❌ **Fallidas** | {stats['fallidas']} |
| 📈 **Tasa de éxito** | {(stats['exitosas']/stats['total_urls']*100):.1f}% |
| ⏱️ **Tiempo total** | {stats['tiempo_total_segundos']}s |
| 💾 **Tamaño total** | {stats['tamaño_total_mb']} MB |
| 📊 **Promedio por página** | {stats['promedio_mb_por_pagina']} MB |

## ✅ Capturas Exitosas

"""
        
        for capture in report['capturas_exitosas']:
            summary += f"- **{capture['filename']}** - {capture['size_mb']}MB  \n"
            summary += f"  `{capture['url']}`\n\n"
            
        if report['capturas_fallidas']:
            summary += "## ❌ Capturas Fallidas\n\n"
            for failure in report['capturas_fallidas']:
                summary += f"- **{failure['filename']}** - {failure['error']}  \n"
                summary += f"  `{failure['url']}`\n\n"
                
        summary += f"""
---
📅 **Generado**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} UTC  
🤖 **Sistema**: GitHub Actions + SingleFile CLI  
📁 **Carpeta**: `{report['fecha_semana']}`
"""
        
        return summary

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Captura semanal automatizada para GitHub Actions')
    parser.add_argument('--max-workers', type=int, default=2, 
                       help='Número de capturas simultáneas (1-3)')
    args = parser.parse_args()
    
    # Validar argumentos
    if args.max_workers < 1 or args.max_workers > 3:
        print("❌ max-workers debe estar entre 1 y 3")
        exit(1)
    
    print("🚀 CAPTURA SEMANAL - GITHUB ACTIONS")
    print("=" * 40)
    
    try:
        # Crear instancia del capturador
        capturer = GitHubCapture()
        
        # Ejecutar capturas
        result = capturer.capture_all_urls(max_workers=args.max_workers)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            exit(1)
            
        print(f"\n✅ CAPTURA COMPLETADA")
        print(f"📊 Exitosas: {result['successful']}/{result['total']}")
        print(f"⏱️ Tiempo: {result['time']:.1f}s")
        print(f"📁 Carpeta: {result['folder']}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Captura interrumpida por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        exit(1)

if __name__ == "__main__":
    main()
