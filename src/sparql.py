import logging

from SPARQLWrapper import SPARQLWrapper, CSV, JSON
from pythonql.parser.Preprocessor import makeProgramFromString

import static as static

glogger = logging.getLogger(__name__)

SPARQL_FORMATS = {
    'text/csv': CSV,
    'application/json': JSON
}

CONTENT_EXTENSIONS = {
    'csv': CSV,
    'json': JSON
}

def selectReturnFormat(contentType):
    return SPARQL_FORMATS[contentType] if contentType in SPARQL_FORMATS else CSV

def selectExtensionFormat(fileExtension):
    return CONTENT_EXTENSIONS[fileExtension] if fileExtension in CONTENT_EXTENSIONS else CSV

def executeSPARQLQuery(endpoint, query, retformat):
    client = SPARQLWrapper(endpoint)
    client.setQuery(query)
    client.setReturnFormat(retformat)
    client.setCredentials(static.DEFAULT_ENDPOINT_USER, static.DEFAULT_ENDPOINT_PASSWORD)
    result = client.queryAndConvert()

    return result

def project(dataIn, projectionScript):
    '''Programs may make use of data in the `dataIn` variable and should
    produce data on the `dataOut` variable.'''
    program = makeProgramFromString(projectionScript)
    # We don't really need to initialize it, but we do it to avoid linter errors
    dataOut = []
    try:
        exec(program)
    except Exception as e:
        glogger.error("Error while executing SPARQL projection")
        glogger.error(projectionScript)
        glogger.error("Encountered exception: ")
        glogger.error(e)
        dataOut = dataIn
    return dataOut
