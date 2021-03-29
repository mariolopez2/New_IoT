#!/usr/bin/env python
# Copyright (c) 2021 Foxconn GDL PCE Paragons Solutions México
# Author: Mario Lopez
# Version: 1.3
# Proyecto: https://github.com/mariolopez2/New_IoT 

import re
import configparser
import socket
import requests
import os
import subprocess
import sys
from time import sleep

#Archivo de configuración Inicial
config = configparser.ConfigParser()
config.read('config.ini')

first_use = bool(config['DEFAULT']['FIRST_USE'])
ip = config['DEFAULT']['IPV4']
gateway = config['DEFAULT']['GATEWAY']
dns = config['DEFAULT']['DNS']
root_mask = config['DEFAULT']['MASK']

new_ip = 0
valid_ip = False
new_gateway = 0
valid_gateway = False
new_dns = 0
valid_dns = False
new_mask = 0
valid_mask = False
resp_valida = False



def mascaraRed(mask):
    if(mask == 8 ):
        return "255.0.0.0"
    elif(mask == 9):
        return "255.128.0.0"
    elif(mask == 10):
        return "255.192.0.0"
    elif(mask == 11):
        return "255.224.0.0"
    elif(mask == 12):
        return "255.240.0.0"
    elif(mask == 13):
        return "255.248.0.0"
    elif(mask == 14):
        return "255.252.0.0"
    elif(mask == 15):
        return "255.254.0.0"
    elif(mask == 16):
        return "255.255.0.0"
    elif(mask == 17):
        return "255.255.128.0"
    elif(mask == 18):
        return "255.255.192.0"
    elif(mask == 19):
        return "255.255.224.0"
    elif(mask == 20):
        return "255.255.240.0"
    elif(mask == 21):
        return "255.255.248.0"
    elif(mask == 22):
        return "255.255.252.0"
    elif(mask == 23):
        return "255.255.254.0"
    elif(mask == 24):
        return "255.255.255.0"
    elif(mask == 25):
        return "255.255.255.128"
    elif(mask == 26):
        return "255.255.255.192"
    elif(mask == 27):
        return "255.255.255.224"
    elif(mask == 28):
        return "255.255.255.240"
    elif(mask == 29):
        return "255.255.255.248"
    elif(mask == 30):
        return "255.255.255.252"
    elif(mask == 31):
        return "255.255.255.254"
    elif(mask == 32):
        return "255.255.255.255"
    else:
        return "Mascara Invalida"

def validarIP(ip):
    try:
        socket.inet_pton(socket.AF_INET,ip)
        return True
    except socket.error:
        return False

def Iniciar():
    if(first_use == True):
        os.system("clear")
        os.system("cat readme.txt")
        mostrarConfig()
        configurar()
    else:
        respuesta_reconfig = False
        while(respuesta_reconfig == False):
            print("YA SE HA CONFIGURADO POR PRIMERA VEZ ESTE DISPOSITIVO")
            print("\n Deseas volver a configurarlo? (S/N): ")
            reconf = input()
            if(reconf == "S" or reconf == "s"):
                respuesta_reconfig = True
                configurar()
            elif(reconf == "N" or reconf == "n"):
                print("\n SALIENDO DEL PROGRAMA")
                respuesta_reconfig = True
            else:
                print("\nOpcion no valida, intenta de nuevo.")


def configurar():
    valid_ip = False
    valid_gateway = False
    valid_dns = False
    valid_mask = False
    resp_valida = False
    comando = "cat /proc/cpuinfo | grep -w Serial | awk '{print $3}'"
    sn_completo = os.popen(comando).read()
    sn_corto = sn_completo[10:16]
    new_hostname = "GDLIOT" + sn_corto

    print("\n POR FAVOR ESTABLEZCA LOS NUEVOS VALORES.")
    while(valid_ip == False):
        print("\n Ingrese por favor la nueva IP: ")
        new_ip = input()
        valid_ip = validarIP(new_ip)
        if(valid_ip):
            print("\n La ip: " + new_ip + " ha sido guardada.")
        else:
            print("\n La ip ingresada no es valida, intenta nuevamente.")
    while(valid_gateway == False):
        print("\n Ingrese por favor el nuevo gateway: ")
        new_gateway = input()
        valid_gateway = validarIP(new_gateway)
        if(valid_gateway):
            print("\n El gateway: " + new_gateway + " ha sido guardado.")
        else:
            print("\n El gateway introducido no es valido, intenta nuevamente.")
    while(valid_dns == False):
        print("Ingrese por favor el nuevo DNS: ")
        new_dns = input()
        valid_dns = validarIP(new_dns)
        if(valid_dns):
            print("El DNS: " + new_dns + " ha sido guardado.")
        else:
            print("El DNS introducido no es valido, intenta nuevamente.")
    while(valid_mask == False):
        print("Ingresa la mascara de red en notacion simplificada (Ejemplo 24  <-- esto es igual a 255.255.255.0): ")
        new_mask = int(input())
        if(new_mask >= 8 and new_mask <= 32):
            print("La mascara introducida ha sido guardada.")
            valid_mask = True
        else:
            print("La mascara introducida no es valida, intenta nuevamente.")

    print("La información introducida es la siguiente: ")
    print("\n NUEVA IP: " + new_ip)
    print("\n NUEVO GATEWAY: " + new_gateway)
    print("\n NUEVO DNS: " + new_dns)
    print("\n NUEVA MASCARA DE RED: " + mascaraRed(new_mask))
    print("\n NUEVO HOSTNAME (RECOMENDADO): " + new_hostname + " <--- ESTE HOSTNAME PUEDE SER CAMBIADO DESPUES")
    print("\n ")
    while(resp_valida == False):
        print("\n DESEAS CONFIRMAR ESTOS DATOS Y REINICIAR LA RASPBERRY? (S/N): ")
        respuesta = input()
        if(respuesta == "S" or respuesta == "s"):
            aplicarCambios(new_ip,new_gateway,new_dns,new_mask)
            cambiarHostname(new_hostname)
            print("\n\n LOS DATOS HAN SIDO GUARDADOS, EN BREVE EL DISPOSITIVO SE REINICIARA PARA QUE SURGAN EFECTO ESTOS CAMBIOS.")
            resp_valida = True
            sleep(10000)
            os.system("sudo reboot")
        elif(respuesta == "N" or respuesta == "n"):
            print("\n\n CAMBIOS DESCARTADOS, CERRANDO PROGRAMA")
            resp_valida = True
        else:
            print("OPCION NO VALIDA, INTENTA DE NUEVO")

def aplicarCambios(ip,gateway,dns,mask):
    file_name = '/etc/dhcpcd.conf'
    with open(file_name, 'r') as f:
        file_text = f.read()

    if len(re.findall('inform', file_text)) == 0:
        newlines = [
            'interface eth0' + '\n',
            'inform ' + ip + '\n',
            'static routers=' + gateway + '\n',
            'static domain_nbame_servers=' + dns + '\n'
        ]
        with open(file_name, 'a+') as f:
            f.writelines(newlines)
    else:
        newlines = []
        with open(file_name) as f:
            lines = f.readlines()
            for l in lines:
                if re.findall('#', l):
                    continue
                elif re.findall('inform [0-9.]*' l):
                    newlines.append('inform ' + ip + '/' + mask + '\n')
                elif re.findall('static routers=', l):
                    newlines.append('static routers=' + gateway + '\n')
                elif re.findall('static domain_name_servers=', l):
                    newlines.append('static domain_name_servers=' + dns + '\n')
                else:
                    newlines.append(l)
        with open(file_name, 'w') as n:
            n.writelines(newlines)

def cambiarHostname(newHostname):
    with open('/etc/hosts', 'r') as file:
        data = file.readlines()
        data[5] = '127.0.1.1    ' + newHostname
        with open('temp.txt', 'w') as file:
            file.writelines(data)

        os.system('sudo mv temp.txt /etc/hosts')

        with open('/etc/hostname', 'r') as file:
            data = file.readlines()

        data[0] = newHostname

        with open('temp.txt', 'w') as file:
            file.writelines(data)
        os.system('sudo mv temp.txt /etc/hostname')

def mostrarConfig():
    sn = os.popen("cat sn.txt").read()
    print("\n INFORMACIÓN ACTUAL DEL DISPOSITIVO")
    print("\n SERIAL NUMBER: " + sn)
    print("\n IP: " + str(ip))
    print("\n GATEWAY: " + str(gateway))
    print("\n MASCARA DE RED: " + mascaraRed(int(root_mask)))
    print("\n DNS: " + dns)
    print("\n ")

def instrucciones():
    print ("Setup.py es un script para configurar el dispositivo, puedes utilizar los siguientes comandos")
    print ("- Ejemplo de uso")
    print ("         python setup.py <comando>")
    print ("- Comandos disponibles")
    print ("         - iniciar   <- Inicia el proceso configuración.")
    print ("         - config    <- Muestra la configuracion actual.")
    print ("         - ayuda o ? <- Muestra las instrucciones de uso.")
    print ("\n")

if __name__ == '__main__':

	if(len(sys.argv) > 1):
		if(sys.argv[1] == "iniciar"):
			Iniciar()
		elif(sys.argv[1] == "ayuda" or sys.argv[1] == "?"):
			instrucciones()
		elif(sys.argv[1] == "config"):
			mostrarConfig()
		else:
			print ("Comando no valido")
			instrucciones()
	else:
		Iniciar()

