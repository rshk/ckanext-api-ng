"""
Json-LD support stuff
"""

RDF_NAMESPACES = {
    'dcat': 'http://www.w3.org/ns/dcat#',
    'dct': 'http://purl.org/dc/terms/',
    'dctype': 'http://purl.org/dc/dcmitype/',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'vcard': 'http://www.w3.org/2006/vcard/ns#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
}

CONTEXTS = {}
CONTEXTS['dataset'] = {
    'id': 'dct:identifier',
    'title': 'dct:title',
    'organization': 'dct:publisher',
    'maintainer': {
        '@type': 'vcard:Kind',
        '@id': 'dcat:contactPoint',
    },
    'author': {
        '@id': 'dcat:publisher',
        '@type': 'foaf:Agent',  # foaf:Person of foaf:Organization
    },
    'resource': 'dcat:distribution',
    'notes': 'dct:description',
    'group': 'dct:theme',
    'url': 'dct:landingPage',
    'license_id': '',

    # These are in "extras" -> should we merge them?
    'spatial_coverage': 'dct:spatial',
    'temporal_coverage': 'dct:temporal',  # start, end
    'update_frequency': 'dct:accrualPeriodicity',
    'published_date': 'dct:issued',
    'language': 'dct:language',
}
CONTEXTS['resource'] = {

}
