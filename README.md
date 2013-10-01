mapserverSldGenerator
=====================

Script for mapserver generating SLD including complete FES filters based on mapfile.

Needs mapscript to run.

Highly recommend running xmllint to validate result:

	xmllint --noout --schema http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd $sldFile
