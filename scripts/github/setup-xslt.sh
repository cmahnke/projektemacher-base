#!/bin/sh

SAXON_URL="https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/12.1/Saxon-HE-12.1.jar"
RESOLVER_URL="https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/5.1.2/xmlresolver-5.1.2.jar"
SAXON_DIR="/opt/saxon"
SAXON_SCRIPT="/opt/saxon/saxon"

sudo apt update

echo "Installing Java"

RUN_DEPENDENCIES="openjdk-17-jdk curl"

echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install $RUN_DEPENDENCIES

mkdir -p $SAXON_DIR
# Get Saxon
SAXON_FILE=$(basename $SAXON_URL)
RESOLVER_FILE=$(basename $RESOLVER_URL)
curl $SAXON_URL --output $SAXON_DIR/$SAXON_FILE
curl $RESOLVER_URL --output $SAXON_DIR/$RESOLVER_FILE
ln -s $SAXON_DIR/$SAXON_FILE $SAXON_DIR/saxon.jar
ln -s $SAXON_DIR/$RESOLVER_FILE $SAXON_DIR/xmlresolver.jar

printf '#!/bin/sh\njava -Xmx1024m -cp $SAXON_DIR/saxon.jar:$SAXON_DIR/xmlresolver.jar net.sf.saxon.Transform "$@"' > $SAXON_SCRIPT
chmod +x $SAXON_SCRIPT
