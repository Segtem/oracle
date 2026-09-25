#!/bin/bash
E=/home/workstation/Dev/oracle/ejemplo/batalla-naval
O() { python3 /home/workstation/Dev/oracle/tools/cli.py "$@"; }
D=$(mktemp -d); cd $D && O init batalla-naval >/dev/null && cd batalla-naval && cp $E/oracle.json . && mkdir -p corpus/naval catalogos/naval
cp $E/catalogos/naval/*.oracle catalogos/naval/
cp $E/corpus/naval/{005,006,026,027,028,001,002,023,024,025}-*.caso corpus/naval/
echo "--- 11 medidas, 10 casos que fijan sólo 2 de ellas (catalogo_base false)"; O test 2>&1 | grep -E "sobreviv|VEREDICTO|ACEPTACIÓN|sin caso|fijada" | cut -c1-160
sed -i 's/"catalogo_base": false/"catalogo_base": true/' oracle.json
echo "--- lo mismo con catalogo_base true"; O test 2>&1 | grep -E "sobreviv|VEREDICTO|toda_medida_esta_fijada" | cut -c1-160
rm -rf $D
