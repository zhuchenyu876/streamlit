#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
import csv
import os
from datetime import datetime
import random

def get_tire_database():
    """获取轮胎数据库"""
    return [
        # 185/65R15 规格
        {"id": "LL-C30210", "name": "185 65 15 COMPASAL BLAZER HP 88H", "price": 1142, "stock": 8},
        {"id": "LL-C29885", "name": "185 65 R15 92H XL BLACKHAWK HH11 AUTO", "price": 1156, "stock": 1},
        {"id": "CCCC2342", "name": "185/65 R15 88H ANSU OPTECO A1", "price": 1192, "stock": 1},
        {"id": "C79647", "name": "185 65 R15 SAFERICH FRC16 88H", "price": 1294, "stock": 1},
        {"id": "C000231", "name": "185 65 R15 GOODYEAR ASSURANCE 88T", "price": 1906, "stock": 1},
        {"id": "CCCC1836", "name": "185 65 R15 JK TYRE VECTRA 92T", "price": 2030, "stock": 6},
        
        # 195/65R15 规格
        {"id": "LL-C40211", "name": "195 65 15 COMPASAL BLAZER HP 91H", "price": 1245, "stock": 5},
        {"id": "LL-C39886", "name": "195 65 R15 95H XL BLACKHAWK HH11 AUTO", "price": 1289, "stock": 2},
        {"id": "CCCC2343", "name": "195/65 R15 91H ANSU OPTECO A1", "price": 1356, "stock": 3},
        {"id": "C79648", "name": "195 65 R15 SAFERICH FRC16 91H", "price": 1445, "stock": 2},
        
        # 205/55R16 规格
        {"id": "LL-C50212", "name": "205 55 16 COMPASAL BLAZER HP 94H", "price": 1567, "stock": 4},
        {"id": "LL-C49887", "name": "205 55 R16 94H XL BLACKHAWK HH11 AUTO", "price": 1623, "stock": 1},
        {"id": "CCCC2344", "name": "205/55 R16 94H ANSU OPTECO A1", "price": 1689, "stock": 2},
        {"id": "C79649", "name": "205 55 R16 SAFERICH FRC16 94H", "price": 1789, "stock": 1},
        
        # 215/60R16 规格
        {"id": "LL-C60213", "name": "215 60 16 COMPASAL BLAZER HP 95H", "price": 1678, "stock": 3},
        {"id": "LL-C59888", "name": "215 60 R16 95H XL BLACKHAWK HH11 AUTO", "price": 1734, "stock": 2},
        {"id": "CCCC2345", "name": "215/60 R16 95H ANSU OPTECO A1", "price": 1823, "stock": 1},
        
        # 175/70R14 规格
        {"id": "LL-C20215", "name": "175 70 14 COMPASAL BLAZER HP 84H", "price": 967, "stock": 6},
        {"id": "LL-C19890", "name": "175 70 R14 84H XL BLACKHAWK HH11 AUTO", "price": 1023, "stock": 3},
        
        # 165/70R13 规格
        {"id": "LL-C10216", "name": "165 70 13 COMPASAL BLAZER HP 79H", "price": 856, "stock": 4},
        {"id": "LL-C09891", "name": "165 70 R13 79H XL BLACKHAWK HH11 AUTO", "price": 912, "stock": 2},
    ]

def get_products_by_spec(tire_products, spec):
    """根据规格获取产品"""
    matching_products = []
    for product in tire_products:
        if spec.replace('/', ' ').replace('R', ' ') in product['name'].replace('/', ' ').replace('R', ' '):
            matching_products.append(product)
    return matching_products

def generate_product_table_json(products):
    """生成标准的产品表格JSON回复"""
    # 生成markdown表格
    markdown_table = "| ID Producto | Nombre del Producto | Stock | Precio |\\n"
    markdown_table += "|:------------|:--------------------|:------|:-------|\\n"
    
    for product in products:
        markdown_table += f"| {product['id']} | {product['name']} | {product['stock']} | ${product['price']} |\\n"
    
    # 生成描述
    if products:
        min_price = min(p['price'] for p in products)
        max_price = max(p['price'] for p in products)
        spec = products[0]['name'].split()[:3]  # 提取规格
        spec_str = f"{spec[0]}/{spec[1]}R{spec[2]}"
        
        desc = f"🔍 Resultados de búsqueda para neumáticos {spec_str}\\n\\n📊 Encontrados: {len(products)} productos\\n💰 Rango de precios: ${min_price} - ${max_price}\\n\\n¿Cuál modelo le interesa?"
    else:
        desc = "Lo siento, no se encontraron neumáticos que coincidan con su búsqueda."
    
    # 生成JSON
    response_data = {
        "type": "markdown",
        "data": markdown_table,
        "desc": desc
    }
    
    return json.dumps(response_data, ensure_ascii=False)

def create_accurate_spanish_qa():
    """创建符合prompt规范的西班牙语QA数据，包含多轮对话"""
    
    tire_products = get_tire_database()
    
    # 西班牙语列头
    spanish_headers = [
        '#', 'Pregunta', 'Fuente de Respuesta', 'Fuente de Pregunta', 
        'Satisfactorio', 'Número de Serie', 'Contenido de Pregunta', 'Respuesta de Referencia'
    ]
    
    # 轮胎规格列表
    tire_specs = [
        "185/65R15", "195/65R15", "205/55R16", "215/60R16", "175/70R14", "165/70R13"
    ]
    
    # 车型数据
    car_models = [
        {"brand": "Toyota", "model": "Corolla", "year": "2020"},
        {"brand": "Honda", "model": "Civic", "year": "2021"},
        {"brand": "Nissan", "model": "Sentra", "year": "2019"},
        {"brand": "Chevrolet", "model": "Aveo", "year": "2020"},
        {"brand": "Hyundai", "model": "Accent", "year": "2021"},
        {"brand": "Kia", "model": "Rio", "year": "2020"},
        {"brand": "Mazda", "model": "3", "year": "2021"},
        {"brand": "Volkswagen", "model": "Jetta", "year": "2020"},
        {"brand": "Ford", "model": "Focus", "year": "2019"},
        {"brand": "Suzuki", "model": "Swift", "year": "2020"},
    ]
    
    # 品牌列表
    tire_brands = ["COMPASAL", "BLACKHAWK", "ANSU OPTECO", "SAFERICH", "GOODYEAR", "JK TYRE"]
    
    data_rows = []
    current_row = 1
    
    # 第一类：多轮对话 - 问候 + 三参数查询（15个对话会话，30行）
    print("生成多轮对话场景...")
    for session_id in range(1, 16):
        # 第一轮：问候
        greetings = [
            "¡Hola! Buenos días",
            "Buenas tardes",
            "Hola, ¿cómo están?",
            "Buenos días, necesito ayuda",
            "Hola, ¿me pueden atender?",
            "Buenas, quisiera información",
            "¡Hola! ¿Están abiertos?",
            "Buenos días, vengo por llantas"
        ]
        
        greeting_responses = [
            "¡Hola! Bienvenido a Llantasyservicios.mx (Grupo Magno). ¿En qué puedo ayudarle hoy?",
            "¡Buenos días! Soy su asistente de ventas de Grupo Magno. ¿Cómo puedo asistirle?",
            "¡Hola! Me da mucho gusto atenderle. ¿Qué necesita hoy?",
            "¡Buenos días! Estamos aquí para ayudarle con sus neumáticos. ¿Qué busca?",
            "¡Hola! Claro que sí, estamos para servirle. ¿En qué le ayudo?",
            "¡Buenas tardes! Por supuesto, ¿qué información necesita?",
            "¡Hola! Sí, estamos abiertos y listos para atenderle. ¿Qué necesita?",
            "¡Buenos días! Perfecto, ¿qué tipo de llantas está buscando?"
        ]
        
        greeting = random.choice(greetings)
        greeting_response = random.choice(greeting_responses)
        
        row1 = [
            current_row,
            "Saludo inicial",
            "Respuesta cortés",
            "Cliente",
            "Satisfactorio",
            session_id,
            greeting,
            greeting_response
        ]
        data_rows.append(row1)
        current_row += 1
        
        # 第二轮：三参数查询
        spec = random.choice(tire_specs)
        products = get_products_by_spec(tire_products, spec)
        
        follow_up_questions = [
            f"Necesito llantas {spec}",
            f"Busco neumáticos {spec}",
            f"¿Tienen {spec}?",
            f"Quiero ver precios de {spec}",
            f"Me interesan las {spec}",
        ]
        
        question = random.choice(follow_up_questions)
        answer = generate_product_table_json(products)
        
        row2 = [
            current_row,
            "Consulta tres parámetros",
            "Plugin búsqueda neumáticos",
            "Cliente",
            "Satisfactorio",
            session_id,  # 使用相同的session_id表示同一对话
            question,
            answer
        ]
        data_rows.append(row2)
        current_row += 1
    
    # 第二类：多轮对话 - 车型咨询 + 确认参数（10个对话会话，20行）
    print("生成车型咨询多轮对话...")
    for session_id in range(16, 26):
        # 第一轮：车型咨询
        car = random.choice(car_models)
        question1 = f"¿Qué llantas necesita mi {car['brand']} {car['model']} {car['year']}?"
        
        # 根据车型推荐规格
        if car['model'] in ['Corolla', 'Civic', 'Sentra', 'Aveo', 'Accent', 'Rio']:
            recommended = "185/65R15"
        elif car['model'] in ['3', 'Jetta', 'Focus']:
            recommended = "205/55R16"
        else:
            recommended = "175/70R14"
        
        answer1 = f"Para su {car['brand']} {car['model']} {car['year']}, la especificación más común es {recommended}. Para confirmar y mostrarle opciones disponibles, ¿podría verificar los tres parámetros en el lateral de su llanta actual?"
        
        row1 = [
            current_row,
            "Consulta vehículo",
            "Recomendación con confirmación",
            "Cliente",
            "Satisfactorio",
            session_id,
            question1,
            answer1
        ]
        data_rows.append(row1)
        current_row += 1
        
        # 第二轮：确认参数并查询
        question2 = f"Sí, confirmo que es {recommended}"
        products = get_products_by_spec(tire_products, recommended)
        answer2 = generate_product_table_json(products)
        
        row2 = [
            current_row,
            "Confirmación parámetros",
            "Plugin búsqueda neumáticos", 
            "Cliente",
            "Satisfactorio",
            session_id,
            question2,
            answer2
        ]
        data_rows.append(row2)
        current_row += 1
    
    # 第三类：送货和到店购买场景（10个）
    print("生成送货和到店购买场景...")
    delivery_scenarios = [
        # 送货相关
        ("¿Hacen entregas a domicilio?", "Sí, ofrecemos servicio de entrega a domicilio: gratis en CDMX y Estado de México. Otras zonas por paquetería con costo al cliente. Si son más de 100 llantas fuera de la ciudad, el envío es gratuito."),
        ("¿Cuánto cobran por envío?", "En CDMX y Estado de México la entrega es gratuita. Para otras zonas el costo varía según la paquetería. ¿A qué ciudad necesita el envío?"),
        ("¿Envían a Guadalajara?", "Sí, enviamos a Guadalajara por paquetería. El costo es por cuenta del cliente, excepto si compra más de 100 llantas que sería envío gratuito."),
        ("¿Puedo recoger en tienda?", "Por supuesto, puede recoger en nuestra tienda en Calz de las Armas 591, CDMX. Horarios: lunes a viernes 9:00-18:00, sábados 9:00-15:00."),
        ("¿Dónde están ubicados?", "Estamos en Calz de las Armas 591, Azcapotzalco, CDMX. Horarios: lunes a viernes 9:00-18:00, sábados 9:00-15:00."),
        
        # 到店购买相关
        ("¿Puedo ir a comprar directamente?", "¡Por supuesto! Puede venir directamente a nuestra tienda. Tendremos ofertas adicionales disponibles en compra presencial."),
        ("¿Qué horarios manejan?", "Atendemos lunes a viernes de 9:00 a 18:00 horas y sábados de 9:00 a 15:00 horas. Descansamos domingos."),
        ("¿Tienen estacionamiento?", "Sí, contamos con área de estacionamiento para la comodidad de nuestros clientes."),
        ("¿Instalan ahí mismo?", "Sí, instalamos en el momento. El servicio incluye desmontaje, montaje, balanceo y válvula nueva. Toma aproximadamente 30 minutos."),
        ("¿Necesito cita para la instalación?", "Es recomendable hacer cita previa para garantizar disponibilidad inmediata, aunque también atendemos sin cita según disponibilidad."),
    ]
    
    for i, (question, answer) in enumerate(delivery_scenarios):
        session_id = 26 + i
        row = [
            current_row,
            "Consulta entrega/tienda",
            "Información logística",
            "Cliente",
            "Satisfactorio",
            session_id,
            question,
            answer
        ]
        data_rows.append(row)
        current_row += 1
    
    # 第四类：单轮完整三参数查询（15个）
    print("生成单轮三参数查询...")
    for i in range(15):
        spec = random.choice(tire_specs)
        products = get_products_by_spec(tire_products, spec)
        
        question_variations = [
            f"Necesito llantas {spec}",
            f"¿Tienen disponible {spec}?",
            f"¿Cuánto cuestan las {spec}?",
            f"Precio de {spec}",
            f"Me interesan las {spec}",
        ]
        
        question = random.choice(question_variations)
        answer = generate_product_table_json(products)
        session_id = 36 + i
        
        row = [
            current_row,
            "Consulta tres parámetros",
            "Plugin búsqueda neumáticos",
            "Cliente",
            "Satisfactorio",
            session_id,
            question,
            answer
        ]
        data_rows.append(row)
        current_row += 1
    
    # 第五类：引导类场景（20个）
    print("生成引导类场景...")
    # 部分参数查询
    partial_params = ["185", "195", "205", "65", "55", "R15", "R16"]
    for i in range(10):
        param = random.choice(partial_params)
        session_id = 51 + i
        
        if param.startswith('R'):
            question = f"Busco llantas {param}"
            answer = f"Para encontrar las mejores opciones en {param}, necesito que me proporcione el ancho y el perfil. Por ejemplo: 185/65{param}. ¿Podría darme la especificación completa?"
        elif param.isdigit() and len(param) <= 2:
            question = f"Necesito llantas aro {param}"
            answer = f"Para neumáticos aro {param}, necesito el ancho y perfil completos. ¿Podría proporcionarme los tres parámetros: ancho, perfil y diámetro del aro?"
        else:
            question = f"Busco llantas {param}"
            answer = f"Veo que necesita neumáticos de {param}mm de ancho. Para completar la búsqueda, necesito el perfil y diámetro del aro. ¿Podría proporcionarme la especificación completa?"
        
        row = [
            current_row,
            "Consulta parámetros incompletos",
            "Guía al cliente",
            "Cliente",
            "Satisfactorio",
            session_id,
            question,
            answer
        ]
        data_rows.append(row)
        current_row += 1
    
    # 品牌咨询
    for i in range(10):
        brand = random.choice(tire_brands)
        session_id = 61 + i
        
        question_variations = [
            f"¿Qué opciones tienen de {brand}?",
            f"Busco llantas {brand}",
            f"¿Tienen neumáticos {brand}?",
            f"Me interesan las {brand}",
        ]
        
        question = random.choice(question_variations)
        answer = f"Tenemos excelentes opciones de {brand}. Para mostrarle los modelos disponibles y precios exactos, necesito que me proporcione los tres parámetros de su llanta: ancho, perfil y diámetro del aro. ¿Podría verificar esta información?"
        
        row = [
            current_row,
            "Consulta marca",
            "Guía al cliente",
            "Cliente",
            "Satisfactorio",
            session_id,
            question,
            answer
        ]
        data_rows.append(row)
        current_row += 1
    
    # 第六类：服务相关咨询（21个）
    print("生成服务咨询...")
    service_qa = [
        ("¿Hacen instalación?", "Sí, incluimos instalación profesional, válvula nueva y balanceo."),
        ("¿Aceptan tarjetas?", "Sí, todas las tarjetas excepto American Express. Meses sin intereses disponibles."),
        ("¿Dan garantía?", "12 meses contra defectos de fábrica. Desgaste normal no incluido."),
        ("¿Reparan llantas?", "Sí, reparación $150 pesos. Si hay daño lateral no se puede reparar."),
        ("¿Tienen descuentos?", "Ofertas adicionales disponibles en compra presencial en tienda."),
        ("¿Cuánto tarda la instalación?", "Aproximadamente 30 minutos por vehículo con cita previa."),
        ("¿Puedo apartar una llanta?", "Sí, con el 50% de anticipo. Disponible por 15 días."),
        ("¿Cómo pago a meses?", "3 meses sin intereses con tarjetas participantes."),
        ("¿Qué incluye el precio?", "Llanta + instalación + válvula + balanceo + inflado con nitrógeno."),
        ("¿Atienden sábados?", "Sí, sábados de 9:00 a 15:00 horas."),
        ("¿Dan factura?", "Sí, facturación disponible con RFC. Se envía por correo."),
        ("¿Hay técnicos certificados?", "Sí, todo nuestro personal está capacitado y certificado."),
        ("¿Revisan la llanta usada?", "Sí, revisamos y damos diagnóstico gratuito del estado."),
        ("¿Balancean con pesas?", "Usamos pesas de clip y adhesivas según tipo de rin."),
        ("¿Calibran la presión?", "Sí, verificamos y ajustamos presión según especificaciones."),
        ("¿Rotan las llantas?", "Sí, servicio de rotación disponible. Recomendado cada 10,000 km."),
        ("¿Tienen promociones?", "Promociones especiales en tienda. Consulte al llegar."),
        ("¿Trabajan domingos?", "No, descansamos domingos. Lunes a sábado únicamente."),
        ("¿Aceptan American Express?", "No, aceptamos todas las tarjetas excepto American Express."),
        ("¿Cuánto dura la garantía?", "12 meses contra defectos de fabricación. No cubre desgaste normal."),
        ("¿Qué marcas manejan?", "Manejamos COMPASAL, BLACKHAWK, ANSU OPTECO, SAFERICH, GOODYEAR, JK TYRE y más."),
    ]
    
    for i, (question, answer) in enumerate(service_qa):
        session_id = 71 + i
        row = [
            current_row,
            "Consulta servicios",
            "Información general",
            "Cliente",
            "Satisfactorio",
            session_id,
            question,
            answer
        ]
        data_rows.append(row)
        current_row += 1
    
    # 保存为CSV文件
    output_filename = "轮胎测试数据_西班牙语_多轮对话_完整版本.csv"
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(spanish_headers)
        writer.writerows(data_rows)
    
    print(f"✅ 成功创建完整的西班牙语测试数据: {output_filename}")
    print(f"📊 总共生成了 {len(data_rows)} 行数据")
    print(f"🎯 问题分布:")
    print(f"  - 多轮对话（问候+查询）: 15个会话，30行")
    print(f"  - 多轮对话（车型+确认）: 10个会话，20行") 
    print(f"  - 送货/到店购买场景: 10个")
    print(f"  - 单轮三参数查询: 15个")
    print(f"  - 引导类场景: 20个")
    print(f"  - 服务咨询: 21个")
    print(f"🔧 包含多轮对话测试，适合测试agent的会话连续性和准确性")
    
    return output_filename

# 执行脚本
if __name__ == "__main__":
    create_accurate_spanish_qa() 