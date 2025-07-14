#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
import csv
import os
from datetime import datetime
import random

def read_tire_database():
    """读取轮胎数据库"""
    # 直接使用默认轮胎数据
    return get_default_tire_data()

def get_default_tire_data():
    """获取默认轮胎数据"""
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
        
        # 225/60R16 规格
        {"id": "LL-C70214", "name": "225 60 16 COMPASAL BLAZER HP 98H", "price": 1789, "stock": 2},
        {"id": "LL-C69889", "name": "225 60 R16 98H XL BLACKHAWK HH11 AUTO", "price": 1856, "stock": 1},
        
        # 175/70R14 规格
        {"id": "LL-C20215", "name": "175 70 14 COMPASAL BLAZER HP 84H", "price": 967, "stock": 6},
        {"id": "LL-C19890", "name": "175 70 R14 84H XL BLACKHAWK HH11 AUTO", "price": 1023, "stock": 3},
        
        # 165/70R13 规格
        {"id": "LL-C10216", "name": "165 70 13 COMPASAL BLAZER HP 79H", "price": 856, "stock": 4},
        {"id": "LL-C09891", "name": "165 70 R13 79H XL BLACKHAWK HH11 AUTO", "price": 912, "stock": 2},
    ]

def extract_tire_specs(tire_name):
    """从轮胎名称中提取规格"""
    import re
    
    # 匹配轮胎规格的正则表达式
    patterns = [
        r'(\d{3})\s*[/]?\s*(\d{2})\s*[/]?\s*R?(\d{2})',  # 185/65R15 或 185 65 15
        r'(\d{3})\s*[/]?\s*(\d{2})\s*[/]?\s*(\d{2})',   # 185/65/15
    ]
    
    for pattern in patterns:
        match = re.search(pattern, tire_name)
        if match:
            width = match.group(1)
            aspect_ratio = match.group(2)
            rim_diameter = match.group(3)
            return f"{width}/{aspect_ratio}R{rim_diameter}"
    
    return None

def create_diverse_spanish_qa():
    """创建多样化的西班牙语QA数据"""
    
    # 读取轮胎数据
    tire_products = read_tire_database()
    
    # 提取不同的轮胎规格
    tire_specs = set()
    for tire in tire_products:
        spec = extract_tire_specs(tire['name'])
        if spec:
            tire_specs.add(spec)
    
    print(f"发现 {len(tire_specs)} 种轮胎规格: {tire_specs}")
    
    # 西班牙语列头
    spanish_headers = [
        '#', 'Pregunta', 'Fuente de Respuesta', 'Fuente de Pregunta', 
        'Satisfactorio', 'Número de Serie', 'Contenido de Pregunta', 'Respuesta de Referencia'
    ]
    
    # 车型数据
    car_models = [
        {"brand": "Toyota", "model": "Corolla", "year": "2020", "specs": ["185/65R15", "195/65R15"]},
        {"brand": "Honda", "model": "Civic", "year": "2021", "specs": ["185/65R15", "195/65R15"]},
        {"brand": "Nissan", "model": "Sentra", "year": "2019", "specs": ["185/65R15", "195/65R15"]},
        {"brand": "Chevrolet", "model": "Aveo", "year": "2020", "specs": ["185/65R15", "175/70R14"]},
        {"brand": "Hyundai", "model": "Accent", "year": "2021", "specs": ["185/65R15", "175/70R14"]},
        {"brand": "Kia", "model": "Rio", "year": "2020", "specs": ["185/65R15", "175/70R14"]},
        {"brand": "Mazda", "model": "3", "year": "2021", "specs": ["205/55R16", "215/60R16"]},
        {"brand": "Volkswagen", "model": "Jetta", "year": "2020", "specs": ["205/55R16", "215/60R16"]},
        {"brand": "Ford", "model": "Focus", "year": "2019", "specs": ["205/55R16", "215/60R16"]},
        {"brand": "Suzuki", "model": "Swift", "year": "2020", "specs": ["175/70R14", "165/70R13"]},
    ]
    
    # 问题类型和模板
    question_types = [
        "especificacion_completa",
        "especificacion_parcial", 
        "consulta_vehiculo",
        "consulta_precio",
        "consulta_stock",
        "consulta_instalacion",
        "problema_tecnico",
        "comparacion_productos",
        "recomendacion_uso",
        "garantia_servicio"
    ]
    
    def generate_product_table_markdown(filtered_products):
        """生成产品表格的markdown格式"""
        markdown_table = "| ID Producto | Nombre del Producto | Stock | Precio |\\n"
        markdown_table += "|:------------|:--------------------|:------|:-------|\\n"
        
        for product in filtered_products:
            markdown_table += f"| {product['id']} | {product['name']} | {product['stock']} | ${product['price']} |\\n"
        
        return markdown_table
    
    def get_products_by_spec(spec):
        """获取指定规格的产品"""
        matching_products = []
        for product in tire_products:
            if spec.replace('/', ' ').replace('R', ' ') in product['name'].replace('/', ' ').replace('R', ' '):
                matching_products.append(product)
        return matching_products
    
    def generate_question_answer_pair(question_type, index, tire_spec=None, car_model=None):
        """生成问题答案对"""
        
        if question_type == "especificacion_completa":
            # 完整规格查询
            spec = tire_spec or random.choice(list(tire_specs))
            products = get_products_by_spec(spec)
            
            question = f"Necesito llantas {spec} para mi auto"
            
            if products:
                table_markdown = generate_product_table_markdown(products)
                response_data = {
                    "type": "markdown", 
                    "data": table_markdown,
                    "desc": f"🔍 Resultados de búsqueda para neumáticos {spec}\\n\\n📊 Encontrados: {len(products)} productos\\n💰 Rango de precios: ${min(p['price'] for p in products)} - ${max(p['price'] for p in products)}\\n\\n¿Cuál modelo le interesa?"
                }
                answer = json.dumps(response_data, ensure_ascii=False)
            else:
                answer = f"Lo siento, no tenemos disponibles neumáticos {spec} en este momento. ¿Puedo ayudarle con otra especificación?"
        
        elif question_type == "especificacion_parcial":
            # 部分规格查询
            specs = ["185", "195", "205", "R15", "R16", "65", "55"]
            partial_spec = random.choice(specs)
            
            if partial_spec.startswith('R'):
                question = f"Busco llantas {partial_spec}"
                answer = f"🌟 Perfecto! Veo que busca neumáticos {partial_spec}. Para encontrar las mejores opciones necesito el ancho y perfil. Por ejemplo: 185/65{partial_spec} o 195/65{partial_spec}. ¿Podría proporcionarme la especificación completa?"
            else:
                question = f"Quiero llantas {partial_spec} para mi carro"
                answer = f"🌟 Gracias por contactarnos! Veo que busca neumáticos de {partial_spec}mm de ancho. Para una búsqueda precisa necesito el perfil y diámetro del aro. ¿Podría verificar la especificación completa en el lateral de su llanta actual?"
        
        elif question_type == "consulta_vehiculo":
            # 车型咨询
            car = car_model or random.choice(car_models)
            question = f"¿Qué llantas necesita un {car['brand']} {car['model']} {car['year']}?"
            
            recommended_specs = car['specs']
            answer = f"Para su {car['brand']} {car['model']} {car['year']} las especificaciones recomendadas son: {', '.join(recommended_specs)}. La especificación original es {recommended_specs[0]}. ¿Prefiere mantener la especificación original o considera una alternativa?"
        
        elif question_type == "consulta_precio":
            # 价格咨询
            spec = tire_spec or random.choice(list(tire_specs))
            products = get_products_by_spec(spec)
            
            question = f"¿Cuánto cuestan las llantas {spec}?"
            
            if products:
                price_range = f"${min(p['price'] for p in products)} - ${max(p['price'] for p in products)}"
                brands = [p['name'].split()[3] for p in products[:3]]  # 获取品牌名
                answer = f"Las llantas {spec} varían según la marca: {', '.join(brands[:2])} desde ${products[0]['price']}, hasta ${products[-1]['price']}. El rango completo es {price_range}. ¿Tiene preferencia por alguna marca específica?"
            else:
                answer = f"Disculpe, no tengo información de precios para {spec} en este momento. ¿Puedo ayudarle con otra especificación?"
        
        elif question_type == "consulta_stock":
            # 库存咨询
            spec = tire_spec or random.choice(list(tire_specs))
            products = get_products_by_spec(spec)
            
            question = f"¿Tienen disponible {spec}?"
            
            if products:
                available_count = sum(1 for p in products if p['stock'] > 0)
                total_stock = sum(p['stock'] for p in products)
                answer = f"Sí, tenemos {available_count} modelos disponibles en {spec} con un total de {total_stock} unidades en stock. Los modelos disponibles incluyen: {', '.join([p['name'].split()[3] for p in products[:3] if p['stock'] > 0])}. ¿Cuál le interesa?"
            else:
                answer = f"En este momento no tenemos {spec} disponible. ¿Puedo sugerirle especificaciones similares?"
        
        elif question_type == "consulta_instalacion":
            # 安装咨询
            services = [
                "instalación a domicilio",
                "servicio de balanceo",
                "alineación",
                "rotación de llantas",
                "reparación de ponchadura"
            ]
            service = random.choice(services)
            
            question = f"¿Ofrecen {service}?"
            
            if service == "instalación a domicilio":
                answer = "Sí, ofrecemos servicio de instalación a domicilio dentro de la zona metropolitana. El costo es $150 adicional e incluye: desmontaje, montaje, balanceo básico y disposición de llantas usadas. ¿En qué zona se encuentra?"
            elif service == "servicio de balanceo":
                answer = "Sí, el balanceo está incluido en todos nuestros servicios de instalación. También ofrecemos balanceo individual por $50 por llanta. El balanceo es esencial para evitar vibraciones y desgaste irregular."
            elif service == "alineación":
                answer = "Sí, ofrecemos servicio de alineación profesional por $300. Se recomienda realizar alineación cada 10,000 km o cuando cambie las llantas. ¿Necesita agendar una cita?"
            elif service == "rotación de llantas":
                answer = "Sí, ofrecemos rotación de llantas por $80. Se recomienda cada 8,000-10,000 km para asegurar desgaste uniforme y maximizar la vida útil de sus neumáticos."
            else:
                answer = "Sí, ofrecemos reparación de ponchaduras por $120. Evaluamos el daño y si es reparable lo solucionamos el mismo día. ¿Puede describirme el tipo de daño?"
        
        elif question_type == "problema_tecnico":
            # 技术问题
            problems = [
                "desgaste irregular",
                "vibración al manejar",
                "ruido excesivo",
                "pérdida de presión",
                "agrietamiento lateral"
            ]
            problem = random.choice(problems)
            
            question = f"Mi llanta presenta {problem}. ¿Qué puede ser?"
            
            if problem == "desgaste irregular":
                answer = "El desgaste irregular puede indicar: desalineación, problemas de suspensión, presión incorrecta o rotación insuficiente. Recomiendo inspección inmediata y posible alineación. ¿Hace cuánto no realiza mantenimiento?"
            elif problem == "vibración al manejar":
                answer = "La vibración puede ser causada por: desbalance de llantas, deformación del aro, problemas de suspensión o desgaste irregular. Recomendamos balanceo y inspección. ¿A qué velocidad se presenta la vibración?"
            elif problem == "ruido excesivo":
                answer = "El ruido excesivo puede indicar: desgaste avanzado, patrón de banda de rodadura inadecuado, presión incorrecta o daño interno. ¿El ruido es constante o solo al girar?"
            elif problem == "pérdida de presión":
                answer = "La pérdida de presión puede ser por: pinchazo, válvula defectuosa, fisura en el aro o envejecimiento del neumático. Recomiendo inspección inmediata. ¿Qué tan rápido pierde presión?"
            else:
                answer = "El agrietamiento lateral indica envejecimiento del neumático y es peligroso. Recomendamos reemplazo inmediato por seguridad. ¿Cuántos años tienen las llantas?"
        
        elif question_type == "comparacion_productos":
            # 产品比较
            spec = tire_spec or random.choice(list(tire_specs))
            products = get_products_by_spec(spec)
            
            if len(products) >= 2:
                brand1 = products[0]['name'].split()[3]
                brand2 = products[1]['name'].split()[3]
                question = f"¿Cuál es la diferencia entre {brand1} y {brand2} en {spec}?"
                
                price_diff = abs(products[0]['price'] - products[1]['price'])
                answer = f"Comparando {brand1} (${products[0]['price']}) vs {brand2} (${products[1]['price']}):\\n\\n• Diferencia de precio: ${price_diff}\\n• {brand1}: {'Premium' if products[0]['price'] > products[1]['price'] else 'Económica'} opción\\n• {brand2}: {'Premium' if products[1]['price'] > products[0]['price'] else 'Económica'} opción\\n\\n¿Cuál es su prioridad: precio o prestaciones?"
            else:
                question = f"¿Cuál marca recomiendan para {spec}?"
                answer = f"Para {spec} recomendamos nuestras marcas más confiables según su presupuesto y uso. ¿Busca economía, rendimiento o durabilidad?"
        
        elif question_type == "recomendacion_uso":
            # 使用建议
            usage_types = [
                "ciudad y carretera",
                "principalmente ciudad",
                "uso intensivo",
                "condiciones de lluvia",
                "manejo deportivo"
            ]
            usage = random.choice(usage_types)
            
            question = f"¿Qué llantas recomiendan para {usage}?"
            
            if usage == "ciudad y carretera":
                answer = "Para uso mixto recomendamos neumáticos touring como COMPASAL BLAZER HP o GOODYEAR ASSURANCE. Ofrecen buen balance entre comodidad, durabilidad y economía de combustible. ¿Qué especificación necesita?"
            elif usage == "principalmente ciudad":
                answer = "Para uso urbano recomendamos neumáticos con buen agarre en seco/mojado y baja resistencia al rodamiento. ANSU OPTECO A1 o SAFERICH FRC16 son excelentes opciones. ¿Maneja mucho en lluvia?"
            elif usage == "uso intensivo":
                answer = "Para uso intensivo recomendamos neumáticos premium como GOODYEAR ASSURANCE o JK TYRE VECTRA. Ofrecen mayor durabilidad y resistencia al desgaste. ¿Cuántos kilómetros recorre mensualmente?"
            elif usage == "condiciones de lluvia":
                answer = "Para lluvia recomendamos neumáticos con excelente evacuación de agua como BLACKHAWK HH11 AUTO o GOODYEAR ASSURANCE. Tienen compuesto especial para mejor tracción en mojado. ¿Qué especificación necesita?"
            else:
                answer = "Para manejo deportivo recomendamos neumáticos con mayor índice de velocidad y mejor respuesta. COMPASAL BLAZER HP o JK TYRE VECTRA ofrecen buen desempeño. ¿Busca especificación específica?"
        
        else:  # garantia_servicio
            # 保修服务
            warranty_topics = [
                "garantía de las llantas",
                "política de cambios",
                "servicio postventa",
                "tiempo de entrega",
                "formas de pago"
            ]
            topic = random.choice(warranty_topics)
            
            question = f"¿Cuál es su {topic}?"
            
            if topic == "garantía de las llantas":
                answer = "Ofrecemos garantía de 12 meses contra defectos de manufactura en todas nuestras llantas. La garantía no cubre desgaste normal, daños por mal uso o pinchaduras. ¿Tiene alguna llanta con problema?"
            elif topic == "política de cambios":
                answer = "Aceptamos cambios dentro de 30 días si la llanta no ha sido usada y conserva etiquetas originales. Para llantas instaladas, evaluamos caso por caso. ¿Necesita realizar algún cambio?"
            elif topic == "servicio postventa":
                answer = "Ofrecemos servicio postventa completo: balanceo gratuito por 30 días, revisión de presión mensual, rotación con descuento especial y asesoría técnica. ¿Qué servicio necesita?"
            elif topic == "tiempo de entrega":
                answer = "Productos en stock: entrega inmediata. Productos por pedido: 3-5 días hábiles. Instalación a domicilio: se agenda dentro de 24-48 horas. ¿Necesita entrega urgente?"
            else:
                answer = "Aceptamos efectivo, tarjetas de crédito/débito, transferencias bancarias y pagos en línea. Para compras mayores a $5,000 ofrecemos planes de financiamiento. ¿Cuál forma prefiere?"
        
        return question, answer
    
    # 生成数据行
    data_rows = []
    used_questions = set()  # 跟踪已使用的问题，避免重复
    
    # 确保每种问题类型都有合理的分布
    questions_per_type = 111 // len(question_types)
    extra_questions = 111 % len(question_types)
    
    row_index = 1
    
    for i, question_type in enumerate(question_types):
        # 计算这个类型需要生成多少个问题
        questions_count = questions_per_type + (1 if i < extra_questions else 0)
        
        for j in range(questions_count):
            # 生成问题，确保不重复
            attempts = 0
            while attempts < 20:  # 最多尝试20次
                try:
                    # 随机选择轮胎规格和车型
                    tire_spec = random.choice(list(tire_specs)) if tire_specs else None
                    car_model = random.choice(car_models) if random.random() < 0.3 else None
                    
                    question, answer = generate_question_answer_pair(question_type, j, tire_spec, car_model)
                    
                    if question not in used_questions:
                        used_questions.add(question)
                        break
                    
                    attempts += 1
                except Exception as e:
                    print(f"生成问题时出错: {e}")
                    attempts += 1
            
            if attempts >= 20:
                print(f"警告：无法为类型 {question_type} 生成唯一问题，使用默认问题")
                question = f"Consulta general sobre neumáticos - {question_type} {j+1}"
                answer = "Gracias por su consulta. Nuestro equipo le ayudará con toda la información que necesite sobre neumáticos."
            
            # 创建数据行
            row = [
                row_index,  # #
                question_type.replace('_', ' ').title(),  # Pregunta (分类)
                "Respuesta estándar FAQ",  # Fuente de Respuesta
                "Fuente FAQ",  # Fuente de Pregunta
                "Satisfactorio",  # Satisfactorio
                row_index,  # Número de Serie
                question,  # Contenido de Pregunta
                answer  # Respuesta de Referencia
            ]
            
            data_rows.append(row)
            row_index += 1
    
    # 确保恰好有111行
    while len(data_rows) < 111:
        # 如果不足111行，添加额外的问题
        question_type = random.choice(question_types)
        tire_spec = random.choice(list(tire_specs)) if tire_specs else None
        car_model = random.choice(car_models) if random.random() < 0.3 else None
        
        question, answer = generate_question_answer_pair(question_type, len(data_rows), tire_spec, car_model)
        
        if question not in used_questions:
            used_questions.add(question)
            row = [
                row_index,
                question_type.replace('_', ' ').title(),
                "Respuesta estándar FAQ",
                "Fuente FAQ",
                "Satisfactorio",
                row_index,
                question,
                answer
            ]
            data_rows.append(row)
            row_index += 1
    
    # 如果超过111行，裁剪到111行
    data_rows = data_rows[:111]
    
    # 保存为CSV文件
    output_filename = "轮胎测试数据_西班牙语_多轮对话_多样化版本.csv"
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(spanish_headers)
        writer.writerows(data_rows)
    
    print(f"✅ 成功创建多样化西班牙语数据文件: {output_filename}")
    print(f"📊 总共生成了 {len(data_rows)} 行数据")
    print(f"🎯 包含 {len(used_questions)} 个不同的问题")
    print(f"🔧 涵盖 {len(question_types)} 种问题类型")
    print(f"🚗 基于 {len(car_models)} 种车型")
    print(f"🛞 涉及 {len(tire_specs)} 种轮胎规格")
    
    return output_filename

# 执行脚本
if __name__ == "__main__":
    create_diverse_spanish_qa() 