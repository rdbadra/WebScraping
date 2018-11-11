import numpy as np
import pandas as pd
import time
import requests

from urllib.request import urlopen
from bs4 import BeautifulSoup

def createfile():
    content = ""
    with open("data.csv", "w+") as file:
        file.write(content)

def delay():
    t0=time.time()
    response_delay=time.time()-t0
    time.sleep(10*response_delay)

def get_hrefs(webPage):
    hrefs = []
    provincias = []
    page = requests.get(webPage)
    soup = BeautifulSoup(page.content, features="html.parser")
    cabecera = soup.find('div', attrs={'id':'cabecera'})
    contenedor = cabecera.find('div', attrs={'id':'contenedor'})
    contenedor_contenido = contenedor.find('div', attrs={'class':'contenedor_contenido'})
    contenedor_central = contenedor_contenido.find('div', attrs={'class':'contenedor_central'})
    oculta_enlaces = contenedor_central.find('ul', attrs={'class':'oculta_enlaces'})
    lis = oculta_enlaces.find_all('li')
    for li in lis:
        a = li.find('a')
        hrefs.append(a.get('href'))
        provincias.append(li.get_text())
    return hrefs, provincias

def go_to_next_page(origin, href):
    hrefs_municipio = []
    municipios = []
    nextPage = origin+href
    page = requests.get(nextPage)
    soup = BeautifulSoup(page.content, features="html.parser")
    trs = soup.find_all('tr', attrs={'class':'localidades'})
    for tr in trs:
        tds = tr.find_all('td')
        for td in tds:
            a = td.find('a')
            hrefs_municipio.append(a.get('href'))
            municipios.append(a.get_text())
    return hrefs_municipio, municipios

def insert_data_in_file(csv, precipitaciones, fec_str, municipio, provincia, maxTemp, minTemp, temperaturas, horarios):
    temp = ""
    fechaAqui = ""
    miTemp = ""
    maTemp = ""
    for i in range(12):
        if(i is 0):
            fechaAqui = fec_str[0]
            miTemp = minTemp[0]
            maTemp = maxTemp[0]
        if(i > 0 and i<5):
            fechaAqui = fec_str[1]
            miTemp = minTemp[1]
            maTemp = maxTemp[1]
        if(i > 5 and i < 7):
            fechaAqui = fec_str[2]
            miTemp = minTemp[2]
            maTemp = maxTemp[2]
        if(i >= 7 and i < 9):
            fechaAqui = fec_str[3]
            miTemp = minTemp[3]
            maTemp = maxTemp[3]
        if(i is 9):
            fechaAqui = fec_str[4]
            miTemp = minTemp[4]
            maTemp = maxTemp[4]
        if(i is 10):
            fechaAqui = fec_str[5]
            miTemp = minTemp[5]
            maTemp = maxTemp[5]
        if(i is 11):
            fechaAqui = fec_str[6]
            miTemp = minTemp[6]
            maTemp = maxTemp[6]
        if(i < 5):
            temp = temperaturas[i]
        else:
            temp = ""
        csv.write(municipio+";"+provincia+";"+fechaAqui+";"+horarios[i]+";"+temp+";"+precipitaciones[i]+";"+miTemp+";" + maTemp+";"  +";\n")

def get_data_municipio2(csv, municipio, origin, href, provincia):
    
    fec_str = []
    precipitaciones = []
    horarios = []
    temperaturas = []
    maxTemp = []
    minTemp = []

    dataPage = origin+href
    page = requests.get(dataPage)
    soup = BeautifulSoup(page.content, features="html.parser")
    thead = soup.find('thead')
    fechas = thead.find_all('th')

    # Se cogen las fechas de cada estado temporal

    for fec in fechas:
        fec_str.append(fec.get_text())
    tbody = soup.find('tbody')
    cab = tbody.find('tr', attrs={'class':'cabecera_loc_niv2'})
    ths = cab.find_all('th')
    

    
    
    # Se cogen los datos de los horarios y las temperaturas que habrá en esos horarios
    
    for th in ths:
        if(len(th.find_all('div'))>0):
            horarios.append(th.find_all('div')[0].get_text())
        if(len(th.find_all('div'))>2):
            temperaturas.append(th.find_all('div')[2].get_text())

    
    # Se cogen los datos de probabilidad de precipitaciones por día

    cab = tbody.find_all('tr')
    tds = cab[2].find_all('td')
    for td in tds:
        precipitaciones.append(td.get_text())

    temps = cab[6]
    tempsMax = temps.find_all('span', attrs={'class':'texto_rojo'})
    tempsMin = temps.find_all('span', attrs={'class':'texto_azul'})

    # Se cogen las temperaturas máximas y mínimas de cada día

    for tempMax in tempsMax:
        maxTemp.append(str.strip(tempMax.get_text()))

    for tempMin in tempsMin:
        minTemp.append(str.strip(tempMin.get_text()))

    insert_data_in_file(csv, precipitaciones, fec_str, municipio, provincia, maxTemp, minTemp, temperaturas, horarios)



def get_data_municipio(origin, href):
    dataPage = origin+href
    page = requests.get(dataPage)
    soup = BeautifulSoup(page.content, features="html.parser")
    thead = soup.find('thead')
    fechas = thead.find_all('th')
    tbody = soup.find('tbody')
    cab = tbody.find('tr', attrs={'class':'cabecera_loc_niv2'})
    ths = cab.find_all('th')
    for th in ths:
        #print(th.find_all('div'))
        if(len(th.find_all('div'))>0):
            horario = th.find_all('div')[0].get_text()
        if(len(th.find_all('div'))>2):
            temperatura = th.find_all('div')[2].get_text()

def main():
    csv = open('tiempo_semanal_municipios.csv', "w+")
    csv.write("municipio;provincia;fecha;horario;temperatura_actual;probabilidad_precipitacion;temperatura_minima;temperatura_maxima;\n")
    webPage = "http://www.aemet.es/es/eltiempo/prediccion/municipios"
    origin = "http://www.aemet.es"
    hrefs, provincias = get_hrefs(webPage)
    for i in range(len(hrefs)):
        if(provincias[i] != 'Ceuta' and provincias[i] != 'Melilla'):
            hs, municipios = go_to_next_page(origin, hrefs[i])
            delay()
            for j in range(len(hs)):
                get_data_municipio2(csv, municipios[j], origin, hs[j], provincias[i])
                delay()
            
        else:
            get_data_municipio2(csv, provincias[i], origin, hrefs[i], provincias[i])    
        print("Terminado para "+str(provincias[i]))
        
        
        


main()