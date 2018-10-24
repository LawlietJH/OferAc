
# Genera Una Base de Datos Con Una Tabla Por Centro Universitario
# para extraer datos de la Oferta Academica y colocarlos en su respectiva Tabla.

# Version Python: 2 y 3.
# Nombre:OferAc (Scrapper de la Oferta Academica).
# By: LawlietJH.

from bs4 import BeautifulSoup		# Dependencia: python -m pip install bs4
import xlsxwriter					# Dependencia: python -m pip install xlsxwriter
import requests						# Dependencia: python -m pip install requests
import os, sys, copy

reload(sys)  
sys.setdefaultencoding('utf8')

class ScrapperOferAc:
	
	Campos = [
		'NRC', 'Clave', 'Materia', 'Seccion', 'Creditos',
		'Cupo_Maximo', 'Cupo_Disponible', 'Horario', 'Dias',
		'Edificio', 'Aula', 'Periodo', 'Nombres', 'Apellidos'
	]
	
	URLOferta = 'consulta.siiau.udg.mx/wco/sspseca.consulta_oferta?'
	
	def __init__(self, Tabla, CU):
		
		self.ParametrosGenerales = 'ciclop=201820&cup='+CU+'&mostrarp=7000'
		self.Tabla = Tabla
	
	#===================================================================
	#===================================================================
	#===================================================================
	
	def pause(self, quiet=True): os.system('Pause > Nul' if quiet else 'Pause')
	
	def replaceAll(self, List, actual, reemplazo):
		
		Lista = copy.deepcopy(List)
		Extraer = [(i, Lista[i]) for i in range(len(Lista))]
		
		for pos, elem in Extraer:
			if elem == actual: Lista[pos] = reemplazo
		
		return Lista
	
	def deleteAll(self, List, eliminar):
		
		Lista = copy.deepcopy(List)
		
		while eliminar in Lista:
			Lista.remove(eliminar)
		
		return Lista
	
	def deleteAllNumbers(self, List):
		
		Lista = copy.deepcopy(List)
		Extraer = [(i, Lista[i]) for i in range(len(Lista))]
		
		for pos, elem in Extraer:
			if str(elem).isdigit():
				Lista[pos] = ''
		
		return self.deleteAll(Lista, '')
	
	def normalizeName(self, nombre):
		profesor = nombre.split(', ')[::-1]
		try: profesor = [profesor[0].title(), profesor[1].title()]
		except: pass
		return profesor
	
	def normalizeTime(self, str):
		
		str = str.split('-')
		str1 = str[0][:2] + ':' + str[0][2:]
		str2 = str[1][:2] + ':' + str[1][2:]
		str = str1 + '-' + str2
		
		return str
	
	def normalizeDays(self, strr):
		
		strr = strr.split('.')
		strr = list(map(lambda x: x.strip(), strr))
		strr = self.deleteAll(strr, '')
		strr = ','.join(strr)
		
		strr = strr.replace('L','Lunes')
		strr = strr.replace('M','Martes')
		strr = strr.replace('I','Miercoles')
		strr = strr.replace('J','Jueves')
		strr = strr.replace('V','Viernes')
		strr = strr.replace('S','Sabado')
		strr = strr.replace('D','Domingo')
		
		return strr
	
	def prettyData(self, DatosParte1, DatosParte2, DatosParte3):
		
		Datos1 = copy.deepcopy(DatosParte1)
		Datos2 = copy.deepcopy(DatosParte2)
		Datos3 = copy.deepcopy(DatosParte3)
		
		# tilte() toma la cadena la convierte a mayuscula la primer letra de cada palabra y minusculas las demas.
		Datos1[2] = Datos1[2].title()
		
		# Cambia los datos vacios de las Tablas por null y quitamos el Ses.
		for z in range(len(Datos2)):
			Datos2[z] = self.replaceAll(Datos2[z], '\xa0', '')
			Datos2[z] = Datos2[z][1:]						#Quita Ses
			Datos2[z][0] = self.normalizeTime(Datos2[z][0])
			Datos2[z][1] = self.normalizeDays(Datos2[z][1])
		
		# Coloca el nombre de profesor primero por nombres y luego por apellidos y quitamos el Ses.
		data = []
		
		for z in range(len(Datos3)):
			if not Datos3[z].isdigit():
				if not '' == Datos3[z]:
					Datos3[z] = self.normalizeName(Datos3[z])
		
		Datos3 = self.deleteAllNumbers(Datos3)				#Quita Ses
		
		return Datos1, Datos2, Datos3
	
	#===================================================================
	#===================================================================
	#===================================================================
	
	
	def insertDataInXLS(self, Valores, worksheet):
		
		row = 0
		col = 0
		
		for x in self.Campos:
			
			worksheet.write(row, col, x)
			col += 1
		
		for x in Valores:
			
			col = 0
			row += 1
			
			for y in x:
				
				worksheet.write(row, col, y)
				col += 1
			

	
	def setDataInXLS(self, worksheet):
		
		DatosParte1 = []
		DatosParte2 = []
		DatosParte3 = []
		ListaTemp = []
		Datos = []
		XLS = []
		cont = 0
		URL = 'http://' + self.URLOferta + self.ParametrosGenerales
		# URL = 'http://consulta.siiau.udg.mx/wco/sspseca.consulta_oferta?ciclop=201820&cup=D&crsep=IT342'
		
		Req = requests.get(URL)
		Estado = Req.status_code
		
		print('\n\n\t [+] URL: \n\n ' + URL)
		print('\n\n\t [+] Extrayendo Datos de la pagina.')
		
		if Estado == 200:
			
			Soup = BeautifulSoup(Req.text, 'html.parser')
			Datos_1 = Soup.find_all('tr',{'style':'background-color:#e5e5e5;'})
			Datos_2 = Soup.find_all('tr',{'style':'background-color:#FFFFFF;'})
			
			print('\n\n\t [+] Ordenando los datos...')
			
			for x in range(len(Datos_1)):
				Datos.append(Datos_1[x])
				try: Datos.append(Datos_2[x])
				except: break
				
			print('\n\n\t [+] Insertando Datos en la Tabla {}.\n\n'.format(self.Tabla))
			
			for x in range(len(Datos)):
				
				DatosParte1 = []
				DatosParte2 = []
				DatosParte3 = []
				ListaTemp = []
				Tabla1, Tabla2 = [], []
				
				TD = Datos[x].find_all('td')
				TR = Datos[x].find_all('tr')
				lenTD = len(TD)
				lenTR = len(TR)
				
				cont += 1
				
				for y in TR:
					val = self.deleteAll(str(y.text).split('\n'), '')
					if len(val) == 1: Tabla1.append(val[0])
					else: Tabla2.append(val)
				
				for y in TD:
					if not '\n' in str(y): ListaTemp.append(str(y.text))
				
				# Datos Parte 1: NRC, Clave, Materia, Seccion, Creditos, Cupo_Maximo y Cupo_Disponible.
				DatosParte1 = ListaTemp[:7]
				# Tablas Con: Ses, Horario, Dias, Edificio, Aula y Periodo:
				DatosParte2 = [ListaTemp[(7*z)-(z-1):7+(6*z)] for z in range(1, len(Tabla1)+1)]
				# Datos Parte 3: Ses y Profesor.
				DatosParte3 = ListaTemp[7+(6*len(Tabla1)):]

				# Arreglamos los datos para guardar en la DB:
				val = self.prettyData(DatosParte1, DatosParte2, DatosParte3)
				
				DatosParte1 = val[0]
				DatosParte2 = val[1]
				DatosParte3 = val[2]
				
				if len(Tabla1) == 0 and len(Tabla2) == 0:
					
					Dat = DatosParte1 + ['','','','','', '', '']
					
					XLS.append(Dat)
					
				elif len(Tabla1) == 0 and len(Tabla2) >= 1:
					for z in range(len(Tabla2)):
						
						Dat = DatosParte1 + ['','','','',''] + DatosParte3[z]
						
						XLS.append(Dat)
						
				elif len(Tabla1) >= 1 and len(Tabla2) == 0:
					for z in range(len(Tabla1)):
						
						Dat = DatosParte1 + DatosParte2[z] + ['','']
						
						XLS.append(Dat)
						
				else:
					for z in range(len(Tabla2)):
						for y in range(len(Tabla1)):
							if Tabla1[y][:2] == Tabla2[z][0]:
								
								Dat = DatosParte1 + DatosParte2[y] + DatosParte3[z]
								
								XLS.append(Dat)
				
				sys.stdout.write('\r [+] Cargando Registros: {} de {}        '.format(x+1, len(Datos)))
				
				# ~ self.pause()
			self.insertDataInXLS(XLS, worksheet)
			print('\n\n\t [+] Terminada Tabla: {}'.format(self.Tabla))
		else:
			print('\n\n [-] No se logro conectar con la pagina, intentelo de nuevo...')
			return


CUs = {
	
	# 'CUAAD':'A',
	# 'CUCBA':'B',
	# 'CUCEA':'C',
	'CUCEI':'D',
	# 'CUCS':'E',
	# 'CUCSH':'F',
	# 'CU_ALTOS':'G',
	# 'CU_CIENEGA':'H',
	# 'CU_COSTA':'I',
	# 'CU_COSTA_SUR':'J',
	# 'CU_SUR':'K',
	# 'CU_VALLES':'M',
	# 'CU_NORTE':'N',
	# 'CU_LAGOS':'U',
	# 'CU_TONALA':'Z'
}



if __name__ == '__main__':
	
	workbook = xlsxwriter.Workbook('xD.xlsx')
	
	for key, elems in CUs.items():
		
		worksheet = workbook.add_worksheet(key)
		ScrapperOferAc(key, elems).setDataInXLS(worksheet)
		
	workbook.close()
