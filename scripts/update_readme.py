#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actualizador automático de README.md con estadísticas de última captura
Se ejecuta automáticamente después de cada captura en GitHub Actions
"""

import json
import re
from pathlib import Path
from datetime import datetime

def update_readme_with_report():
    """Actualiza README.md con el último reporte de captura"""
    
    print("📝 Actualizando README.md con último reporte...")
    
    # Leer reporte de última captura
    report_file = Path("capturas/latest/report.json")
    if not report_file.exists():
        print("⚠️ No hay reporte disponible para actualizar README")
        print(f"   Archivo esperado: {report_file}")
        return False
        
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo reporte: {e}")
        return False
    
    stats = report.get('estadisticas', {})
    
    # Crear contenido del reporte para README
    reporte_content = f"""
**📅 Última ejecución:** {datetime.now().strftime('%d/%m/%Y %H:%M')} UTC

| Métrica | Valor |
|---------|-------|
| 🎯 **Total URLs** | {stats.get('total_urls', 0)} |
| ✅ **Exitosas** | {stats.get('exitosas', 0)} |
| ❌ **Fallidas** | {stats.get('fallidas', 0)} |
| 📈 **Tasa de éxito** | {(stats.get('exitosas', 0)/max(stats.get('total_urls', 1), 1)*100):.1f}% |
| ⏱️ **Tiempo total** | {stats.get('tiempo_total_segundos', 0)}s |
| 💾 **Tamaño total** | {stats.get('tamaño_total_mb', 0)} MB |
| 📊 **Promedio por página** | {stats.get('promedio_mb_por_pagina', 0)} MB |

🔗 **[Ver reporte completo](capturas/latest/summary.md)** | 📦 **[Descargar capturas](../../actions)**
"""
    
    # Leer README actual
    readme_file = Path("README.md")
    if not readme_file.exists():
        print("❌ README.md no encontrado")
        print("💡 Asegúrate de que el archivo README.md existe en la raíz del repositorio")
        return False
        
    try:
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error leyendo README: {e}")
        return False
    
    # Buscar y reemplazar la sección del reporte
    # Los marcadores deben estar en el README para que funcione
    pattern = r'<!-- REPORTE_INICIO -->.*?<!-- REPORTE_FIN -->'
    replacement = f'<!-- REPORTE_INICIO -->{reporte_content}<!-- REPORTE_FIN -->'
    
    if '<!-- REPORTE_INICIO -->' in content and '<!-- REPORTE_FIN -->' in content:
        # Reemplazar contenido entre marcadores
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        try:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ README.md actualizado con último reporte")
            print(f"   Exitosas: {stats.get('exitosas', 0)}/{stats.get('total_urls', 0)}")
            print(f"   Tiempo: {stats.get('tiempo_total_segundos', 0)}s")
            print(f"   Tamaño: {stats.get('tamaño_total_mb', 0)}MB")
            return True
        except Exception as e:
            print(f"❌ Error escribiendo README: {e}")
            return False
    else:
        print("⚠️ README.md no tiene marcadores de reporte")
        print("💡 Asegúrate de que README.md contiene:")
        print("   <!-- REPORTE_INICIO -->")
        print("   <!-- REPORTE_FIN -->")
        return False

def validate_readme_structure():
    """Validar que README.md tiene la estructura correcta"""
    readme_file = Path("README.md")
    
    if not readme_file.exists():
        print("❌ README.md no existe")
        return False
    
    try:
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error leyendo README: {e}")
        return False
    
    has_start_marker = '<!-- REPORTE_INICIO -->' in content
    has_end_marker = '<!-- REPORTE_FIN -->' in content
    
    print(f"📋 Validación README.md:")
    print(f"   Marcador inicio: {'✅' if has_start_marker else '❌'}")
    print(f"   Marcador fin: {'✅' if has_end_marker else '❌'}")
    
    if has_start_marker and has_end_marker:
        print("✅ README.md tiene estructura correcta")
        return True
    else:
        print("❌ README.md necesita marcadores de reporte")
        return False

def main():
    """Función principal"""
    print("📝 ACTUALIZADOR DE README")
    print("=" * 30)
    
    # Validar estructura
    if not validate_readme_structure():
        print("💡 Agrega estos marcadores a tu README.md:")
        print("   <!-- REPORTE_INICIO -->")
        print("   *El reporte se actualizará automáticamente*")
        print("   <!-- REPORTE_FIN -->")
        return
    
    # Actualizar README
    if update_readme_with_report():
        print("🎉 README.md actualizado exitosamente")
    else:
        print("❌ No se pudo actualizar README.md")

if __name__ == "__main__":
    main()
