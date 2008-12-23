#/*=========================================================================
# 
#  Library   : wrapping
#  Module    : $RCSfile: doxy2docstring.py,v $
#  Authors   : Raghavendra Chandrashekara
#  Copyright : Imperial College, Department of Computing
#              Visual Information Processing (VIP), 2000-2004
#  Purpose   : Python script used to generate the SWIG documentation
#              strings from XML representation of documentation obtained
#              from doxygen.
#  Date      : $Date: 2004-10-13 14:49:45 $
#  Version   : $Revision: 1.4 $
#  Changes   : $Locker:  $
#              $Log: doxy2docstring.py,v $
#              Revision 1.4  2004-10-13 14:49:45  rc3
#              Added processXMLFile() function.
#
#              Revision 1.3  2004/10/13 12:42:26  rc3
#              Added option to process a single file.
#
#              Revision 1.2  2004/10/13 12:31:30  rc3
#              Added GetMethodInformation() method.
#
#              Revision 1.1  2004/10/13 11:05:29  rc3
#              Added script for generating documentation strings
#              from doxygen generated XML files.
#
#=========================================================================*/

import os, string, sys, textwrap
from xml.dom.ext.reader import Sax2
from xml import xpath

def normalizeWhiteSpace(s):
    return string.join(s.split())

def writeHeader(f, argv):
    textWrapper = textwrap.TextWrapper()
    textWrapper.initial_indent = '// '
    textWrapper.subsequent_indent = '// '

    s = textWrapper.fill('This file was automatically generated by %s. Please do not edit it. Use %s to regenerate the file. The following command line arguments were used:' % (argv[0], argv[0]))
    s += '\n//\n// '
    for arg in argv:
        s += arg + ' '

    f.write(s)
    f.write('\n\n')

def processXMLFile(processor, fileName, outputFile):
    '''Processes a single XML file and writes the documentation strings
    extracted to the output file.

    processor - The DoxygenXMLFileToDocstrings object which does the processing.
    fileName - The name of the XML file.
    outputFile - The output file object.'''
    processor.ProcessXMLFile(fileName)
    names = processor.DocumentationStrings.keys()
    names.sort()
    for name in names:
        outputFile.write(processor.DocumentationStrings[name] + '\n')
    
class ParameterInformation:
    '''Class to represent the parameters which need to be passed to a method.

    name - String representing the name of the parameter.
    typ - The type of the parameter.
    '''
    def __init__(self, name = None, typ = None):
        self.Name = name
        self.Type = typ

    def __str__(self):
        return self.Type + ' ' + self.Name

class MethodInformation:
    '''Class to represent the information about a method in a class.'''
    def __init__(self, name = None, returnType = None, parameterInfos = None, className = None, briefDescription = None, detailedDescription = None):
        '''Initializes the method with the name and return type.

        name - String representing the name of the class.
        returnType - String representing the return type.
        parameterInfo - List of ParameterInformation objects containing
        information about the parameters to the method.'''
        self.Name = name
        self.ReturnType = returnType
        self.ParameterInformations = parameterInfos
        self.ClassName = className
        self.BriefDescription = briefDescription
        self.DetailedDescription = detailedDescription

    def __str__(self):
        s = self.Name + '('

        nParameters = len(self.ParameterInformations)

        for i in range(nParameters - 1):
            s += str(self.ParameterInformations[i]) + ', '

        if nParameters - 1 >= 0:
            s += str(self.ParameterInformations[nParameters - 1])

        s += ') -> ' + self.ReturnType

        return s

class DoxygenXMLFileToDocstrings:
    '''Class to convert a doxygen generated XML file containing information
    about a class into a list of MethodInformation objects which store
    information about each method in the class.'''
    def ProcessXMLFile(self, xmlFileName):
        '''Returns a list of method information objects containing information
        about each method in the class.

        xmlFileName - The name of the XML file containing the class information.
        '''
        reader = Sax2.Reader()
        xmlDocument = reader.fromStream(xmlFileName)
        documentElement = xmlDocument.documentElement

        self.ClassName = self.GetTextFromElement(documentElement, 'compounddef/compoundname/text()')
                                            
        self.MethodInformations = []
        methodElements = self.GetMethodElements(documentElement)

        for methodElement in methodElements:
            methodInformation = self.GetMethodInformation(methodElement)
            self.MethodInformations.append(methodInformation)

        self.DocumentationStrings = {}
        for methodInfo in self.MethodInformations:
            self.DocumentationStrings[methodInfo.Name] = '%feature ("docstring", "'

        for methodInfo in self.MethodInformations:
            self.DocumentationStrings[methodInfo.Name] += '\n' + str(methodInfo) + '\n'
            if methodInfo.BriefDescription != '':
                self.DocumentationStrings[methodInfo.Name] += methodInfo.BriefDescription + '\n'
            if methodInfo.DetailedDescription != '':
                self.DocumentationStrings[methodInfo.Name] += methodInfo.DetailedDescription + '\n'

        keys = self.DocumentationStrings.keys()
        for key in keys:
            self.DocumentationStrings[key] += '") ' + methodInfo.ClassName + '::' + key + ';\n'

    def GetMethodInformation(self, e):
        '''Takes a method element and returns information about the method.'''
        mi = MethodInformation()
        mi.ClassName = self.ClassName
        mi.Name = self.GetTextFromElement(e, 'name/text()')
        mi.ReturnType = self.GetTextFromElement(e, 'type/text()|type/ref/text()')
        mi.ReturnType = self.CPPTextToPythonText(mi.ReturnType)
        mi.ReturnType = mi.ReturnType.replace('virtual', '')

        if mi.ReturnType == '':
            mi.ReturnType = 'None'
        mi.ReturnType = self.CPPTextToPythonText(mi.ReturnType)
        mi.BriefDescription = textwrap.fill(self.GetTextFromElement(e, 'briefdescription/para/text()'), 65)
        if mi.BriefDescription != '':
            mi.BriefDescription = '\n' + mi.BriefDescription
        mi.DetailedDescription = textwrap.fill(self.GetTextFromElement(e, 'detaileddescription/text()'), 65)
        if mi.DetailedDescription != '':
            mi.DetailedDescription = '\n' + mi.DetailedDescription
            
        # Get information about the parameters to the method.
        mi.DetailedDescription += self.GetDetailedParameterInformation(e)
        
        mi.ParameterInformations = []
        paramElements = self.GetParameterElements(e)
        for paramElement in paramElements:
            typeName = self.GetTextFromElement(paramElement, 'type/text()|type/ref/text()')
            typeName = self.CPPTextToPythonText(typeName)
            paramName = self.GetTextFromElement(paramElement, 'declname/text()')
            mi.ParameterInformations.append(ParameterInformation(paramName, typeName))

        return mi
        
    def GetDetailedParameterInformation(self, methodElement):
        '''Returns a string representing the information about the parameters
        which can be passed to a method.'''
        parameterNames = xpath.Evaluate('detaileddescription/para/parameterlist/parametername', methodElement)
        parameterDescriptions = xpath.Evaluate('detaileddescription/para/parameterlist/parameterdescription/para', methodElement)

        paramInformation = ''
        nParams = len(parameterNames)
        for i in range(nParams):
            paramInformation += textwrap.fill(self.GetTextFromElement(parameterNames[i]) + ' ' + self.GetTextFromElement(parameterDescriptions[i]), 65, subsequent_indent = '  ')
            if i < nParams - 1:
                paramInformation += '\n'

        if paramInformation != '':
            paramInformation = '\n' + paramInformation
        return paramInformation
        
    def GetMethodElements(self, classElement):
        '''Returns the method elements from a class element.

        classElement - The class element.'''
        methodElements = xpath.Evaluate('compounddef/sectiondef[@kind = "public-func"]/memberdef[@kind = "function"]', classElement)
        return methodElements

    def GetParameterElements(self, methodElement):
        '''Returns the parameter elements from a method element.

        methodElement - The method element.'''
        paramElements = xpath.Evaluate('param', methodElement)
        return paramElements

    def GetTextFromElement(self, element, xpathStr = 'text()'):
        '''Returns the text in an element.

        element - The element.
        xpaths - Optional xpath string to match against. The default xpath
        string is "text()".
        '''
        textNodes = xpath.Evaluate(xpathStr, element)

        text = ''
        for textNode in textNodes:
            if textNode.nodeValue != None:
                text += normalizeWhiteSpace(textNode.nodeValue)

        return text

    def CPPTextToPythonText(self, s):
        '''Converts C++ keywords in a string to equivalent python keywords.

        s - The string to convert.
        '''
        s = s.replace('virtual ', '')
        s = s.replace('void', 'None')
        s = s.replace('const ', '')
        s = s.replace('&', '(ref)')
        s = s.replace('double', 'float')
        s = s.replace('char *', 'string')
        return s

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print textwrap.fill(sys.argv[0] + ' takes XML files generated by the doxygen program and generates SWIG documentation strings for the class methods in the XML files.', 80)
        print
        print 'Usage:', sys.argv[0], 'fileName.xml outputFileName.i'
        print
        print 'Where:'
        print
        print 'fileName.xml'
        print textwrap.fill('The XML file containing information about the class and the methods within it. An index file can also be passed to the script to generate the documentation strings for all the classes referred to in the index.', 80, initial_indent = '  ', subsequent_indent = '  ')
        print
        print 'outputFileName.i'
        print textwrap.fill('The output file name to store the documentation strings.', 80, initial_indent = '  ', subsequent_indent = '  ')
        print
        print 'Requirements:'
        print textwrap.fill('PyXML 0.8.3 or above must be installed.', initial_indent = '  ', subsequent_indent = '  ')
        sys.exit(1)

    inputFileName = sys.argv[1]
    outputFileName = sys.argv[2]

    outputFile = file(outputFileName, 'w')
    writeHeader(outputFile, sys.argv)
    
    processor = DoxygenXMLFileToDocstrings()

    if os.path.basename(inputFileName) == 'index.xml':
        print 'Processing index file.'
        dirName = os.path.dirname(inputFileName)
        indexFile = file(inputFileName)

        reader = Sax2.Reader()
        document = reader.fromStream(indexFile)
        documentElement = document.documentElement

        nameElements = xpath.Evaluate('compound[@kind = "class"]', documentElement)
        fileNames = []

        for nameElement in nameElements:
            fileNames.append(dirName + '/' + nameElement.getAttribute('refid') + '.xml')

        i = 1
        totalNumberOfFiles = len(fileNames)
        for fileName in fileNames:
            print 'Processing file %d of %d ' % (i, totalNumberOfFiles) + fileName
            processXMLFile(processor, fileName, outputFile)
            i += 1

        print 'Done'
    else:
        print 'Processing file', inputFileName

        processXMLFile(processor, inputFileName, outputFile)
        print 'Done'

    outputFile.close()
