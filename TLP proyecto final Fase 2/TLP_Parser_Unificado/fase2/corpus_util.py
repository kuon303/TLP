"""Valida el corpus de 60 oraciones compartido por todos los enfoques."""
import csv
from collections import Counter
from pathlib import Path

CAMPOS = {'id', 'nivel', 'oracion', 'esperado_cfg', 'correcta_espanol', 'fenomeno'}


def leer_corpus(ruta):
    ruta = Path(ruta)
    with ruta.open(encoding='utf-8-sig', newline='') as archivo:
        lector = csv.DictReader(archivo)
        if not CAMPOS.issubset(lector.fieldnames or []):
            raise ValueError('El corpus no tiene todas las columnas necesarias')
        casos = list(lector)
    if len(casos) != 60:
        raise ValueError(f'Se requieren 60 oraciones: llegaron {len(casos)}')
    ids = [c['id'] for c in casos]
    if len(set(ids)) != 60 or any(not x for x in ids):
        raise ValueError('Los ID del corpus deben ser unicos y no vacios')
    if any(not c['oracion'].strip() or c['nivel'] not in ('1','2','3') or
           c['esperado_cfg'] not in ('ACEPTADA','RECHAZADA') for c in casos):
        raise ValueError('El corpus tiene datos incompletos o invalidos')
    if Counter(c['esperado_cfg'] for c in casos) != Counter({'ACEPTADA':40,'RECHAZADA':20}):
        raise ValueError('La distribucion esperada es 40 aceptadas y 20 rechazadas')
    if Counter(c['nivel'] for c in casos) != Counter({'1':20,'2':20,'3':20}):
        raise ValueError('Se esperan 20 oraciones por nivel')
    return casos
