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

sudo mkdir -p $SAXON_DIR
# Get Saxon
SAXON_FILE=$(basename $SAXON_URL)
RESOLVER_FILE=$(basename $RESOLVER_URL)
sudo curl $SAXON_URL --output $SAXON_DIR/$SAXON_FILE
sudo curl $RESOLVER_URL --output $SAXON_DIR/$RESOLVER_FILE
sudo ln -s $SAXON_DIR/$SAXON_FILE $SAXON_DIR/saxon.jar
sudo ln -s $SAXON_DIR/$RESOLVER_FILE $SAXON_DIR/xmlresolver.jar

sudo printf '#!/bin/sh\njava -Xmx1024m -cp $SAXON_DIR/saxon.jar:$SAXON_DIR/xmlresolver.jar net.sf.saxon.Transform "$@"' > $SAXON_SCRIPT
sudo chmod +x $SAXON_SCRIPT

echo "Installed Saxon to /opt/saxon:"
ls -al /opt/saxon
