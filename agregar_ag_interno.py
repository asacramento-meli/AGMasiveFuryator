import time
import logging
import requests
import csv
from collections import OrderedDict
import sys

logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s-%(message)s-',
                    level=logging.INFO)

API_INTERNAL_URL = "https://catalog.furycloud.io/"


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='*'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration  -Required  : current iteration (Int)
        total      -Required  : total iterations (Int)
        prefix     -Optional  : prefix string (Str)
        suffix     -Optional  : suffix string (Str)
        decimals   -Optional  : positive number of decimals in percent complete (Int)
        length     -Optional  : character length of bar (Int)
        fill       -Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length-filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def get_offline_response(path):
    if str(path).endswith("/"):
        path = path[:-1]
    archivo = 'docs/' + str(path).replace("/", "_") + '.json'
    import json
    # TODO Arreglar esta cosita mal hecha
    data = [json.loads(line) for line in open(archivo, 'r')][0]
    return data


class Client():
    def api_get(self, path, base_url=None, params={}, headers={}):
        if base_url is None:
            try:
                consulta = requests.get(url=API_INTERNAL_URL + path, params=params, headers=headers)
            except Exception as e:
                logging.error("Error en consulta a shipping con parametros %s" % str(params))
                consulta = {}
                consulta['status_code'] = 'cualquiera'
        else:
            consulta = requests.get(url=base_url + path, params=params, headers=headers)
        if consulta.status_code == 200:
            resultados = consulta.json(object_pairs_hook=OrderedDict)
            return resultados
        else:
            raise Exception("Error en consulta : %s a %s" % (consulta.reason, path))

    def api_post(self, path, params=None, json=None, base_url=None, headers={}):
        if base_url is None:
            consulta = requests.post(url=API_INTERNAL_URL + path, data=params, json=json,
                                     headers=headers)
        else:
            consulta = requests.post(url=base_url + path, data=params, json=json, headers=headers)
        return consulta.json()

    def api_options(self, path, params=None):
        if params is None:
            params = {}
        consulta = requests.options(url=API_INTERNAL_URL + path, data=params, headers={})
        if consulta.status_code == 200:
            res = consulta.json()
            return res
        else:
            raise Exception("Error en consulta : %s" % consulta.reason)


# Obtengo los parametros
token = sys.argv[1]
archivo = sys.argv[2]
ag = sys.argv[3]
ag_id = sys.argv[4]

if not token or not archivo or not ag or not ag_id:
    raise Exception("Se debe ingresar token, archivo, access group y ID de access group")


def tiene_ag(reglas, nueva):
    tiene_la_nueva = False
    for regla in reglas:
        if regla['access_group']['name'] == nueva:
            tiene_la_nueva = True
    return tiene_la_nueva


try:
    inicio = time.time()
    rest = Client()
    with open(archivo, 'r') as entrada:
        lector = csv.reader(entrada)
        for lectura in lector:
            aplicacion = lectura[0]
            params = {
                "application": aplicacion
            }
            headers = {
                        "x-application": aplicacion,
                    "x-auth-token": token
            }
            try:
                datos = rest.api_get('endpoints', API_INTERNAL_URL, params=params, headers=headers)['endpoints']
                if datos.__len__() == 0:
                    logging.info("%s no aplica" % aplicacion)
                    continue
                print_progress_bar(0, datos.__len__())
                i = 0
                for dato in datos:
                    if not tiene_ag(dato['rules'],"internal_stock-fbm_wms-all"):
                        payload_data = {
                            "application":aplicacion,
                            "visibility":"public",
                            "public_path":dato["path"],
                            "description":"Internal use",
                            "status":"pending",
                            "alias":"mercadolibre",
                            "pr_id":None,
                            "service_domain_id":dato['application_id'],
                            "endpoint_id":dato['id'],
                            # OJO hardcodeado
                            "access_group_id":770,
                            "access_group_name":"internal_stock-fbm_wms-all"
                        }
                        rest.api_post('rules',json=payload_data, headers=headers)
                logging.info("Termino %s" % aplicacion)
            except Exception as e:
                logging.error(e)

except Exception as e:
    logging.error(e)
