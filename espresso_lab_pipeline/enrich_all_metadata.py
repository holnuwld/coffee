import json
import re
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('espresso_lab_pipeline/raw_parsed_coffees.json', 'r', encoding='utf-8') as f:
    coffees = json.load(f)

print(f"Enriching {len(coffees)} coffees...")

# Rules and pattern matchers based on the description text
PRODUCER_PATTERNS = [
    r'produced by\s+([^,.\n]+)',
    r'producer\s*:\s*([^,.\n<]+)',
    r'farmer\s*:\s*([^,.\n<]+)',
    r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
    r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+is one of',
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+Family)',
    r'About the Producer\s+([^.\n]+)'
]

FARM_PATTERNS = [
    r'farm\s*:\s*([^,.\n<]+)',
    r'(Finca\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Estate)',
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Washing Station)',
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Farm)'
]

LOCATION_PATTERNS = [
    r'location\s*:\s*([^,.\n<]+)',
    r'origin\s*:\s*([^,.\n<]+)',
    r'region\s*:\s*([^,.\n<]+)',
    r'in the highlands of\s+([^,.\n]+)',
    r'nestled in\s+([^,.\n]+)',
    r'located in\s+([^,.\n]+)'
]

for c in coffees:
    desc = c.get('desc_text', '')
    title = c['title']
    handle = c['handle']
    
    # 1. Country refinement
    if 'panama' in desc.lower() or 'boquete' in desc.lower() or 'chiriqu' in desc.lower() or any(k in handle for k in ['auromar', 'lamastus', 'kotowa', 'lerida', 'longboard', 'nuguo', 'salto', 'chevas', 'finquita', 'santos']):
        c['country'] = 'Panama'
    elif 'ethiopia' in desc.lower() or 'sidama' in desc.lower() or 'guji' in desc.lower() or 'yirgacheffe' in desc.lower() or any(k in handle for k in ['bombe', 'hambela', 'geisha-village', 'haru', 'testi', 'harusuke']):
        c['country'] = 'Ethiopia'
    elif 'kenya' in desc.lower() or 'nyeri' in desc.lower() or any(k in handle for k in ['kamavindi', 'giakanja', 'cianda']):
        c['country'] = 'Kenya'
    elif 'colombia' in desc.lower() or 'huila' in desc.lower() or 'cauca' in desc.lower() or any(k in handle for k in ['negrita', 'milan', 'rubi', 'moreno']):
        c['country'] = 'Colombia'
    elif 'brazil' in desc.lower() or 'cerrado' in desc.lower() or any(k in handle for k in ['daterra', 'carmo', 'samambaia']):
        c['country'] = 'Brazil'
    elif 'honduras' in desc.lower() or 'guzman' in handle:
        c['country'] = 'Honduras'
    elif 'costa rica' in desc.lower():
        c['country'] = 'Costa Rica'
    elif 'ecuador' in desc.lower():
        c['country'] = 'Ecuador'
    
    # 2. Specific Known Producers & Farms in Espresso Lab Catalog
    if 'auromar' in handle:
        c['producer'] = 'Roberto Brenes / Auromar Family'
        c['farm'] = 'Finca La Auromar'
        c['location'] = 'Piedra Candela, Chiriquí'
        c['country'] = 'Panama'
    elif 'lamastus' in handle:
        c['producer'] = 'Wilford Lamastus Family'
        c['farm'] = 'Elida Estate'
        c['location'] = 'Boquete, Chiriquí'
        c['country'] = 'Panama'
    elif 'bombe-washed' in handle:
        c['producer'] = 'Tamiru Tadesse / Alo Coffee'
        c['farm'] = 'Bombe Washing Station'
        c['location'] = 'Sidama Bensa'
        c['country'] = 'Ethiopia'
    elif 'geisha-village' in handle:
        c['producer'] = 'Adam Overton & Rachel Samuel'
        c['farm'] = 'Geisha Village Estate (Oma Lot 1)'
        c['location'] = 'Bench Maji'
        c['country'] = 'Ethiopia'
    elif 'kotowa' in handle:
        c['producer'] = 'Ricardo Koyner'
        c['farm'] = 'Finca Kotowa (Las Brujas)'
        c['location'] = 'Boquete, Chiriquí'
        c['country'] = 'Panama'
    elif 'lerida' in handle:
        if '0642' in handle:
            c['producer'] = 'Garcia Family'
        else:
            c['producer'] = 'Maria Antonella Amoruso'
        c['farm'] = 'Finca Lérida'
        c['location'] = 'Alto Quiel, Boquete'
        c['country'] = 'Panama'
    elif 'longboard' in handle:
        c['producer'] = 'Justin Boudeman'
        c['farm'] = 'Longboard Coffee (Misty Mountain)'
        c['location'] = 'Piedra Candela, Boquete'
        c['country'] = 'Panama'
    elif 'nuguo' in handle:
        c['producer'] = 'José Manuel "Pocho" Gallardo Méndez'
        c['farm'] = 'Finca Nuguo'
        c['location'] = 'Jurutungo, Renacimiento'
        c['country'] = 'Panama'
    elif 'morgan-estate' in handle:
        c['producer'] = 'The Morgan Family & Jamison Savage'
        c['farm'] = 'Morgan Estate'
        c['location'] = 'Boquete, Chiriquí'
        c['country'] = 'Panama'
    elif 'las-nubes' in handle:
        c['producer'] = 'Lost Origin Coffee Lab'
        c['farm'] = 'Finca Las Nubes'
        c['location'] = 'Boquete, Chiriquí'
        c['country'] = 'Panama'
    elif 'mi-finquita' in handle:
        c['producer'] = 'Ratibor Hartmann & Tessie Palacios'
        c['farm'] = 'Mi Finquita'
        c['location'] = 'Los Naranjos, Boquete'
        c['country'] = 'Panama'
    elif 'kamavindi-giakanja' in handle:
        c['producer'] = 'Giakanja Farmers Co-op'
        c['farm'] = 'Giakanja Washing Station'
        c['location'] = 'Nyeri'
        c['country'] = 'Kenya'
    elif 'kamavindi-cianda' in handle:
        c['producer'] = 'Cianda Estate'
        c['farm'] = 'Cianda Estate'
        c['location'] = 'Kiambu'
        c['country'] = 'Kenya'
    elif 'guji-hambela-rogicha' in handle:
        c['producer'] = 'Rogicha Smallholders / METAD'
        c['farm'] = 'Rogicha Washing Station'
        c['location'] = 'Guji Hambela'
        c['country'] = 'Ethiopia'
    elif 'harusuke' in handle:
        c['producer'] = 'Harusuke Washing Station'
        c['farm'] = 'Harusuke Station'
        c['location'] = 'Guji'
        c['country'] = 'Ethiopia'
    elif 'la-negrita' in handle:
        c['producer'] = 'Mauricio Shattah'
        c['farm'] = 'Finca La Negrita'
        c['location'] = 'Tolima'
        c['country'] = 'Colombia'
    elif 'carmo-fazenda' in handle:
        c['producer'] = 'Isidro Pereira Family'
        c['farm'] = 'Fazenda Isidro Pereira'
        c['location'] = 'Carmo de Minas, Minas Gerais'
        c['country'] = 'Brazil'
    elif 'samambaia' in handle:
        c['producer'] = 'Henrique Cambraia'
        c['farm'] = 'Fazenda Samambaia'
        c['location'] = 'Santo Antônio do Amparo, Sul de Minas'
        c['country'] = 'Brazil'
    elif 'daterra' in handle:
        c['producer'] = 'Daterra Coffee'
        c['farm'] = 'Daterra Farm'
        c['location'] = 'Cerrado Mineiro'
        c['country'] = 'Brazil'
    elif 'chevas' in handle:
        c['producer'] = 'Chevas Coffee Estate'
        c['farm'] = 'Finca Chevas'
        c['location'] = 'Boquete, Chiriquí'
        c['country'] = 'Panama'
    elif 'cgle' in handle:
        c['producer'] = 'Rigoberto & Luis Eduardo Herrera (Cafe Granja La Esperanza)'
        c['farm'] = 'Finca Las Margaritas / Potosi'
        c['location'] = 'Valle del Cauca'
        c['country'] = 'Colombia'
    elif 'cota' in handle:
        c['producer'] = 'Finca Cota'
        c['farm'] = 'Finca Cota'
        c['location'] = 'Tarrazú'
        c['country'] = 'Costa Rica'
    elif 'el-olingo' in handle:
        c['producer'] = 'Finca El Olingo'
        c['farm'] = 'Finca El Olingo'
        c['location'] = 'Boquete, Chiriquí'
        c['country'] = 'Panama'
    elif 'el-rubi' in handle:
        c['producer'] = 'Heiner Lazo'
        c['farm'] = 'Finca El Rubí'
        c['location'] = 'San Adolfo, Acevedo, Huila'
        c['country'] = 'Colombia'
    elif 'el-salto' in handle:
        c['producer'] = 'Finca El Salto'
        c['farm'] = 'Finca El Salto'
        c['location'] = 'Boquete, Chiriquí'
        c['country'] = 'Panama'
    elif 'finca-feryen' in handle:
        c['producer'] = 'Finca Feryen'
        c['farm'] = 'Finca Feryen'
        c['location'] = 'Nyeri'
        c['country'] = 'Kenya'
    elif 'finca-milan' in handle:
        c['producer'] = 'Julio Madrid'
        c['farm'] = 'Finca Milán'
        c['location'] = 'Pereira, Risaralda'
        c['country'] = 'Colombia'
    elif 'moreno' in handle:
        c['producer'] = 'Edilberto Moreno'
        c['farm'] = 'Finca Moreno'
        c['location'] = 'Huila'
        c['country'] = 'Colombia'
    elif 'nelin-guzman' in handle:
        c['producer'] = 'Nelin Guzmán'
        c['farm'] = 'Finca Los Pinos'
        c['location'] = 'Pozo Negro, Intibucá'
        c['country'] = 'Honduras'
    elif 'nocturne' in handle:
        c['producer'] = 'The Espresso Lab Selection'
        c['farm'] = 'Specialty Smallholders'
        c['location'] = 'Highland Regions'
        c['country'] = 'Blend / Origin'
    elif 'ponderosa' in handle:
        c['producer'] = 'Ponderosa Coffee / Cordillera Central'
        c['farm'] = 'Finca Ponderosa'
        c['location'] = 'Cordillera Central'
        c['country'] = 'Panama'
    elif 'romesas' in handle:
        c['producer'] = 'Romesas Coffee'
        c['farm'] = 'Finca Romesas'
        c['location'] = 'Chiriquí'
        c['country'] = 'Panama'
    elif 'santos-geisha' in handle:
        c['producer'] = 'The Lezcano Family'
        c['farm'] = 'Santos Coffee Estate'
        c['location'] = 'Boquete, Chiriquí'
        c['country'] = 'Panama'
    elif 'santa-isabel' in handle or 'agricola-geisha' in handle:
        c['producer'] = 'Agricola Geisha'
        c['farm'] = 'Finca Santa Isabel'
        c['location'] = 'Boquete, Chiriquí'
        c['country'] = 'Panama'
    elif 'testi' in handle:
        c['producer'] = 'Testi Coffee / Faysel Abdosh'
        c['farm'] = 'Yaye / Hambela Station'
        c['location'] = 'Guji & Sidama'
        c['country'] = 'Ethiopia'
    elif 'yirgacheffe-haru' in handle:
        c['producer'] = 'Haru Washing Station Smallholders'
        c['farm'] = 'Haru Station'
        c['location'] = 'Yirgacheffe'
        c['country'] = 'Ethiopia'

    # Fill default if still blank
    if not c['producer'] or c['producer'] == 'Specialty Producer':
        c['producer'] = c['farm'] or 'Specialty Producer'
    if not c['farm']:
        c['farm'] = c['title']
    if not c['location']:
        c['location'] = c['country']

# Save enriched dataset
with open('espresso_lab_pipeline/enriched_coffees.json', 'w', encoding='utf-8') as out_f:
    json.dump(coffees, out_f, ensure_ascii=False, indent=2)

print("Enriched dataset saved to espresso_lab_pipeline/enriched_coffees.json")
