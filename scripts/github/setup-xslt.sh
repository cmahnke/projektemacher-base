#!/usr/bin/env bash

set -e -o pipefail

# --- Update these as needed (check Maven Central for the latest) ---
SAXON_VERSION="12.5"
RESOLVER_VERSION="5.2.2"
# ---------------------------------------------------------------------

SAXON_URL="https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/${SAXON_VERSION}/Saxon-HE-${SAXON_VERSION}.jar"
RESOLVER_URL="https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/${RESOLVER_VERSION}/xmlresolver-${RESOLVER_VERSION}.jar"

SAXON_DIR="/opt/saxon"
SAXON_SCRIPT="$SAXON_DIR/saxon"

sudo apt update

echo "Installing Java"
RUN_DEPENDENCIES="openjdk-17-jdk curl"
echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install -y $RUN_DEPENDENCIES

sudo mkdir -p "$SAXON_DIR"

SAXON_FILE=$(basename "$SAXON_URL")
RESOLVER_FILE=$(basename "$RESOLVER_URL")

echo "Downloading Saxon $SAXON_VERSION and xmlresolver $RESOLVER_VERSION"
sudo curl -fL "$SAXON_URL" --output "$SAXON_DIR/$SAXON_FILE"
sudo curl -fL "$RESOLVER_URL" --output "$SAXON_DIR/$RESOLVER_FILE"

sudo ln -sf "$SAXON_DIR/$SAXON_FILE" "$SAXON_DIR/saxon.jar"
sudo ln -sf "$SAXON_DIR/$RESOLVER_FILE" "$SAXON_DIR/xmlresolver.jar"

sudo tee "$SAXON_SCRIPT" > /dev/null <<EOF
#!/bin/sh
java -Xmx1024m -cp "$SAXON_DIR/saxon.jar:$SAXON_DIR/xmlresolver.jar" net.sf.saxon.Transform "\$@"
EOF

sudo chmod +x "$SAXON_SCRIPT"

echo "Installed Saxon to $SAXON_DIR:"
ls -al "$SAXON_DIR"
