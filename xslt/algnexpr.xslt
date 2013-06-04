<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!--
  <xsl:output method="html"
              doctype-system="about:legacy-compat"
              encoding="utf-8"
              indent="yes" />-->

<!-- 
  We should be able to parse alginment expressions using 
  the grammar that mwg provides in the law paper

  Here I number the rules of the grammar and below
  I write an xsl template for each of them.

  S=AlgnExpr

  1: AlgnExpr -> Algn | Algn Delim AlgnExpr
  2: Algn ->  #id Selection
  ## Delim -> ',' | '+' (this rule is implemented on-line)
  ## Selection -> '[' Selectors ']' | epsilon (implemented on-line)
  3: Selectors -> Span | Span Delim Span (this rule is implemented on-line)
  4: Span -> integer ':' integer
  
  
-->
  
  <xsl:template match="span">
    [<xsl:value-of select="." />]
    <xsl:call-template name="rule0">
      <xsl:with-param name="ambigAlgnExpr" select="." />
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="rule0">
    <!-- the same delims get used inside the selctors type, we need to be sure
         !not to split on delims inside [ ] 
          
         this is a little tricky, to do so, we disambiguate in preprocessing
         step: make all the +s inside [ ] -> % and the ,s inside delims go
         to ; 
  
         to accomplish this, we'll recursively substitue []s for {}s to know
         that we've processed them.
    -->

    <xsl:param name="ambigAlgnExpr" />
    <xsl:choose>
      <xsl:when test="contains($ambigAlgnExpr, '[')">
        <!-- clean it! -->
        <xsl:variable name="openb">
          <xsl:value-of select="string-length(substring-before($ambigAlgnExpr,'['))" />
        </xsl:variable>
        <xsl:variable name="closeb">
          <xsl:value-of select="string-length(substring-before($ambigAlgnExpr,']'))" />
        </xsl:variable>
        <xsl:variable name="lessAmbigAlgnExpr">
          <xsl:value-of select="concat(substring-before($ambigAlgnExpr, '['), '{')" />
          <xsl:value-of select="translate(substring($ambigAlgnExpr, $openb+2, ($closeb - $openb - 1)), '+,', '%;')" />
          <xsl:value-of select="concat('}', substring-after($ambigAlgnExpr, ']'))" />
        </xsl:variable>
        <xsl:call-template name="rule0">
          <xsl:with-param name="ambigAlgnExpr" select="$lessAmbigAlgnExpr" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <!-- put it back together -->
        <xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="translate($ambigAlgnExpr, '{}', '[]')" />
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="rule1">
    <xsl:param name="AlgnExpr" />

    <xsl:choose>
      <xsl:when test="contains($AlgnExpr, ',')">
        <xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="substring-before($AlgnExpr,',')" />
        </xsl:call-template>
        <xsl:text>&#xA0;</xsl:text>
        <xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="substring-after($AlgnExpr,',')" />
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="contains($AlgnExpr, '+')">
        <xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="substring-before($AlgnExpr,'+')" />
        </xsl:call-template><xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="substring-after($AlgnExpr,'+')" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="rule2">
          <xsl:with-param name="Algn" select="$AlgnExpr" />
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="rule2">
    <!-- at this point in the grammar, we know have a string 
         and we either want the whole thing, or a subselection of it -->
    <xsl:param name="Algn" />
    <xsl:choose>
      <xsl:when test="contains($Algn, '[')">
        <xsl:variable name="openb">
          <xsl:value-of select="string-length(substring-before($Algn,'['))" />
        </xsl:variable>
        <xsl:variable name="closeb">
          <xsl:value-of select="string-length(substring-before($Algn,']'))" />
        </xsl:variable>

        <xsl:call-template name="rule3">
          <!--remember to strip off the brackets!! -->
          <xsl:with-param name="content" select="//span[@id=substring-before($Algn, '[')]" />
          <xsl:with-param name="Selectors" select="substring($Algn, $openb+2, ($closeb - $openb - 1))" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
      <!-- with no subselection to make, we're done just get the element's 
           content -->
        <xsl:value-of select="//span[@id=$Algn]" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="rule3">
    <xsl:param name="Selectors" />
    <xsl:param name="content" />
    <xsl:choose>
      <xsl:when test="contains($Selectors, ';')">
        <xsl:call-template name="rule3">
          <xsl:with-param name="Selectors" select="substring-before($Selectors,';')" />
          <xsl:with-param name="content" select="$content" />
        </xsl:call-template>
        <xsl:text>&#xA0;</xsl:text>
        <xsl:call-template name="rule3">
          <xsl:with-param name="Selectors" select="substring-after($Selectors,';')" />
          <xsl:with-param name="content" select="$content" />
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="contains($Selectors, '%')">
        <xsl:call-template name="rule3">
          <xsl:with-param name="Selectors" select="substring-before($Selectors,'%')" />
          <xsl:with-param name="content" select="$content" />
        </xsl:call-template><xsl:call-template name="rule3">
          <xsl:with-param name="Selectors" select="substring-after($Selectors,'%')" />
          <xsl:with-param name="content" select="$content" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <!-- otherwise you've got simple selectors so go ahead and get the relevant substring -->
        <xsl:variable name="from">
          <xsl:value-of select="substring-before($Selectors, ':')" />
        </xsl:variable>
        <xsl:variable name="to">
          <xsl:value-of select="substring-after($Selectors, ':')" />
        </xsl:variable>
        <xsl:value-of select="substring($content, $from+1, ($to - $from))" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
