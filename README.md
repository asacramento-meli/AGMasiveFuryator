Instalacion y creacion del entorno virtual

       sudo zsh monu_instalaciones.sh
Luego teniendo el entorno virtual activo (y si no lo tienen pueden ejecutar este comando) 

        source venv/bin/activate
        
El comando es:

        python agregar_ag_interno.py {token_fury} {archivo de entrada} {archivo_salida} {nombre dee Access group} {ID de access group}
        
Ejemplo: (archivo de entrada)
fbm-wms-nico
fbm-wms-fabi
fbm-wms-maxi
fbm-wms-lucas
fbm-wms-peluca
fbm-wms-motu

Para obtener el ID del Access group yo tuve que inspeccionar los datos en la web de Fury, es el paso mas fiaca la verdad.

Pueden ejecutar el comando las veces que deseen, si ya tienen el AG agregado no va a hacer nada