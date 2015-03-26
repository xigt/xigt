
class XigtError(Exception): pass
class XigtLookupError(XigtError): pass
class XigtStructureError(XigtError): pass
class XigtAttributeError(XigtError): pass
class XigtAutoAlignmentError(XigtError): pass

class XigtWarning(Warning): pass