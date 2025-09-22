#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el sistema de captura localmente antes de subir a GitHub
Útil para verificar configuración, URLs y dependencias
"""

import subprocess
import sys
import json
import os
from pathlib import Path

def print_header(title):
    """Imprimir encabezado formateado"""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def check_python():
    """Verificar versión de Python"""
    print("🐍 Verificando Python...")
    version = sys.version.split()[0]
    print(f"✅ Python {version} encontrado")
    return True

def check_singlefile_cli():
    """Verificar que SingleFile CLI está instalado"""
    print("🔍 Verificando SingleFile CLI...")
    
    try:
        result = subprocess.run(['single-file', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ SingleFile CLI encontrado: {version}")
            return True
        else:
            print("❌ SingleFile CLI no responde correctamente")
            return False
    except FileNotFoundError:
        print("❌ SingleFile CLI no está instalado")
        print("💡 Para instalarlo:")
        print("   1. Instala Node.js: https://nodejs.org/")
        print("   2. Ejecuta: npm install -g single-file-cli")
        return False
    except subprocess.TimeoutExpired:
        print("❌ SingleFile CLI no responde (timeout)")
        return False

def check_project_structure():
    """Verificar estructura del proyecto"""
    print("📁 Verificando estructura del proyecto...")
    
    required_files = [
        "scripts/capture.py",
        "scripts/update_readme.py", 
        "config/urls.json"
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - No encontrado")
            all_good = False
    
    return all_good

def check_config():
    """Verificar configuración de URLs"""
    print("📋 Verificando configuración de URLs...")
    
    config_file = Path("config/urls.json")
    
    if not config_file.exists():
        print(f"❌ Archivo de configuración no encontrado: {config_file}")
        print("💡 Crea este archivo con tus URLs")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        urls = config.get('urls', {})
        
        if not urls:
            print("❌ No hay URLs configuradas")
            print("💡 Agrega URLs al archivo config/urls.json")
            return False
        
        print(f"✅ Configuración válida")
        print(f"📊 URLs encontradas: {len(urls)}")
        
        # Mostrar algunas URLs de ejemplo
        print("🔗 URLs configuradas:")
        for i, (name, url) in enumerate(list(urls.items())[:5]):
            print(f"   {i+1}. {name}: {url}")
        
        if len(urls) > 5:
            print(f"   ... y {len(urls) - 5} URLs más")
        
        # Validar formato de URLs
        invalid_urls = []
        for name, url in urls.items():
            if not url.startswith(('http://', 'https://')):
                invalid_urls.append(f"{name}: {url}")
        
        if invalid_urls:
            print("⚠️ URLs con formato inválido encontradas:")
            for invalid in invalid_urls:
                print(f"   • {invalid}")
            return False
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error en formato JSON: {e}")
        print("💡 Verifica que el archivo JSON tenga sintaxis correcta")
        return False
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return False

def run_test_capture():
    """Ejecutar una captura de prueba"""
    print("🧪 Ejecutando prueba de captura...")
    print("⚠️ Esto puede tomar varios minutos dependiendo del número de URLs...")
    print("⚠️ Se ejecutará con 1 worker para minimizar carga")
    
    try:
        # Ejecutar script principal con 1 worker para prueba
        result = subprocess.run([
            sys.executable, "scripts/capture.py", 
            "--max-workers", "1"
        ], timeout=600)  # 10 minutos timeout para prueba
        
        if result.returncode == 0:
            print("✅ Prueba de captura exitosa!")
            return True
        else:
            print("❌ Error en la prueba de captura")
            print("🔍 Revisa los mensajes de error arriba")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout en prueba (10 minutos)")
        print("💡 Puede ser que algunas URLs sean muy lentas")
        return False
    except FileNotFoundError:
        print("❌ No se pudo ejecutar scripts/capture.py")
        print("💡 Verifica que el archivo existe")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando prueba: {e}")
        return False

def show_results():
    """Mostrar resultados de la prueba"""
    print("📊 Verificando resultados de la prueba...")
    
    # Verificar reporte JSON
    report_file = Path("capturas/latest/report.json")
    if report_file.exists():
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            stats = report.get('estadisticas', {})
            print("📈 Estadísticas de la prueba:")
            print(f"   ✅ Exitosas: {stats.get('exitosas', 0)}")
            print(f"   ❌ Fallidas: {stats.get('fallidas', 0)}")
            print(f"   ⏱️ Tiempo: {stats.get('tiempo_total_segundos', 0)}s")
            print(f"   💾 Tamaño: {stats.get('tamaño_total_mb', 0)}MB")
            
            # Mostrar capturas exitosas
            exitosas = report.get('capturas_exitosas', [])
            if exitosas:
                print("\n📄 Archivos generados:")
                for capture in exitosas[:3]:
                    print(f"   • {capture['filename']}.html ({capture.get('size_mb', 0)}MB)")
                if len(exitosas) > 3:
                    print(f"   ... y {len(exitosas) - 3} archivos más")
            
            # Mostrar errores si los hay
            fallidas = report.get('capturas_fallidas', [])
            if fallidas:
                print("\n❌ Errores encontrados:")
                for error in fallidas[:3]:
                    print(f"   • {error['filename']}: {error['error']}")
                if len(fallidas) > 3:
                    print(f"   ... y {len(fallidas) - 3} errores más")
            
        except Exception as e:
            print(f"❌ Error leyendo reporte: {e}")
    else:
        print("❌ No se generó reporte de prueba")
        print("💡 La prueba puede no haber completado correctamente")
    
    # Verificar archivos HTML generados
    capturas_folder = Path("capturas")
    if capturas_folder.exists():
        html_files = list(capturas_folder.glob("**/*.html"))
        if html_files:
            print(f"\n📁 Total archivos HTML generados: {len(html_files)}")
            total_size = sum(f.stat().st_size for f in html_files)
            print(f"💾 Tamaño total: {total_size / 1024 / 1024:.1f}MB")
        else:
            print("⚠️ No se generaron archivos HTML")
    
    # Verificar resumen markdown
    summary_file = Path("capturas/latest/summary.md")
    if summary_file.exists():
        print(f"✅ Resumen generado: {summary_file}")
    else:
        print("⚠️ No se generó archivo de resumen")

def main():
    """Función principal"""
    print_header("PRUEBA LOCAL DEL SISTEMA DE CAPTURA")
    print("Este script verifica que todo esté configurado correctamente")
    print("antes de subir el proyecto a GitHub.\n")
    
    # Lista de verificaciones
    checks = [
        ("Python", check_python),
        ("SingleFile CLI", check_singlefile_cli),
        ("Estructura del proyecto", check_project_structure),
        ("Configuración de URLs", check_config),
    ]
    
    all_passed = True
    
    # Ejecutar verificaciones básicas
    for name, check_func in checks:
        print(f"\n{'─' * 30}")
        if not check_func():
            all_passed = False
    
    print_header("RESUMEN DE VERIFICACIONES")
    
    if not all_passed:
        print("❌ Algunas verificaciones fallaron")
        print("🔧 Corrige los errores antes de continuar")
        print("💡 Una vez corregidos, ejecuta este script nuevamente")
        return
    
    print("✅ Todas las verificaciones básicas pasaron!")
    
    # Preguntar si ejecutar prueba completa
    print("\n" + "=" * 50)
    print("La prueba completa ejecutará una captura real de todas las URLs")
    print("configuradas. Esto puede tomar varios minutos.")
    
    while True:
        response = input("\n¿Ejecutar prueba completa de captura? (y/N): ").lower().strip()
        if response in ['y', 'yes', 'sí', 's']:
            break
        elif response in ['n', 'no', ''] or not response:
            print("\n✅ Verificaciones básicas completadas")
            print("💡 El sistema está listo para ser subido a GitHub")
            print("🚀 Próximo paso: crear repositorio y subir archivos")
            return
        else:
            print("Por favor responde 'y' para sí o 'n' para no")
    
    # Ejecutar prueba completa
    print_header("EJECUTANDO PRUEBA COMPLETA")
    
    if run_test_capture():
        show_results()
        print_header("PRUEBA COMPLETADA EXITOSAMENTE")
        print("🎉 ¡El sistema funciona correctamente!")
        print("✅ Está listo para GitHub Actions")
        print("🚀 Próximos pasos:")
        print("   1. Crear repositorio en GitHub")
        print("   2. Subir todos los archivos")
        print("   3. Activar GitHub Actions")
        print("   4. ¡Disfrutar las capturas automáticas!")
    else:
        print_header("PRUEBA FALLÓ")
        print("❌ La prueba local encontró problemas")
        print("🔍 Revisa los errores mostrados arriba")
        print("🔧 Corrige los problemas y vuelve a ejecutar")
        print("💡 Posibles causas:")
        print("   • URLs inaccesibles")
        print("   • Problemas de conectividad")
        print("   • SingleFile CLI mal configurado")

if __name__ == "__main__":
    main()
