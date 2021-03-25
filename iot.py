# Copyright (c) 2021 Foxconn GDL PCE Paragons Solutions México
# Author: Mario Lopez
# Version: 1.1
# Proyecto: https://github.com/mariolopez2/New_IoT 

#Librerias Adafruit para utilizar la pantalla OLED - Más información (https://learn.adafruit.com)
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import socket
import requests
import os
import subprocess
import sys

from gpiozero import Button
from gpiozero import LED
from time import sleep


#Variable para red
nombre_equipo = socket.gethostname()
conexion_estado = "No Conectado"

#Variable para LED
led = LED(17)

#Variables para  Boton
button = Button(18) # GPIO Pin

#Variable para Camara
camara_estado = "No conectada"

#Inicializar Pantalla 
RST = None
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin() #Inicializar pantalla
disp.clear() #Limpiar pantalla
disp.display() #Mostrar pantalla
ancho = disp.width
largo = disp.height
image = Image.new('1', (ancho,largo))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,ancho,largo), outline=0, fill=0)
padding = -2
top = padding
bottom = largo-padding
x = 0
font = ImageFont.load_default()	


# Se lee el resultado del comando y retorna el resultado
def obtenerIP():
	comando = "ifconfig eth0 | grep -w inet | awk '{print $2}'"
	return os.popen(comando).read()


# Se valida mediante el comando de auto-detect cuantos dispositivos hay conectados
# si no existe ningun dispositivo conectado el resultado será 2, si hay 1 o más
# dispositivos conectados serán 3 o mas.
def comprobarCamara():
	conteo = 0
	os.system('gphoto2 --auto-detect > gphoto2_resultado')
	conteo = int(os.popen('cat gphoto2_resultado | wc -l').read())
	if conteo > 2:
		return "Conectada"
	else:
		return "No conectada"

# Revisa conexion hacia el host que se le indique
# host = se refiere al host al que intentara probar la conexion
# timeo = es el timeout que tiene antes de dejar de intentarlo
def probarConexion(host,timeo):
	try:
		request = requests.get(host,timeout=timeo)
	except (requests.ConnectionError, requests.Timeout):
		return "No conectado"
	else:
		return "Conectado"

# Funcion creada para facilitar escribir en la pantalla OLED
# mensaje = Texto que se deseas imprimir en la pantalla
# y = es la posicion en el eje Y (Rango de 0 a 64)
def printd(mensaje,y):
	draw.text((x,top+y), mensaje, font=font, fill=255)

def subirFotos():
	draw.rectangle((0,0,ancho,largo), outline=0, fill=0)
	disp.clear()
	print("SUBIENDO FOTOS")
	printd("SUBIENDO ARCHIVOS",32)
	disp.image(image) 
	disp.display()
	os.system("gphoto2 --get-all-files")
	subprocess.call("mv /home/pi/New_IoT/*!(iot.py) /home/pi/New_IoT/Fotos_IOT/")

def Iniciar():
	#Limpiar consola
	os.system('clear')
	#Limpiar pantalla
	disp.clear()
	try:
		while True:
			draw.rectangle((0,0,ancho,largo), outline=0, fill=0)
			camara_estado = comprobarCamara()
			conexion_estado = probarConexion("https://office365.com",5)
			printd("----- INFO DE IOT -----",0)
			printd("IP: " + obtenerIP(),8)
			printd("Host: " + nombre_equipo,16)
			printd("Conexion: " + conexion_estado,24)
			printd("Camara: " + camara_estado,32)

			# Validar que la camara este conectada y haya salida a internet.
			# POSIBLE integración de BD para guardar registro.
			if camara_estado == "Conectada" and conexion_estado == "Conectado":
				print("Puede iniciar el proceso de subida de fotografias")
				printd("PUEDE INICIAR",48)
				printd("EL PROCESO",56)
				led.on()
				if button.is_pressed:
					subirFotos()
			else:
				printd("NO DISPONIBLE",40)
				printd("REVISE QUE LA CAMARA",48)
				printd("ESTE ENCENDIDA",56)
				led.off()

			disp.image(image) 
			disp.display()
			sleep(1)
	except KeyboardInterrupt:
		print ("Programa terminado por el usuario.")
		printd("PROGRAMA DETENIDO",32)
		printd("INTERRUMPIDO",40)
		disp.image(image) 
		disp.display()
		
		
def Parar():
	printd("PROGRAMA DETENIDO",54)
	printd("PLANEADO",63)
	os.system('sudo pkill -f' + str(sys.argv[0]))


def instrucciones():
	print ("Para poder utilizar el iot.py es necesario ingresar un comando")
	print ("- Ejemplo de uso")
	print ("         python iot.py <comando>")
	print ("- Comandos disponibles")
	print ("         - start   <- Inicia el proceso de monitoreo de la red.")
	print ("         - stop    <- Detiene el proceso de monitoreo de la red.")
	print ("         - ?       <- Muestra las instrucciones de uso.")
	print ("\n")


if __name__ == '__main__':

	if(len(sys.argv) > 1):
		if(sys.argv[1] == "start"):
			Iniciar()
		elif(sys.argv[1] == "stop"):
			Parar()
		elif(sys.argv[1] == "?"):
			instrucciones()
		else:
			print ("Comando no valido")
			instrucciones()
	else:
		Iniciar()
