# # selenium 4
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import pdb

# service=Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service)

# driver.get("https://www.congreso.gob.pe/departamentocomisiones/leyes-aprobadas/")

# 8,104 laws

from typing import Any, List, Optional, Sequence
import os
import pdb
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

class Crawler():
    """Class for traverse congress information and access law descriptions and content."""
    class Law(object):
        def __init__(self, values):
            self.values = values
            self.crawl_law_description(values['url_description'])
        
        def crawl_law_description(self, url: str):
            if url is None or url == '':
                return
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            
            elements = soup.find_all('input')
            dict_elements = {}
            for element in elements:
                dict_elements[element['name']] = element['value']

            try:                
                self.values['estado_ley'] = dict_elements['CodUltEsta']
                self.values['titulo_ley'] = dict_elements['TitIni']
                self.values['objetivo_ley'] = dict_elements['SumIni']            
                self.values['codigo_ley'] = dict_elements['CodIni']
                self.values['periodo_parlamentario'] = dict_elements['DesPerio_1']
                self.values['legislatura'] = dict_elements['DesLegis']
                # month/day/year
                self.values['fecha_presentacion'] = dict_elements['FecPres']
                self.values['proponente'] = dict_elements['DesPropo']
                # both below are empty strings if the proponent is the Executive 
                self.values['grupo_parlamentario'] = dict_elements['NombredelGrupoParlamentario']
                self.values['autores'] = dict_elements['NomCongre'].split(',')
                self.values['url_pdf'] = dict_elements['NombreDelEnlace']
                # a law can be analized by more than 1 comission
                self.values['nombre_comision'] = dict_elements['NombreDeLaComision'].split(',')
                self.values['sesion'] = dict_elements['sesion']
            except KeyError:
                raise Exception(f"Not all entries are defined in law: {self.values['url_description']}.\nElement: {element}")
            return

    def __init__(self, root_data: str):
        self.root_data = root_data
        return
    
    def process_comission_laws(self, file_path):
        df = pd.read_csv(file_path, delimiter='\t', header=None)
        return df

    def read_html_table_laws(self, file_path):
        """Traverse and read the laws contained in the html table, a law per row"""
        
        html_file = open(file_path, "r").read()
        soup = BeautifulSoup(html_file, features="html.parser")
        elements = soup.find_all('td')

        # 4 columns in local html page, each one is a bs4's Tag element
        #   [code, status, date, title]
        rows = []
        for i in range(0, len(elements), 4):
            # the .text attribute leaves only the visible content of an HTML element
            url         = elements[i].find('a')['href'].strip() 
            code        = elements[i].find('a').text.strip()
            status      = elements[i+1].text.strip()
            date        = elements[i+2].text.strip()
            title       = elements[i+3].text.strip()

            values = {
                'url_description': url,
            }
            law = self.Law(values)
            rows.append(law.values)      
        return rows

    def write_jsonl(self, list_dic, file_path):
        with open(file_path, 'w', encoding='utf8') as f:
            for d in list_dic:
                json.dump(d, f)
                f.write('\n')
        
    def run_crawling(self):
        """Traverse all the html files, each one containing a list of laws discussed by congress in 
        a given year"""        
        raw_folder = os.path.join(self.root_data, 'raw')
        crawl_folder = os.path.join(self.root_data, 'crawled')
        files = [x for x in os.listdir(raw_folder) if x.endswith('.html')]   
        
        pbar = tqdm(files)
        for file_name in pbar:
            file_path = os.path.join(raw_folder, file_name)
            pbar.set_description(f'Reading file: {file_path}') 
            #file_path = os.path.join(raw_folder, 'May_2017.html')
            rows = self.read_html_table_laws(file_path)
            laws_path = os.path.join(crawl_folder, file_name+'.jsonl')
            self.write_jsonl(rows, laws_path)
        return 
    
    def describe_laws(self, df):
        """
        Laws donloaded from: https://www.congreso.gob.pe/departamentocomisiones/leyes-aprobadas/ 
        Legislation process: https://lpderecho.pe/como-crea-ley-peru/
            1. Iniciativa legislativa:
                - Una ley es una norma jurídica general dictada por el Parlamento
                - 3 tipos de leyes pueden crearse: ordinarias, orgánicas y de reforma constitucional
                - Solo el Congreso tiene potestad de hacer y aprobar leyes. Pero los otros poderes del Estado, las instituciones públicas autónomas, los gobiernos regionales, los gobiernos locales, y los colegios profesionales también cuentan con iniciativa legislativa
                - Los ciudadanos, que representen un 0.3 % de la población electoral con firmas comprobadas por la autoridad electoral, pueden proponer una ley
            2. Estudios en comisiones:
                - Tipos de comisiones: ordinarias, de invetigacion, especiales, etica parlamentaria
                - Las comisiones se dividen en:
                    - Agraria
                    - Ciencia, innovación y tecnología
                    - Comercio exterior y turismo
                    - Constitución y reglamento
                    - Cultura y patrimonio cultural
                    - Defensa del consumidor y organismos reguladores de los servicios públicos
                    - Defensa nacional, orden interno, desarrollo alternativo y lucha contra las drogas
                    - Descentralización, regionalización, gobiernos locales y modernización de la gestión del Estado
                    - Economía, banca, finanzas e inteligencia financiera
                    - Educación, juventud y deporte
                    - Energía y minas
                    - Fiscalización y contraloría
                    - Inclusión social y personas con discapacidad
                    - Inteligencia
                    - Justicia y derechos humanos
                    - Mujer y familia
                    - Presupuesto y cuenta general de la República
                    - Producción, micro y pequeña empresa y cooperativas
                    - Pueblos andinos, amazónicos y afroperuanos, ambiente y ecología
                    - Relaciones exteriores
                    - Salud y población
                    - Trabajo y seguridad social
                    - Transportes y comunicación
                    - Vivienda y construcción                
            3. Dictamen de comisiones:             
                - Cinco posibles escenarios de acuerdo con el artículo 70 del reglamento del congreso.
                    - Dictámenes en los que se recomienda la aprobación del proyecto en todos sus términos.
                    - Dictámenes en los que se recomienda la aprobación del proyecto y se agrega un proyecto sustitutorio.
                    - La propuesta es rechazada y se envía al archivo, lo cual no requiere un dictamen.
                    - Se recomienda la creación de una comisión especial de estudio sobre la materia en cuestión.
                    - Se solicita una extensión del plazo para emitir el dictamen.
            4. Debate en el pleno del Congreso: 
                - Pueden prevalecer solamente dos resultados: aprobado o rechazado (enviado al archivo)
                - Para aprobar una ley ordinaria, se exige solo mayoría simple: la mitad de los congresistas presentes a la hora de votar
                - Las leyes orgánicas, leyes que regulan el funcionamiento de las instituciones públicas, se exige el voto de la mitad más uno del número legal de congresistas. En otras palabras, 66 votos de 130
                - Las leyes de reforma constitucional, debido a su poder para modificar la Constitución, pueden ser aprobadas por una votación favorable de 66 congresistas. Y a eso se suma la ratificación en referéndum.
                - Se puede omitir el referéndum si es que el proyecto de reforma constitucional es aprobado por dos tercios del número legal de congresistas en dos legislaturas ordinarias sucesivas.
                - Cada año hay dos legislaturas ordinarias separadas por un receso y en cada legislatura se producen decenas de sesiones del pleno
            5. Aprobacion: 
            6. Autografa: 
                - El proyecto de ley aprobado pasa a la oficina especializada de la Oficialía Mayor, donde se redactará la autógrafa
                - La autógrafa es el documento que representa el cuerpo de la ley
            7. Remision:
            8. Promulgar:
                - Según el artículo 108 de la Constitución Política del Perú, cada ley aprobada por el Congreso es enviada al presidente de la República para que la promulgue dentro de un plazo de 15 días
                - Promulgar una ley se entiende como darle validez, hacerla oficial y depende exclusivamente del presidente
                - El presidente no está obligado a promulgar la ley de forma automática
                    - El presidente promulgue la ley y esta entra en vigencia al día siguiente de su publicación en El Peruano
                    - El presidente ni la promulgue ni la observe dentro de los 15 días que cuenta como plazo. En ese caso, la responsabilidad se traslada al presidente del Congreso o el presidente de la Comisión Permanente
                    - Que el presidente observe la ley dentro de los 15 días que tiene para promulgarla. Esto genera tres posibles resultados:
                        a. La ley es sometida a votación tal como fue aprobada antes de las observaciones del presidente. Así, en caso de que la ley obtenga más de la mitad de los votos del número legal de congresistas, esta es promulgada por el presidente del Congreso. En caso contrario, no se aprueba la ley.
                        b. A la ley se le incorporan las observaciones del presidente y es aprobada por más de la mitad del número legal de congresistas. El presidente del Congreso es el que promulga la ley modificada.
            9. Pulblicacion en El Peruano:
                - La ley entra en vigencia desde el día siguiente de su publicación en el diario oficial El Peruano.


        estado_ley
        Al Archivo                      5030 <--
        Publicado El Peruano            2165 <--
        Presentado                       362
        Retirado                         155
        En comisión                      147
        Dictamen Negativo                 66 <--
        Orden del Día                     61
        Dictamen                          55
        Autógrafa                         13        
        Observado                         11 <--
        Rechazado de Plano                10
        Aprobado                           8
        En comisiˇn                        4
        Dispensado 2da. votación           3
        Se inhibe                          3
        En comisiµn                        2
        Reconsideración                    1
        Orden del DŪa                      1
        Anulado                            1
        Aprobado en Primera Votación       1
        Orden del DÌa                      1
        Orden del DÝa                      1
        En comisi¾n                        1
        Devuelto                           1
        En comisiůn                        1
        """
        label_counts = laws_df['estado_ley'].value_counts()

        # laws_df[laws_df['estado_ley'] == 'Al Archivo'].url_description.tolist()
        # laws_df['nombre_comision'].explode().value_counts().index.tolist()
        # laws_df['nombre_comision'].explode().value_counts().values
        print(label_counts)
    
    def create_df(self, root_path):
        jsonl_filenames = [x for x in os.listdir(root_path) if x.endswith('.jsonl')]
        
        laws = []
        for f_name in jsonl_filenames:
            with open(os.path.join(root_path, f_name)) as f:
                rows = [json.loads(line) for line in f]
                laws.extend(rows)
                break
        
        laws_df = pd.DataFrame(laws)
        n_laws = laws_df['codigo_ley'].nunique()
        print(f"Dataframe contains {n_laws:,.0f} unique law descriptions out of {len(laws_df):,.0f} entries.")
        pdb.set_trace()
        return laws_df

if __name__ == '__main__':
    root_data = './data/peru/laws'
    
    crawler = Crawler(root_data=root_data)
    #crawler.run_crawling()

    jsonl_path = os.path.join(root_data, 'crawled')
    laws_df = crawler.create_df(jsonl_path)


