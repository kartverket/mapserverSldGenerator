mapserverSldGenerator
=====================

Examples of SLDs generated with this tool:

ABAS
* http://labs.kartverket.no/sld/abas/abas.sld
* http://labs.kartverket.no/sld/abas/namedlayers/

Kartdata2
* http://labs.kartverket.no/sld/kartdata2/kartdata2.sld
* http://labs.kartverket.no/sld/kartdata2/namedlayers/


Usage:

	./sldGen.py $mapfile [[ -f $sldFile || -fpl $outputDir ] -g ]
	
Script for mapserver generating SLD including complete FES filters based on mapfile.

Needs mapscript to run.


Loads mapfile and uses layer.generateSLD() from mapscript to write a temporary file.
When it finds a Filter, it tries to generate a new Filter based on the classifications in the mapfile.

Highly recommend running xmllint to validate result:

	xmllint --noout --schema http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd $sldfile
