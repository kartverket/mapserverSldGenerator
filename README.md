mapserverSldGenerator
=====================

Script for mapserver generating SLD including complete filters based on mapfile.

Highly recommend running xmllint to validate result:

	xmllint --noout --schema http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd $sldFile
