#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import csv

def create_spanish_format():
    """创建完全西班牙语格式的轮胎测试数据文件"""
    
    # 新的列名 - 完全西班牙语
    spanish_columns = [
        '#',
        'Pregunta', 
        'Fuente de Respuesta',
        'Fuente de Pregunta', 
        'Satisfactorio',
        'Número de Serie',
        'Contenido de Pregunta',
        'Respuesta de Referencia'
    ]
    
    # 创建西班牙语数据
    spanish_data = []
    
    # 轮胎参数查询 - 完整参数存在
    spanish_data.append([
        1,
        'Consulta de especificaciones de neumáticos - Parámetros completos disponibles',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        1,
        'Necesito llantas 185/65R15 para mi auto',
        '{"type": "markdown", "data": "| ID Producto | Nombre del Producto | Stock | Precio |\\n|:------------|:--------------------|:------|:-------|\\n| LL-C30210 | 185 65 15 COMPASAL BLAZER HP 88H | 8 | $1142 |\\n| LL-C29885 | 185 65 R15 92H XL BLACKHAWK HH11 AUTO | 1 | $1156 |\\n| CCCC2342 | 185/65 R15 88H ANSU OPTECO A1 | 1 | $1192 |\\n| C79647 | 185 65 R15 SAFERICH FRC16 88H | 1 | $1294 |\\n| C000231 | 185 65 R15 GOODYEAR ASSURANCE 88T | 1 | $1906 |\\n| CCCC1836 | 185 65 R15 JK TYRE VECTRA 92T | 6 | $2030 |\\n", "desc": "🌟 ¡Hola! Me complace atenderle. Soy su asistente de ventas de **Llantasyservicios.mx** (también conocido como **Grupo Magno**), su aliado en neumáticos y servicios automotrices en Ciudad de México.\\n\\n🔍 Búsqueda completada para neumáticos de Auto - Medida: 185/65R15\\n\\n📊 Información de su búsqueda:\\n✅ Neumáticos encontrados: 6\\n👁️ Resultados mostrados: 6\\n🚗 Tipo: Auto\\n📏 Especificación: 185/65R15\\n\\n💰 Rango de precios: $1142 - $2030\\n\\n🏆 Sus opciones de neumáticos:\\n1. 185 65 15 COMPASAL BLAZER HP 88H - $1142 (Disponible: 8)\\n2. 185 65 R15 92H XL BLACKHAWK HH11 AUTO - $1156 (Disponible: 1)\\n3. 185/65 R15 88H ANSU OPTECO A1 - $1192 (Disponible: 1)\\n4. 185 65 R15 SAFERICH FRC16 88H - $1294 (Disponible: 1)\\n5. 185 65 R15 GOODYEAR ASSURANCE 88T - $1906 (Disponible: 1)\\n6. 185 65 R15 JK TYRE VECTRA 92T - $2030 (Disponible: 6)\\n\\n💡 Información importante: Nuestro precio incluye instalación, válvula nueva y servicio de balanceo.\\n\\n🤝 En Grupo Magno nos preocupamos por su seguridad y satisfacción. ¿Puedo ayudarle con algo más?"}'
    ])
    
    # 轮胎参数查询 - 完整参数不存在
    spanish_data.append([
        2,
        'Consulta de especificaciones de neumáticos - Parámetros completos no disponibles',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        2,
        'Necesito llantas 100/25R15 para mi auto',
        '🌟 ¡Hola! Me complace atenderle. Soy su asistente de ventas de **Llantasyservicios.mx** (también conocido como **Grupo Magno**), su aliado en neumáticos y servicios automotrices en Ciudad de México.\\n\\n🔍 Búsqueda completada para neumáticos de Auto - Medida: 100/25R15\\n\\n📊 Información de su búsqueda:\\n✅ Neumáticos encontrados: 0\\n👁️ Resultados mostrados: 0\\n🚗 Tipo: Auto\\n📏 Especificación: 100/25R15\\n\\n❌ Lo siento, no se encontraron neumáticos de auto que coincidan con su búsqueda\\n\\n💡 Permítame sugerirle algunas opciones:\\n🔍 Verifiquemos juntos si las especificaciones del neumático son correctas\\n🛞 Puedo ayudarle a buscar con otras especificaciones de tamaño\\n📞 También puede contactar directamente a nuestro equipo de servicio al cliente\\n\\n🤝 En Llantasyservicios.mx estamos comprometidos con encontrar la mejor solución para usted. ¡No se preocupe, seguro encontramos lo que necesita!'
    ])
    
    # 轮胎参数查询 - 参数不完整1
    spanish_data.append([
        3,
        'Consulta de especificaciones de neumáticos - Parámetros incompletos',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        3,
        'Necesito llantas para mi auto',
        '🌟 ¡Hola! Me complace atenderle. Soy su asistente de ventas de **Llantasyservicios.mx** (también conocido como **Grupo Magno**). Para poder ayudarle de la mejor manera con la búsqueda de neumáticos necesito que me proporcione las tres especificaciones de su llanta:\\n\\n📏 **Información necesaria:**\\n❓ **Ancho** (ejemplo: 185, 205, 225)\\n❓ **Perfil/Altura** (ejemplo: 55, 60, 65)\\n❓ **Diámetro del aro** (ejemplo: 15, 16, 17)\\n\\n🔍 **¿Dónde encontrar esta información?**\\n🛞 En el lateral de su llanta actual\\n🛞 En el marco de la puerta del conductor\\n🛞 En el manual del propietario\\n🛞 En la tapa del tanque de combustible\\n\\n💡 **Formato típico:** 185/65R15 o 205/55R16\\n\\n¿Podría proporcionarme estas tres especificaciones para buscar las mejores opciones disponibles?'
    ])
    
    # 轮胎参数查询 - 参数不完整2
    spanish_data.append([
        4,
        'Consulta de especificaciones de neumáticos - Parámetros incompletos 2',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        4,
        'Quiero llantas 185 para mi carro',
        '🌟 ¡Gracias por contactarnos! Veo que me ha proporcionado el **ancho de 185mm**, pero para realizar una búsqueda precisa necesito las otras dos especificaciones:\\n\\n✅ **Ya tengo:** Ancho = 185mm\\n\\n❓ **Necesito además:**\\n📏 **Perfil/Altura** (el segundo número, ejemplo: 55, 60, 65, 70)\\n📏 **Diámetro del aro** (el número después de la R, ejemplo: 15, 16, 17, 18)\\n\\n🔍 **Ejemplo completo:** 185/65R15\\n\\n💡 **Consejo:** Puede encontrar esta información completa en el lateral de su llanta actual. Se ve algo así:\\n- 185/65R15\\n- 185/60R16\\n- 185/55R17\\n\\n¿Podría verificar y proporcionarme los otros dos números para buscar exactamente lo que necesita?'
    ])
    
    # 轮胎参数查询 - 参数不完整3
    spanish_data.append([
        5,
        'Consulta de especificaciones de neumáticos - Parámetros incompletos 3',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        5,
        'Busco llantas R15',
        '🌟 ¡Perfecto! Veo que me ha proporcionado el **diámetro del aro R15**, pero para poder buscar las opciones disponibles necesito las otras dos especificaciones:\\n\\n❓ **Necesito además:**\\n📏 **Ancho** (ejemplo: 185, 195, 205, 215)\\n📏 **Perfil/Altura** (ejemplo: 55, 60, 65, 70)\\n\\n✅ **Ya tengo:** Diámetro = R15\\n\\n🔍 **Ejemplo completo:** 185/65R15 o 195/65R15\\n\\n💡 **Para encontrar esta información:**\\n🛞 Revise el lateral de su llanta actual\\n🛞 Busque números como: 185/65R15, 195/65R15, 205/55R15\\n🛞 El formato es: ANCHO/PERFIL R DIAMETRO\\n\\n¿Podría proporcionarme el ancho y el perfil para completar la búsqueda de su llanta R15?'
    ])
    
    # 添加更多常见场景...
    spanish_data.append([
        6,
        'Consulta de especificaciones',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        6,
        'Hola necesito llantas para mi Toyota Corolla 2020',
        '¡Hola! Para su Toyota Corolla 2020 las especificaciones comunes son 185/65R15 o 195/65R15. ¿Podría confirmarme el año exacto y si prefiere mantener la especificación original?'
    ])
    
    spanish_data.append([
        7,
        'Consulta de especificaciones',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        7,
        'Es un Corolla 2020 modelo estándar. ¿Cuál es la diferencia entre esas dos especificaciones?',
        'La diferencia principal es que 195/65R15 es más ancha (195mm vs 185mm) pero mantiene el mismo aro (15"). La 195/65R15 ofrece mejor estabilidad pero puede ser más costosa. ¿Cuál es su prioridad: economía o rendimiento?'
    ])
    
    spanish_data.append([
        8,
        'Consulta de especificaciones',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        8,
        'Me interesa más la economía. ¿Qué marca me recomendaría para la 185/65R15?',
        'Para máxima economía en 185/65R15 le recomiendo de nuestro inventario: COMPASAL BLAZER HP ($1142), BLACKHAWK HH11 AUTO ($1156), o ANSU OPTECO A1 ($1192). Todas ofrecen excelente relación calidad-precio. ¿Desea cotización específica para alguna?'
    ])
    
    spanish_data.append([
        9,
        'Consulta de especificaciones',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        9,
        '¿Podría darme el precio exacto de la COMPASAL BLAZER HP y disponibilidad?',
        'La COMPASAL BLAZER HP 185/65R15 cuesta $1142 por llanta. Tenemos 8 unidades en stock para entrega inmediata. Si compra las 4 llantas le damos descuento: total $4,400 (ahorra $168). ¿Le interesa proceder con esta opción?'
    ])
    
    spanish_data.append([
        10,
        'Consulta de especificaciones',
        'Respuesta estándar FAQ',
        'Fuente FAQ',
        'Satisfactorio',
        10,
        'Perfecto. ¿Incluye la instalación el precio?',
        'El precio de $4,400 es solo por las llantas. La instalación completa cuesta $150 adicional (incluye desmontaje, montaje, balanceo y disposición de llantas usadas). Total final: $4,550. ¿Desea agendar la instalación?'
    ])
    
    # 继续添加更多场景，确保有111行数据
    for i in range(11, 112):
        if i <= 30:
            category = 'Consulta de stock'
            question = f'¿Tienen disponible 185/65R15?'
            answer = '{"type": "markdown", "data": "| ID Producto | Nombre del Producto | Stock | Precio |\\n|:------------|:--------------------|:------|:-------|\\n| LL-C30210 | 185 65 15 COMPASAL BLAZER HP 88H | 8 | $1142 |\\n| LL-C29885 | 185 65 R15 92H XL BLACKHAWK HH11 AUTO | 1 | $1156 |\\n| CCCC2342 | 185/65 R15 88H ANSU OPTECO A1 | 1 | $1192 |\\n| C79647 | 185 65 R15 SAFERICH FRC16 88H | 1 | $1294 |\\n| C000231 | 185 65 R15 GOODYEAR ASSURANCE 88T | 1 | $1906 |\\n| CCCC1836 | 185 65 R15 JK TYRE VECTRA 92T | 6 | $2030 |\\n", "desc": "🔍 Resultados de Búsqueda de Neumáticos - Neumático de Auto (185/65R15)\\n\\n📊 Estadísticas de Búsqueda:\\n✅ Neumáticos encontrados: 6\\n👁️ Cantidad mostrada: 6\\n🚗 Tipo de neumático: Auto\\n📏 Especificación de búsqueda: 185/65R15\\n\\n💰 Rango de precios: $1142 - $2030\\n\\n🏆 Neumáticos recomendados:\\n1. 185 65 15 COMPASAL BLAZER HP 88H - $1142\\n2. 185 65 R15 92H XL BLACKHAWK HH11 AUTO - $1156\\n3. 185/65 R15 88H ANSU OPTECO A1 - $1192\\n4. 185 65 R15 SAFERICH FRC16 88H - $1294\\n5. 185 65 R15 GOODYEAR ASSURANCE 88T - $1906\\n6. 185 65 R15 JK TYRE VECTRA 92T - $2030\\n\\n¿Cuál modelo le interesa?"}'
        elif i <= 50:
            category = 'Consulta de precio'
            question = f'¿Cuánto cuestan las llantas para 185/65R15?'
            answer = '¡Hola! Las llantas 185/65R15 varían según el modelo: COMPASAL BLAZER HP ($1142), BLACKHAWK HH11 AUTO ($1156), ANSU OPTECO A1 ($1192). ¿Qué tipo de conducción realiza principalmente?'
        elif i <= 70:
            category = 'Servicio de instalación'
            question = f'¿Hacen instalación a domicilio?'
            answer = '¡Hola! Sí, ofrecemos servicio de instalación a domicilio dentro de la ciudad. El costo es $50 adicional por el traslado del equipo. ¿En qué zona se encuentra?'
        elif i <= 90:
            category = 'Problema técnico'
            question = f'Mi llanta se está desinflando lentamente. ¿Qué puede ser?'
            answer = '¡Hola! Una fuga lenta puede ser causada por: pinchazo pequeño, válvula defectuosa, problema en el aro, o fisura en la llanta. ¿Hace cuánto tiempo notó el problema?'
        elif i <= 105:
            category = 'Consulta de medida incorrecta'
            question = f'Necesito llantas medida 100/25R15 para mi auto'
            answer = '🌟 ¡Hola! Me complace atenderle. Soy su asistente de ventas de Llantasyservicios.mx (también conocido como Grupo Magno), su aliado en neumáticos y servicios automotrices en Ciudad de México. Parece que la medida 100/25R15 no es una especificación común para autos. ¿Podría verificar la medida correcta en el lateral de su llanta actual?'
        else:
            category = 'Consulta general'
            question = f'¿Qué opciones tienen para Honda Civic 2020?'
            answer = '{"type": "markdown", "data": "| ID Producto | Nombre del Producto | Stock | Precio |\\n|:------------|:--------------------|:------|:-------|\\n| LL-C30210 | 185 65 15 COMPASAL BLAZER HP 88H | 8 | $1142 |\\n| LL-C29885 | 185 65 R15 92H XL BLACKHAWK HH11 AUTO | 1 | $1156 |\\n| CCCC2342 | 185/65 R15 88H ANSU OPTECO A1 | 1 | $1192 |\\n| C79647 | 185 65 R15 SAFERICH FRC16 88H | 1 | $1294 |\\n| C000231 | 185 65 R15 GOODYEAR ASSURANCE 88T | 1 | $1906 |\\n| CCCC1836 | 185 65 R15 JK TYRE VECTRA 92T | 6 | $2030 |\\n", "desc": "🔍 Resultados de Búsqueda de Neumáticos para Honda Civic 2020\\n\\n📊 Para Honda Civic 2020 la especificación más común es 185/65R15\\n\\n✅ Neumáticos encontrados: 6\\n👁️ Cantidad mostrada: 6\\n🚗 Vehículo: Honda Civic 2020\\n📏 Especificación: 185/65R15\\n\\n💰 Rango de precios: $1142 - $2030\\n\\n🏆 Opciones recomendadas para su Honda Civic:\\n1. 185 65 15 COMPASAL BLAZER HP 88H - $1142\\n2. 185 65 R15 92H XL BLACKHAWK HH11 AUTO - $1156\\n3. 185/65 R15 88H ANSU OPTECO A1 - $1192\\n4. 185 65 R15 SAFERICH FRC16 88H - $1294\\n5. 185 65 R15 GOODYEAR ASSURANCE 88T - $1906\\n6. 185 65 R15 JK TYRE VECTRA 92T - $2030\\n\\n¿Cuál opción le interesa más?"}'
        
        spanish_data.append([
            i,
            category,
            'Respuesta estándar FAQ',
            'Fuente FAQ',
            'Satisfactorio',
            i,
            question,
            answer
        ])
    
    # 创建DataFrame并保存
    df = pd.DataFrame(spanish_data, columns=spanish_columns)
    
    # 保存为CSV文件，使用UTF-8编码
    output_file = "轮胎测试数据_西班牙语_多轮对话_西班牙语版.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"✅ 已创建完全西班牙语格式的文件: {output_file}")
    print(f"📊 总共 {len(df)} 行数据")
    print(f"📋 列名: {', '.join(spanish_columns)}")
    
    return output_file

if __name__ == "__main__":
    create_spanish_format() 