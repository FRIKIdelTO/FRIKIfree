# -*- coding: utf-8 -*
"""
Creado por FRIKIdelTO (https://www.frikidelto.com)
Este script fue desarrollado siguiendo el excelente tutorial de BocaDePez que publicó en:
https://bandaancha.eu/foros/sustituir-router-digi-fibra-router-1732730/2#r1lf3a
todo el mérito es de él.

Muchas gracias a Manel (@VillaArtista en Telegram) por avisarme de dicho tutorial
y por aclararme dudas durante el desarrollo de este script.
"""

import subprocess
import requests
import netifaces
from pathlib import Path as path
import re
import os
import sys
import time
import datetime

# CONSTANTES
# versión
VERSION = "20.10.31"
# colores
verde = '\33[92m'
amarillo = '\033[93m'
azul = "\033[96m"
magenta = "\033[1m\033[95m"
gris = '\33[90m'
blanco = '\033[1m\033[97m'
rojo = '\33[91m'
# reloj animado
reloj = ('🕐','🕑','🕒','🕓','🕔','🕕','🕖','🕗','🕘','🕙','🕚','🕛')
# contenido para archivo de configuración del servidor PPPoE
configuracion = """\
ms-dns 8.8.8.8 asyncmap 0
noauth
crtscts
lock
hide-password
modem
debug
proxyarp
lcp-echo-interval 10
lcp-echo-failure 2
noipx
plugin /etc/ppp/plugins/rp-pppoe.so
require-pap
ktune
nobsdcomp
noccp
novj
"""
# operadores y su vlan
operadores = (
["DiGi", 20],
["Movistar/Tuenti/O2", 6],
["Vodafone/Lowi", 100],
["NEBA: Vodafone/Lowi", 24],
["Jazztel", 1074],
["MasMovil/PepePhone/Yoigo", 20],
["Orange/Amena", 832],
["Adamo", 603]
)

# POSICIONA EL CURSOR DEL TERMINAL n LÍNEAS ARRIBA
def cursor_arriba(n=1):
	print("\033[%sA"%(n+1,))

# CREA UN CUADRO CON UN TEXTO DENTRO
def cuadro(texto):
    linea = "─"
    caracteres = len(texto) + 2
    print(amarillo + "┌" + linea*caracteres + "┐")
    print(amarillo + "│ " + blanco + texto + amarillo + " │")
    print(amarillo + "└" + linea*caracteres + "┘\n" + gris)

# TERMINA TODOS LOS PROCESOS QUE EJECUTA ESTE SCRIPT
def matar_procesos():
	subprocess.run(['sudo', 'killall', '-q', '-w', 'tshark'])
	subprocess.run(['sudo', 'killall', '-q', '-w', 'pppoe-server'])


# FUNCIÓN QUE MUESTRA UN MENSAJE INDEFINIDAMENTE HASTA QUE HAYA CONEXIÓN A INTERNET
def esperar_internet():
	inicio = datetime.datetime.now()
	internet = False
	formato = 0
	while internet == False:
		try:
			subprocess.check_output(['ping', '-c', '2', '8.8.8.8'], stderr=subprocess.STDOUT, universal_newlines=True)
			internet = True
		except subprocess.CalledProcessError:
			animacion_reloj("ESPERANDO CONEXIÓN A INTERNET", inicio)

# MUESTRA UNA ANIMACIÓN DE UN RELOJ CON EL TEXTO Y EL TIEMPO TRANSCURRIDO
def animacion_reloj(texto, inicio):
	n_total = len(reloj)
	for n in range(n_total): # en cada segundo el icono del reloj da la vuelta entera a las agujas
		segundos = (datetime.datetime.now() - inicio).seconds
		mins, segs = divmod(segundos, 60)
		if segundos < 60:
			formato = '{:2d}      '.format(segs)
			print(blanco + "\033[K   " + reloj[n] + "️  " + amarillo + texto + "...... " + blanco + formato + gris)
		else:
			formato = '{:2d}:{:02d}'.format(mins, segs)
			print(blanco + "\033[K   " + reloj[n] + "️  " + amarillo + texto + "... " + blanco + formato + gris)
		time.sleep(1/n_total)
		cursor_arriba()
		n = n + 1
		if n >= n_total:
			n = 0
			segundos = segundos + 1

# MUESTRA CUANTOS MINUTOS Y SEGUNDOS HAN PASADO DESDE EL TIEMPO INDICADO
def mostrar_tiempo(empieza):
    minutos = 0
    segundos = (datetime.datetime.now() - empieza).seconds # segundos que han pasado en total
    if segundos > 0:
        if segundos >= 60: # si ha tardado 1 minuto o más
            color = rojo # se muestra la información de color rojo (para que destaque más)
        else:
            color = verde # sinó se mostrará de color verde
        minutos = int(segundos / 60) # minutos que han pasado
        segundos = segundos - (minutos * 60) # segundos que quedan al restar los minutos en segundos
        print(verde + "COMPLETADO" + color + " en ",end="")
        if minutos != 0:
            if minutos == 1:
                print(blanco + "1" + color + " minuto",end="")
            else:
                print(blanco + str(minutos) + color + " minutos",end="")
            if segundos != 0:
                print(color + " y ",end="")
        if segundos != 0:
            if segundos == 1:
                print(blanco + "1" + color + " segundo",end="")
            else:
                print(blanco + str(segundos) + color + " segundos",end="")
        else:
            if minutos == 0:
                print(blanco + str(segundos) + color + " segundos",end="")
        print(gris)
    print(gris)
    return minutos, segundos

# MAIN ########################################################################################################

if __name__ == '__main__':
	# limpiamos la pantalla
	os.system("clear")
	# configuramos el teclado en español
	subprocess.run(["sudo", "setxkbmap", "-layout", "'es,es'", "-model", "pc105"])
	# si no tenemos privilegios de superusuario reiniciamos el script con ellos
	if os.geteuid() != 0:
		subprocess.run(['sudo', 'python3', *sys.argv])
		sys.exit()
	# terminamos los posibles procesos que hayan quedado abiertos de una sesión anterior
	matar_procesos()
	# creamos una carpeta de trabajo en home y entramos en ella
	os.chdir(str(path.home()))
	try:
		os.mkdir('FRIKIfree')
	except:
		pass
	os.chdir('FRIKIfree')
	# limpiamos la pantalla y mostramos la versión
	os.system("clear")
	cuadro('FRIKIfree ' + str(VERSION) + " by FRIKIdelTO.com")
	# configuramos el teclado en español
	subprocess.run(["sudo", "setxkbmap", "-layout", "'es,es'", "-model", "pc105"])
	# añadimos el repositorio universe si procede
	archivo = open("/etc/apt/sources.list", "r", encoding="utf-8")
	contenido = archivo.read()
	archivo.close()
	if 'universe' not in contenido:
		print(azul + '\033[K   Añadiendo repositorio "universe"...' + gris)
		esperar_internet()
		subprocess.run(["sudo", "add-apt-repository", "universe"])
	# instalamos Tshark para capturar el tráfico
	print(azul + "\033[K   Instalando " + blanco + "tshark" + azul + "..." + gris)
	try:
		subprocess.check_output(["which", "tshark"])
		print(verde + "\033[K      Ya estaba instalado" + gris)
	except:
		esperar_internet()
		# para que no pregunte durante la instalación
		subprocess.run(["echo", '"wireshark-common wireshark-common/install-setuid boolean true"', "|", "sudo",  "debconf-set-selections"])
		# instalamos tshark
		subprocess.run(["sudo", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install",  "tshark", "--yes"])
	# instalamos lo necesario para compilar nuestro servidor PPPoE
	print(azul + "\033[K   Instalando " + blanco + "RP-PPPoE" + azul + "..." + gris)
	try:
		subprocess.check_output(["which", "pppoe-server"])
		print(verde + "\033[K      Ya estaba instalado" + gris)
	except:
		esperar_internet()
		print(azul + "\033[K      Instalando " + blanco + "ppp" + azul + "..." + gris)
		subprocess.run(["sudo", "apt-get", "install", "ppp", "--yes"])
		print(azul + "\033[K      Instalando " + blanco + "ppp-dev" + azul + "..." + gris)
		subprocess.run(["sudo", "apt-get", "install", "ppp-dev", "--yes"])
		print(azul + "\033[K      Instalando " + blanco + "pppoeconf" + azul + "..." + gris)
		subprocess.run(["sudo", "apt-get", "install", "pppoeconf", "--yes"])
		print(azul + "\033[K      Instalando " + blanco + "build-essential" + azul + "..." + gris)
		subprocess.run(["sudo", "apt-get", "install", "build-essential", "--yes"])
		# descargamos el código fuente del servidor PPPoE
		print(azul + "\033[K      Buscando última versión de " + blanco + "RP-PPPoE" + azul + "..." + gris)
		#    buscamos el enlace de la última versión
		esperar_internet()
		resultado = requests.get('https://dianne.skoll.ca/projects/rp-pppoe/download/').content
		enlaces = re.findall(r'<a href=[\"]?([^\" >]+)', str(resultado))
		encontrado = False
		for enlace in enlaces:
			if "tar.gz" in enlace and ".sig" not in enlace:
				url = 'https://dianne.skoll.ca/projects/rp-pppoe/download/' + enlace
				archivo = enlace
				print(verde + "\033[K         Encontrada: " + blanco + str(archivo) + gris)
				encontrado = True
		if encontrado == False:
			print(rojo + "\033[K         ERROR: No se ha encontrado el archivo necesario" + gris)
			print()
			sys.exit()
		#    descargamos el archivo encontrado
		print(azul + "\033[K      Descargando " + blanco + archivo + gris)
		if path(archivo).is_file() == True:
			print(amarillo + "\033[K      Ya estaba descargado" + gris)
		else:
			esperar_internet()
			subprocess.run(["wget", url])
		#    lo descomprimimos en una carpeta con el mismo nombre
		print(azul + "\033[K      Descomprimiendo " + blanco + archivo + gris)
		carpeta = archivo.replace('.tar.gz','') + "/src"
		if path(carpeta).is_dir() == True:
			print(amarillo + "\033[K         Ya estaba descomprimido" + gris)
		else:
			subprocess.run(["tar", "xvf", archivo])
		#    entramos en la carpeta del código fuente
		os.chdir(carpeta)
		#    iniciamos la configuración
		print(azul + "\033[K      Configurando " + blanco + "RP-PPPoE" + gris)
		subprocess.run(["./configure", '--enable-plugin'])
		#    compilamos RP-PPPoE
		print(azul + "\033[K      Compilando " + blanco + "RP-PPPoE" + gris)
		subprocess.run(["make"])
		print(azul + "\033[K      Compilando " + blanco + "rp-pppoe.so" + gris)
		subprocess.run(["make", "rp-pppoe.so"])
		#    instalamos RP-PPPoE
		print(azul + "\033[K      Instalando " + blanco + "RP-PPPoE" + gris)
		subprocess.run(["sudo", "make", "install"])
	# creamos el archivo options
	print(azul + "\033[K   Configurando servidor PPPoE (options)" + gris)
	try:
		archivo = open("/etc/ppp/options", "w", encoding="utf-8")
		archivo.write(configuracion)
		archivo.close()
		print(verde + "\033[K      Hecho" + gris)
	except Exception as e:
		print(rojo + "\033[K      ERROR" + gris)
		print()
		print(blanco + str(e) + gris)
		print()
		sys.exit()
	# modificamos el archivo pap-secrets
	print(azul + "\033[K   Configurando servidor PPPoE (pap-secrets)" + gris)
	linea = '"Username"' + '\t' + '*' + '\t' + '"p4ssw0rd"' + '\t' + '*' + '\n'
	try:
		archivo = open("/etc/ppp/pap-secrets", "r", encoding="utf-8")
		contenido = archivo.read()
		archivo.close()
		if linea not in contenido: # si no se había modificado anteriormente
			archivo = open("/etc/ppp/pap-secrets", "a", encoding="utf-8")
			archivo.write(linea)
			archivo.close()
		print(verde + "\033[K      Hecho" + gris)
	except Exception as e:
		print(rojo + "\033[K      ERROR" + gris)
		print()
		print(blanco + str(e) + gris)
		print()
		sys.exit()
	# detectamos la interfaz Ethernet
	print(azul + "\033[K   Buscando interfaz Ethernet" + gris)
	interfaz = ""
	todas = netifaces.interfaces()
	for item in todas:
		if item[:3] == "eth" or item[:2] == "en":
			interfaz = item
			break
	if interfaz == "":
		print(rojo + "\033[K      ERROR: No se ha podido detectar la interfaz Ethernet" + gris)
		print()
		sys.exit()
	else:
		print(verde + "\033[K      Encontrada: " + blanco + interfaz + gris)
	# preguntamos por operador de internet para configurar la VLAN
	print()
	print(azul + "LISTA DE OPERADORAS FTTH:" + gris)
	print(azul + "════════════════════════" + gris)
	n = 1
	total = len(operadores)
	for operador in operadores:
		nombre = operador[0]
		vlan = operador[1]
		print(blanco + "[ " + str(n) + " ]  " + amarillo + nombre + magenta + "  (vlan: " + str(vlan) + ")" + gris)
		n = n + 1
	print(blanco + "[ " + str(n) + " ]  " + amarillo + "Introducir VLAN manualmente" + gris)
	print()
	opcion = ""
	while True:
		try:
			opcion = int(input(azul + "\033[KSELECCIONA TU OPERADOR:" + blanco + " "))
			if opcion > 0 and opcion <= n:
				break
			else:
				print(rojo + "   OPCIÓN NO VÁLIDA" + gris)
				time.sleep(1)
				cursor_arriba()
				print('\033[K')
				cursor_arriba(2)
		except KeyboardInterrupt:
			print()
			print()
			print(rojo + "\033[KInterrumpido por el usuario" + gris)
			print()
			sys.exit()
		except:
			print(rojo + "   OPCIÓN NO VÁLIDA: debes introducir un número" + gris)
			time.sleep(1)
			cursor_arriba()
			print('\033[K')
			cursor_arriba(2)
	# si se ha escogido introducción manual de vlan
	vlan = 0
	if opcion == n:
		while True:
			try:
				vlan = int(input(azul + "\033[KINTRODUCE la VLAN:" + blanco + " "))
				break
			except KeyboardInterrupt:
				print()
				print()
				print(rojo + "\033[KInterrumpido por el usuario" + gris)
				print()
				sys.exit()
			except:
				print(rojo + "   VLAN NO VÁLIDA: debes introducir un número" + gris)
				time.sleep(1)
				cursor_arriba()
				print('\033[K')
				cursor_arriba(2)
	else:
		vlan = operadores[opcion-1][1]
	# cambiamos la VLAN
	interfaz_vlan = interfaz + "." + str(vlan)
	print()
	print(azul + "\033[K   Creando interfaz virtual VLAN " + blanco + str(vlan) + azul + ": " + blanco + interfaz_vlan + gris)
	#    eliminamos todas las interfaces virtuales que pudiera haber creadas
	todas = netifaces.interfaces()
	for item in todas:
		if "." in item:
			subprocess.run(["sudo", "ip", "link", "delete", item])
	# creamos la interfaz virtual
	try:
		subprocess.run(["sudo", "ip", "link", "add", "link", interfaz, "name", interfaz_vlan, "type", "vlan", "id", str(vlan)])
		print(verde + "\033[K      Interfaz " + blanco + interfaz_vlan + verde + " creada" + gris)
	except Exception as e:
		print(rojo + "\033[K      ERROR" + gris)
		print()
		print(blanco + str(e) + gris)
		print()
		sys.exit()
	# asignamos una IP a la interfaz virtual
	print(azul + "\033[K   Asignando IP a " + blanco + interfaz_vlan + gris)
	try:
		subprocess.run(["sudo", "ip", "addr", "flush", "dev", interfaz_vlan])
		subprocess.run(["sudo", "ip", "addr", "add", "10.0.0.1/16", "dev", interfaz_vlan])
		print(verde + "\033[K      Hecho" + gris)
	except Exception as e:
		print(rojo + "\033[K      ERROR" + gris)
		print()
		print(blanco + str(e) + gris)
		print()
		sys.exit()
	# levantamos la interfaz virtual
	print(azul + "\033[K   Levantando interfaz " + blanco + interfaz_vlan + gris)
	try:
		subprocess.run(["sudo", "ip", "link", "set", interfaz_vlan, "up"])
		print(verde + "\033[K      Hecho" + gris)
	except Exception as e:
		print(rojo + "\033[K      ERROR" + gris)
		print()
		print(blanco + str(e) + gris)
		print()
		sys.exit()
	# informamos de cómo proceder antes de continuar
	print(gris)
	print(azul + "\033[KYA ESTÁ TODO PREPARADO PARA CAPTURAR EL TRÁFICO DEL ROUTER." + gris)
	print(azul + "\033[KA PARTIR DE ESTE PUNTO YA NO ES NECESARIO ESTAR CONECTADO A INTERNET" + gris)
	print(azul + "\033[KASÍ QUE, SI QUIERES O LO NECESITAS PARA CONTINUAR, PUEDES DESCONECTARTE." + gris)
	print(azul + "\033[KCONECTA UN CABLE DE RED DESDE EL ORDENADOR AL PUERTO WAN DEL ROUTER Y ENCIÉNDELO." + gris)
	print(gris)
	input(blanco + "\033[KPulsa ENTER cuando estés listo... " + gris)
	cursor_arriba()
	matar_procesos()
	# iniciamos el servidor PPPoE
	print(azul + "\033[K   Iniciando servidor PPPoE" + gris)
	try:
		subprocess.run(["sudo", "pppoe-server", "-C", "ftth", "-I", interfaz_vlan, "-N", "256", "-O", "/etc/ppp/options"])
		print(verde + "\033[K      Hecho" + gris)
	except Exception as e:
		print(rojo + "\033[K      ERROR" + gris)
		print()
		print(blanco + str(e) + gris)
		print()
		sys.exit()
	# capturamos el tráfico con Tshark
	print(azul + "\033[K   Iniciando captura de tráfico de red" + gris)
	try:
		subprocess.Popen(["sudo", "tshark", "-i", interfaz_vlan, "-T", "text"], stdout=open(str(path.home()) + "/FRIKIfree/captura.txt", "wb"), stderr=open(os.devnull, 'w'))
		print(verde + "\033[K      Hecho" + gris)
	except Exception as e:
		print(rojo + "\033[K      ERROR" + gris)
		print()
		print(blanco + str(e) + gris)
		print()
		sys.exit()
	print()
	usuario = ""
	password = ""
	inicio = datetime.datetime.now()
	while usuario == "" and password == "":
		try:
			# mostramos animación de reloj con el tiempo transcurrido
			animacion_reloj("BUSCANDO...", inicio)
			archivo = open(str(path.home()) + "/FRIKIfree/captura.txt", "r", encoding="utf-8")
			for linea in archivo:
				if 'Authenticate-Request' in linea:
					try:
						usuario = re.search(r'Peer-ID=\'([\@A-Za-z0-9_\./\\-]*)\'', linea).group(1)
					except:
						pass
					try:
						password = re.search(r'Password=\'([\@A-Za-z0-9_\./\\-]*)\'', linea).group(1)
					except:
						pass
					if usuario != "" and password != "":
						print('\033[K')
						print(amarillo + "\033[K¡¡¡ CREDENCIALES PPPoE ENCONTRADAS !!!" + gris)
						print('\033[K')
						print(verde + "\033[KUsuario.....: " + blanco + str(usuario) + gris)
						print(verde + "\033[KContraseña..: " + blanco + str(password) + gris)
						print('\033[K')
						mostrar_tiempo(inicio)
						print('\033[K')
						break
			archivo.close()
		except KeyboardInterrupt:
			print(rojo + "\033[KInterrumpido por el usuario" + gris)
			print('\033[K')
			sys.exit()
		except:
			pass
	print(gris + "\033[KDeteniendo captura" + gris)
	matar_procesos()
	cursor_arriba()
	print(azul + "\033[KCaptura detenida" + gris)
	print()
	print()
	sys.exit()
	
