"""Vocabulario del subconjunto de español, organizado por rasgos gramaticales.

Las formas están escritas explícitamente: el lexer no infiere género o número
por la última letra. Cada pareja es singular/plural; los adjetivos variables
se escriben como masculino singular/femenino singular/masculino plural/femenino
plural. Los verbos son formas de tercera persona singular/plural.
"""

ARTICULOS = {
    'el': 'ART_MS', 'la': 'ART_FS', 'los': 'ART_MP', 'las': 'ART_FP',
    'un': 'ART_MS', 'una': 'ART_FS', 'unos': 'ART_MP', 'unas': 'ART_FP',
}

SUSTANTIVOS_MASCULINOS = """
niño/niños perro/perros gato/gatos parque/parques telescopio/telescopios
carro/carros auto/autos automóvil/automóviles vehículo/vehículos camión/camiones
tren/trenes avión/aviones barco/barcos autobús/autobuses taxi/taxis
ciclista/ciclistas conductor/conductores pasajero/pasajeros mecánico/mecánicos
hombre/hombres padre/padres hijo/hijos hermano/hermanos abuelo/abuelos
tío/tíos primo/primos amigo/amigos vecino/vecinos compañero/compañeros
alumno/alumnos estudiante/estudiantes profesor/profesores maestro/maestros
doctor/doctores médico/médicos enfermero/enfermeros ingeniero/ingenieros
arquitecto/arquitectos abogado/abogados periodista/periodistas escritor/escritores
lector/lectores artista/artistas músico/músicos cantante/cantantes actor/actores
policía/policías bombero/bomberos trabajador/trabajadores vendedor/vendedores
cocinero/cocineros jardinero/jardineros panadero/panaderos agricultor/agricultores
niñero/niñeros deportista/deportistas jugador/jugadores entrenador/entrenadores
presidente/presidentes director/directores jefe/jefes secretario/secretarios
bebé/bebés muchacho/muchachos joven/jóvenes adulto/adultos anciano/ancianos
alcalde/alcaldes rey/reyes príncipe/príncipes abuelo/abuelos
árbol/árboles bosque/bosques río/ríos lago/lagos mar/mares océano/océanos
monte/montes cerro/cerros volcán/volcanes desierto/desiertos campo/campos
camino/caminos sendero/senderos puente/puentes edificio/edificios
hospital/hospitales colegio/colegios instituto/institutos museo/museos
teatro/teatros cine/cines restaurante/restaurantes hotel/hoteles
mercado/mercados supermercado/supermercados aeropuerto/aeropuertos
puerto/puertos estadio/estadios gimnasio/gimnasios banco/bancos
jardín/jardines patio/patios cuarto/cuartos dormitorio/dormitorios
baño/baños comedor/comedores pasillo/pasillos techo/techos
piso/pisos suelo/suelos muro/muros libro/libros cuaderno/cuadernos
lápiz/lápices bolígrafo/bolígrafos papel/papeles periódico/periódicos
texto/textos cuento/cuentos poema/poemas capítulo/capítulos
examen/exámenes ejercicio/ejercicios problema/problemas resultado/resultados
trabajo/trabajos proyecto/proyectos programa/programas código/códigos
archivo/archivos documento/documentos mensaje/mensajes correo/correos
ordenador/ordenadores computador/computadores teléfono/teléfonos
celular/celulares teclado/teclados ratón/ratones monitor/monitores
servidor/servidores sistema/sistemas dispositivo/dispositivos
objeto/objetos instrumento/instrumentos reloj/relojes calendario/calendarios
vaso/vasos plato/platos tenedor/tenedores cuchillo/cuchillos
zapato/zapatos pantalón/pantalones sombrero/sombreros abrigo/abrigos
color/colores dibujo/dibujos cuadro/cuadros regalo/regalos
juguete/juguetes globo/globos balón/balones partido/partidos
juego/juegos deporte/deportes equipo/equipos grupo/grupos
pueblo/pueblos barrio/barrios país/países estado/estados
continente/continentes planeta/planetas mundo/mundos universo/universos sujeto/sujetos predicado/predicados
sol/soles día/días mes/meses año/años minuto/minutos segundo/segundos
momento/momentos tiempo/tiempos sueño/sueños sonido/sonidos
ruido/ruidos viento/vientos trueno/truenos relámpago/relámpagos
animal/animales caballo/caballos conejo/conejos pájaro/pájaros
pez/peces león/leones tigre/tigres elefante/elefantes
oso/osos zorro/zorros lobo/lobos mono/monos
cabello/cabellos ojo/ojos brazo/brazos dedo/dedos
pie/pies corazón/corazones cuerpo/cuerpos rostro/rostros
"""

SUSTANTIVOS_FEMENINOS = """
niña/niñas perra/perras gata/gatas casa/casas escuela/escuelas
persona/personas mujer/mujeres madre/madres hija/hijas hermana/hermanas
abuela/abuelas tía/tías prima/primas amiga/amigas vecina/vecinas
compañera/compañeras alumna/alumnas estudiante/estudiantes
profesora/profesoras maestra/maestras doctora/doctoras médica/médicas
enfermera/enfermeras ingeniera/ingenieras arquitecta/arquitectas
abogada/abogadas periodista/periodistas escritora/escritoras
lectora/lectoras artista/artistas música/músicas cantante/cantantes
actriz/actrices policía/policías bombera/bomberas
trabajadora/trabajadoras vendedora/vendedoras cocinera/cocineras
jardinera/jardineras panadera/panaderas agricultora/agricultoras
deportista/deportistas jugadora/jugadoras entrenadora/entrenadoras
presidenta/presidentas directora/directoras jefa/jefas secretaria/secretarias
muchacha/muchachas joven/jóvenes adulta/adultas anciana/ancianas
reina/reinas princesa/princesas
ciudad/ciudades calle/calles avenida/avenidas carretera/carreteras
plaza/plazas montaña/montañas colina/colinas isla/islas
playa/playas costa/costas región/regiones provincia/provincias
comunidad/comunidades zona/zonas frontera/fronteras
habitación/habitaciones sala/salas cocina/cocinas mesa/mesas
silla/sillas ventana/ventanas puerta/puertas pared/paredes
escalera/escaleras cama/camas almohada/almohadas manta/mantas
lámpara/lámparas televisión/televisiones radio/radios
computadora/computadoras pantalla/pantallas impresora/impresoras
cámara/cámaras batería/baterías aplicación/aplicaciones
herramienta/herramientas máquina/máquinas pieza/piezas
rueda/ruedas bicicleta/bicicletas motocicleta/motocicletas
camioneta/camionetas furgoneta/furgonetas nave/naves
estación/estaciones parada/paradas carretera/carreteras
biblioteca/bibliotecas librería/librerías universidad/universidades
facultad/facultades oficina/oficinas empresa/empresas
fábrica/fábricas tienda/tiendas farmacia/farmacias
clínica/clínicas iglesia/iglesias habitación/habitaciones
clase/clases lección/lecciones asignatura/asignaturas
materia/materias tarea/tareas pregunta/preguntas
respuesta/respuestas prueba/pruebas nota/notas
calificación/calificaciones investigación/investigaciones
ciencia/ciencias teoría/teorías fórmula/fórmulas
palabra/palabras letra/letras oración/oraciones
frase/frases gramática/gramáticas lengua/lenguas
historia/historias novela/novelas noticia/noticias
revista/revistas página/páginas hoja/hojas
fotografía/fotografías imagen/imágenes película/películas
canción/canciones melodía/melodías música/músicas
voz/voces conversación/conversaciones charla/charlas
reunión/reuniones fiesta/fiestas celebración/celebraciones
familia/familias amistad/amistades relación/relaciones
sociedad/sociedades población/poblaciones nación/naciones
noche/noches tarde/tardes mañana/mañanas semana/semanas
hora/horas fecha/fechas temporada/temporadas
luna/lunas estrella/estrellas nube/nubes lluvia/lluvias
flor/flores planta/plantas rama/ramas raíz/raíces
semilla/semillas fruta/frutas manzana/manzanas
pera/peras naranja/naranjas uva/uvas
banana/bananas papa/papas zanahoria/zanahorias
comida/comidas bebida/bebidas sopa/sopas
ensalada/ensaladas torta/tortas galleta/galletas
camisa/camisas blusa/blusas chaqueta/chaquetas
falda/faldas bufanda/bufandas gorra/gorras
mano/manos cabeza/cabezas pierna/piernas
oreja/orejas nariz/narices boca/bocas
espalda/espaldas rodilla/rodillas cara/caras
mariposa/mariposas abeja/abejas hormiga/hormigas
vaca/vacas oveja/ovejas gallina/gallinas
tortuga/tortugas serpiente/serpientes
"""

ADJETIVOS_VARIABLES = """
pequeño/pequeña/pequeños/pequeñas
alto/alta/altos/altas
tranquilo/tranquila/tranquilos/tranquilas
bonito/bonita/bonitos/bonitas
feo/fea/feos/feas
bueno/buena/buenos/buenas
malo/mala/malos/malas
nuevo/nueva/nuevos/nuevas
viejo/vieja/viejos/viejas
rápido/rápida/rápidos/rápidas
lento/lenta/lentos/lentas
largo/larga/largos/largas
corto/corta/cortos/cortas
ancho/ancha/anchos/anchas
estrecho/estrecha/estrechos/estrechas
limpio/limpia/limpios/limpias
sucio/sucia/sucios/sucias
oscuro/oscura/oscuros/oscuras
claro/clara/claros/claras
frío/fría/fríos/frías
seco/seca/secos/secas
mojado/mojada/mojados/mojadas
blanco/blanca/blancos/blancas
negro/negra/negros/negras
rojo/roja/rojos/rojas
amarillo/amarilla/amarillos/amarillas
morado/morada/morados/moradas
dorado/dorada/dorados/doradas
plateado/plateada/plateados/plateadas
cansado/cansada/cansados/cansadas
ocupado/ocupada/ocupados/ocupadas
preocupado/preocupada/preocupados/preocupadas
contento/contenta/contentos/contentas
enojado/enojada/enojados/enojadas
aburrido/aburrida/aburridos/aburridas
asustado/asustada/asustados/asustadas
emocionado/emocionada/emocionados/emocionadas
preparado/preparada/preparados/preparadas
ordenado/ordenada/ordenados/ordenadas
desordenado/desordenada/desordenados/desordenadas
cerrado/cerrada/cerrados/cerradas
abierto/abierta/abiertos/abiertas
apagado/apagada/apagados/apagadas
encendido/encendida/encendidos/encendidas
pintado/pintada/pintados/pintadas
arreglado/arreglada/arreglados/arregladas
roto/rota/rotos/rotas
completo/completa/completos/completas
incompleto/incompleta/incompletos/incompletas
correcto/correcta/correctos/correctas
incorrecto/incorrecta/incorrectos/incorrectas
seguro/segura/seguros/seguras
peligroso/peligrosa/peligrosos/peligrosas
famoso/famosa/famosos/famosas
conocido/conocida/conocidos/conocidas
simpático/simpática/simpáticos/simpáticas
serio/seria/serios/serias
tímido/tímida/tímidos/tímidas
honesto/honesta/honestos/honestas
creativo/creativa/creativos/creativas
curioso/curiosa/curiosos/curiosas
orgulloso/orgullosa/orgullosos/orgullosas
intenso/intensa/intensos/intensas
profundo/profunda/profundos/profundas
sencillo/sencilla/sencillos/sencillas
complicado/complicada/complicados/complicadas
delgado/delgada/delgados/delgadas
grueso/gruesa/gruesos/gruesas
pesado/pesada/pesados/pesadas
ligero/ligera/ligeros/ligeras
blando/blanda/blandos/blandas
duro/dura/duros/duras
redondo/redonda/redondos/redondas
cuadrado/cuadrada/cuadrados/cuadradas
lleno/llena/llenos/llenas
vacío/vacía/vacíos/vacías
"""

ADJETIVOS_COMUNES = """
grande/grandes interesante/interesantes importante/importantes
inteligente/inteligentes excelente/excelentes suficiente/suficientes
diferente/diferentes frecuente/frecuentes reciente/recientes
presente/presentes ausente/ausentes evidente/evidentes
amable/amables agradable/agradables adorable/adorables
triste/tristes fuerte/fuertes suave/suaves joven/jóvenes
feliz/felices capaz/capaces eficaz/eficaces
fácil/fáciles difícil/difíciles útil/útiles
inútil/inútiles débil/débiles hábil/hábiles caliente/calientes
sensible/sensibles visible/visibles invisible/invisibles valiente/valientes responsable/responsables
terrible/terribles increíble/increíbles posible/posibles
imposible/imposibles flexible/flexibles estable/estables
inestable/inestables libre/libres pobre/pobres
verde/verdes azul/azules gris/grises marrón/marrones
normal/normales especial/especiales familiar/familiares
natural/naturales artificial/artificiales principal/principales
final/finales inicial/iniciales general/generales
particular/particulares igual/iguales similar/similares
mayor/mayores menor/menores mejor/mejores peor/peores
ideal/ideales real/reales original/originales
rural/rurales digital/digitales social/sociales
"""

VERBOS_TERCERA_PERSONA = """
corre/corren canta/cantan duerme/duermen juega/juegan camina/caminan
habla/hablan escucha/escuchan mira/miran observa/observan
lee/leen escribe/escriben estudia/estudian aprende/aprenden
enseña/enseñan explica/explican pregunta/preguntan
responde/responden trabaja/trabajan descansa/descansan
viaja/viajan conduce/conducen maneja/manejan llega/llegan
avanza/avanzan frena/frenan acelera/aceleran gira/giran arranca/arrancan
estaciona/estacionan circula/circulan choca/chocan
sale/salen entra/entran vuelve/vuelven regresa/regresan
sube/suben baja/bajan salta/saltan nada/nadan
baila/bailan ríe/ríen sonríe/sonríen llora/lloran
grita/gritan llama/llaman saluda/saludan visita/visitan
espera/esperan busca/buscan encuentra/encuentran
abre/abren cierra/cierran limpia/limpian arregla/arreglan
construye/construyen pinta/pintan dibuja/dibujan
cocina/cocinan come/comen bebe/beben desayuna/desayunan
almuerza/almuerzan cena/cenan compra/compran vende/venden
paga/pagan ahorra/ahorran gana/ganan pierde/pierden
prepara/preparan utiliza/utilizan usa/usan necesita/necesitan
tiene/tienen quiere/quieren puede/pueden sabe/saben es/son está/están
conoce/conocen entiende/entienden piensa/piensan
recuerda/recuerdan olvida/olvidan cree/creen decide/deciden
elige/eligen prefiere/prefieren comienza/comienzan
empieza/empiezan termina/terminan continúa/continúan
cambia/cambian mejora/mejoran aumenta/aumentan
reduce/reducen crece/crecen florece/florecen
ayuda/ayudan cuida/cuidan protege/protegen
acompaña/acompañan sigue/siguen deja/dejan
trae/traen lleva/llevan pone/ponen quita/quitan
mueve/mueven levanta/levantan empuja/empujan
tira/tiran lanza/lanzan recoge/recogen
rompe/rompen repara/reparan entrega/entregan
recibe/reciben envía/envían comparte/comparten
participa/participan colabora/colaboran organiza/organizan
planifica/planifican practica/practican entrena/entrenan
compite/compiten juega/juegan marca/marcan
anota/anotan dibuja/dibujan calcula/calculan
resuelve/resuelven analiza/analizan compara/comparan
describe/describen explica/explican demuestra/demuestran
funciona/funcionan falla/fallan inicia/inician
acaba/acaban existe/existen aparece/aparecen
desaparece/desaparecen ocurre/ocurren sucede/suceden
brilla/brillan ilumina/iluminan suena/suenan
truena/truenan llueve/llueven nieva/nievan
vuela/vuelan respira/respiran camina/caminan
"""

ADVERBIOS = """
rápidamente lentamente tranquilamente alegremente
velozmente suavemente fácilmente difícilmente
cuidadosamente pacientemente amablemente felizmente
tristemente claramente correctamente incorrectamente
seguramente probablemente posiblemente normalmente
frecuentemente ocasionalmente raramente constantemente
regularmente diariamente semanalmente mensualmente
anualmente recientemente actualmente anteriormente
posteriormente inmediatamente finalmente inicialmente
simplemente únicamente solamente especialmente
principalmente generalmente totalmente completamente
parcialmente exactamente aproximadamente prácticamente
realmente sinceramente honestamente seriamente
intensamente profundamente directamente indirectamente
abiertamente libremente cómodamente silenciosamente
ruidosamente públicamente secretamente voluntariamente
involuntariamente eficientemente lentamente
perfectamente oportunamente bien mal hoy ayer mañana siempre nunca
también tampoco aquí allí afuera dentro cerca lejos mucho poco bastante demasiado
"""

PREPOSICIONES = """
en con por a de para sin sobre entre desde hasta hacia
contra durante mediante según ante bajo tras
"""


def _pares(texto):
    for par in texto.split():
        formas = par.split('/')
        if len(formas) != 2:
            raise ValueError(f'Pareja de formas inválida: {par}')
        yield formas


def _crear_vocabulario():
    diccionario = {}

    def agregar(palabra, categoria):
        palabra = palabra.casefold()
        actual = diccionario.get(palabra)
        if actual is None:
            diccionario[palabra] = [categoria]
        elif categoria not in actual:
            actual.append(categoria)

    for palabra, tipo in ARTICULOS.items():
        agregar(palabra, tipo)

    for lista, singular, plural in (
        (SUSTANTIVOS_MASCULINOS, 'SUST_MS', 'SUST_MP'),
        (SUSTANTIVOS_FEMENINOS, 'SUST_FS', 'SUST_FP'),
        (ADJETIVOS_COMUNES, 'ADJ_COMUN_S', 'ADJ_COMUN_P'),
        (VERBOS_TERCERA_PERSONA, 'VERBO_S', 'VERBO_P'),
    ):
        for forma_s, forma_p in _pares(lista):
            agregar(forma_s, singular)
            agregar(forma_p, plural)

    for conjunto in ADJETIVOS_VARIABLES.split():
        formas = conjunto.split('/')
        if len(formas) != 4:
            raise ValueError(f'Adjetivo inválido: {conjunto}')
        for forma, tipo in zip(formas, ('ADJ_MS', 'ADJ_FS', 'ADJ_MP', 'ADJ_FP')):
            agregar(forma, tipo)

    for palabra in ADVERBIOS.split():
        agregar(palabra, 'ADV')
    for palabra in PREPOSICIONES.split():
        agregar(palabra, 'PREP')
    agregar('que', 'QUE')
    return {palabra: tuple(tipos) for palabra, tipos in diccionario.items()}


VOCABULARIO = _crear_vocabulario()
