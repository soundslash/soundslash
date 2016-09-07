<!-- Copy this file to /usr/share/icecast/web/ directory -->
<xsl:stylesheet xmlns:xsl = "http://www.w3.org/1999/XSL/Transform" version = "1.0" >
	<xsl:template match = "/icestats" >
		<xsl:for-each select="source"><xsl:value-of select="@mount" />=<xsl:value-of select="listeners" />;</xsl:for-each>
	</xsl:template>
</xsl:stylesheet>
