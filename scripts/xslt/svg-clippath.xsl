<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                              xmlns:svg="http://www.w3.org/2000/svg"
                              xmlns="http://www.w3.org/2000/svg">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="svg:svg">
    <svg>
      <xsl:copy-of select="@*" />
      <defs>
        <clipPath>
          <xsl:attribute name="id" select="'clipPath'" />
          <xsl:for-each select="//svg:path">
            <xsl:copy-of select="." />
          </xsl:for-each>
        </clipPath>
      </defs>
      <xsl:apply-templates />
    </svg>
  </xsl:template>
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>
</xsl:stylesheet>
