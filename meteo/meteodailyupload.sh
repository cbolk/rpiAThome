#!/bin/bash

ARPA="datiARPALo_502.csv"
FULLURL="http://meteo.arpalombardia.it/mappe/dati_brevi/"
LPATH="/media/pi/Logs/meteo/"
BPATH="/home/pi/Software/bin/"
EXEC="meteoyesterday.py"

rm "$LPATH$ARPA"
wget "$FULLURL$ARPA" -O "$LPATH$ARPA"
YDAY=$(date --date="yesterday" +"%Y%m%d")
python3 $BPATH$EXEC
mv "$LPATH$ARPA" "$LPATH/rep/$YDAY.csv"

