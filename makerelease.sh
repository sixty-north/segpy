#!/bin/sh
VERSION=0.3

DIR=segypy-$VERSION

mkdir $DIR
cp segypy.py $DIR/.
cp testsegy.py $DIR/.
cp LICENSE $DIR/.
cp README $DIR/.

zip -r $DIR.zip $DIR
tar cvfz $DIR.tgz $DIR

rm -fr $DIR