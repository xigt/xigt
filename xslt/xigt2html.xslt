<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html"
              doctype-system="about:legacy-compat"
              encoding="utf-8"
              indent="yes" />

  <xsl:template match="/">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="xigt-corpus">
  <html>
    <head>
      <meta http-equiv="Content-type" content="text/html;charset=utf-8" />
      <style type="text/css">
      td { padding:5px } 
      </style>
    </head>
    <body>
      <xsl:apply-templates select="metadata" />
      <xsl:apply-templates select="igt" />
    </body>
  </html>
  </xsl:template>
  
  <xsl:template match="metadata">
    <table>
      <tr><th colspan="2">metadata:</th></tr>
      <xsl:apply-templates select="meta" /></table>
  </xsl:template>

  <xsl:template match="meta">
    <tr><td><xsl:value-of select="@type" /></td>
        <td><xsl:value-of select="." /></td></tr>
  </xsl:template>

  <xsl:template match="igt">
    <hr />
    <table border="1">
    <xsl:apply-templates select="tier|comment" />
    </table>
  </xsl:template>

  <xsl:template match="comment|tier[@type='phrases' or @type='translations']">
    <xsl:variable name="colspan">
       <xsl:value-of select="count(../tier[@type='glosses']/elem)" />
    </xsl:variable>
    <tr>
    <xsl:choose>
    <xsl:when test="name(.) = 'comment'"> 
      <xsl:element name="td">
        <xsl:attribute name="colspan">
          <xsl:value-of select="$colspan" />
        </xsl:attribute> 
        <span style="font-style:italic"><xsl:value-of select="."/></span>
      </xsl:element>
    </xsl:when>
    <xsl:otherwise>
      <xsl:for-each select="elem">
        <xsl:element name="td">
          <xsl:attribute name="colspan">
            <xsl:value-of select="$colspan" />
          </xsl:attribute> 
          <xsl:attribute name="id">
            <xsl:value-of select="@id"/>
          </xsl:attribute>
          <xsl:value-of select="."/>
        </xsl:element>
      </xsl:for-each>
    </xsl:otherwise>
    </xsl:choose>
    </tr>
  </xsl:template>

  <xsl:template match="tier[@type='words']">
    <tr>
      <xsl:for-each select="elem">
        <xsl:variable name="wid">
          <xsl:value-of select="@id" />
        </xsl:variable>
        <xsl:variable name="subparts">
          <xsl:value-of 
            select="count(../../tier[@type='glosses']/elem[substring(@ref,1,string-length($wid))=$wid])" />
          </xsl:variable>
        <xsl:element name="td">
          <xsl:attribute name="colspan">
            <xsl:value-of select="$subparts" />
          </xsl:attribute> 
          <xsl:attribute name="id">
            <xsl:value-of select="@id" />
          </xsl:attribute>
          <xsl:choose>
            <xsl:when test="not(string(.))">
              <xsl:call-template name="rule0">
                <xsl:with-param name="ambigAlgnExpr" select="@ref" />
                <xsl:with-param name="contextid" select="ancestor::igt/@id" />
              </xsl:call-template>
            </xsl:when>
            <xsl:otherwise><xsl:value-of select="." /></xsl:otherwise>
          </xsl:choose>
        </xsl:element>
      </xsl:for-each>
    </tr>
  </xsl:template>

  <xsl:template match="tier[@type='morphemes']">
    <tr>
      <xsl:for-each select="elem">
        <xsl:variable name="mid">
          <xsl:value-of select="@id" />
        </xsl:variable>
        <xsl:variable name="subparts">
          <xsl:value-of 
            select="count(../../tier[@type='glosses']/elem[substring(@ref,1,string-length($mid))=$mid])" />
          </xsl:variable>
        <xsl:element name="td">
          <xsl:attribute name="colspan">
            <xsl:value-of select="$subparts" />
          </xsl:attribute> 
          <xsl:attribute name="id">
            <xsl:value-of select="@id" />
          </xsl:attribute>
          <xsl:choose>
            <xsl:when test="not(string(.))">
              <xsl:call-template name="rule0">
                <xsl:with-param name="ambigAlgnExpr" select="@ref" />
                <xsl:with-param name="contextid" select="ancestor::igt/@id" />
              </xsl:call-template>
            </xsl:when>
            <xsl:otherwise><xsl:value-of select="." /></xsl:otherwise>
          </xsl:choose>
        </xsl:element>
      </xsl:for-each>
    </tr>
  </xsl:template>

  <xsl:template match="tier[@type='glosses']">
    <tr>
      <xsl:for-each select="elem">
        <xsl:element name="td">
          <xsl:attribute name="id">
            <xsl:value-of select="@id" />
          </xsl:attribute>
          <xsl:value-of select="." />
        </xsl:element>
      </xsl:for-each>
    </tr>
  </xsl:template>


  <xsl:template match="tier[@type='syntax']" />


<!-- rules 0 - 4 implement alignment expressions -->

  <xsl:template name="rule0">
    <!-- the same delims get used inside the selctors type, we need to be sure
         !not to split on delims inside [ ] 
          
         this is a little tricky, to do so, we disambiguate in preprocessing
         step: make all the +s inside [ ] -> % and the ,s inside delims go
         to ; 
  
         to accomplish this, we'll recursively substitue []s for {}s to know
         that we've processed them.
    -->

    <xsl:param name="contextid" />
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
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <!-- put it back together -->
        <xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="translate($ambigAlgnExpr, '{}', '[]')" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="rule1">
    <xsl:param name="AlgnExpr" />
    <xsl:param name="contextid" />

    <xsl:choose>
      <xsl:when test="contains($AlgnExpr, ',')">
        <xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="substring-before($AlgnExpr,',')" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template>
        <xsl:text>&#xA0;</xsl:text>
        <xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="substring-after($AlgnExpr,',')" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="contains($AlgnExpr, '+')">
        <xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="substring-before($AlgnExpr,'+')" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template><xsl:call-template name="rule1">
          <xsl:with-param name="AlgnExpr" select="substring-after($AlgnExpr,'+')" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="rule2">
          <xsl:with-param name="Algn" select="$AlgnExpr" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="rule2">
    <!-- at this point in the grammar, we know have a string 
         and we either want the whole thing, or a subselection of it -->
    <xsl:param name="Algn" />
    <xsl:param name="contextid" />
    <xsl:choose>
      <xsl:when test="contains($Algn, '[')">
        <xsl:variable name="openb">
          <xsl:value-of select="string-length(substring-before($Algn,'['))" />
        </xsl:variable>
        <xsl:variable name="closeb">
          <xsl:value-of select="string-length(substring-before($Algn,']'))" />
        </xsl:variable>
        <!-- note the content element might also be inheriting content! , implement 
               recursively call! -->
        <xsl:variable name="content">
          <xsl:choose>
            <xsl:when test="not(string(//igt[@id=$contextid]//elem[@id=substring-before($Algn, '[')]))">
              <xsl:call-template name="rule0"> 
                <xsl:with-param name="ambigAlgnExpr" select="//igt[@id=$contextid]//elem[@id=substring-before($Algn, '[')]/@ref" />
                <xsl:with-param name="contextid" select="$contextid" />
              </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="//igt[@id=$contextid]//elem[@id=substring-before($Algn, '[')]" />
            </xsl:otherwise>
          </xsl:choose>
        </xsl:variable>

        <xsl:call-template name="rule3">
          <!--remember to strip off the brackets!! -->
          <xsl:with-param name="content" select="$content" />
          <xsl:with-param name="Selectors" select="substring($Algn, $openb+2, ($closeb - $openb - 1))" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
      <!-- with no subselection to make, we're done just get the element's 
           content -->
        <xsl:variable name="content">
          <xsl:choose>
            <xsl:when test="not(string(//igt[@id=$contextid]//elem[@id=substring-before($Algn, '[')]))">
              <xsl:call-template name="rule0"> 
                <xsl:with-param name="ambigAlgnExpr" select="//igt[@id=$contextid]//elem[@id=substring-before($Algn, '[')]/@ref" />
                <xsl:with-param name="contextid" select="$contextid" />
              </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="//igt[@id=$contextid]//elem[@id=substring-before($Algn, '[')]" />
            </xsl:otherwise>
          </xsl:choose>
        </xsl:variable>
        <xsl:value-of select="$content" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="rule3">
    <xsl:param name="Selectors" />
    <xsl:param name="content" />
    <xsl:param name="contextid" />
    <xsl:choose>
      <xsl:when test="contains($Selectors, ';')">
        <xsl:call-template name="rule3">
          <xsl:with-param name="Selectors" select="substring-before($Selectors,';')" />
          <xsl:with-param name="content" select="$content" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template>
        <xsl:text>&#xA0;</xsl:text>
        <xsl:call-template name="rule3">
          <xsl:with-param name="Selectors" select="substring-after($Selectors,';')" />
          <xsl:with-param name="content" select="$content" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="contains($Selectors, '%')">
        <xsl:call-template name="rule3">
          <xsl:with-param name="Selectors" select="substring-before($Selectors,'%')" />
          <xsl:with-param name="content" select="$content" />
          <xsl:with-param name="contextid" select="$contextid" />
        </xsl:call-template><xsl:call-template name="rule3">
          <xsl:with-param name="Selectors" select="substring-after($Selectors,'%')" />
          <xsl:with-param name="content" select="$content" />
          <xsl:with-param name="contextid" select="$contextid" />
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
