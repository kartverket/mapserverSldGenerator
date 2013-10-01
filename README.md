mapserverSldGenerator
=====================

Script for mapserver generating SLD including complete FES filters based on mapfile.

Needs mapscript to run.


Loads mapfile and uses layer.generateSLD() from mapscript to write a temporary file.
It then loads and prints out all but the Filter part.
When it finds a Filter, it tries to generate a new Filter based on the classifications in the mapfile.


Highly recommend running xmllint to validate result:

	xmllint --noout --schema http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd $sldFile
