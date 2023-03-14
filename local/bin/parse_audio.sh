#!/bin/bash

LABEL_FILE='labels.txt'
CONT_FILE='contents.txt'
python parse_audio.py
cd splits
FILES=`ls -1`
for f in $FILES; do
	BFILE=`basename $f '.wav'`
	TXT=$BFILE.txt
	paddlespeech asr --input $f > $TXT
	CONT=`cat $TXT`
	NOTE=`python py.py $CONT`
	#echo $NOTE > $TXT
	echo $BFILE\|$NOTE >> $LABEL_FILE
	echo $BFILE\|$CONT >> $CONT_FILE
done
