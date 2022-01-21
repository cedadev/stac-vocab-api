# encoding: utf-8
"""

"""
__author__ = 'Rhys Evans'
__date__ = '01 Jan 2022'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'rhys.r.evans@stfc.ac.uk'

from fastapi import FastAPI
from . import _config as config
from .utils import *


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/concept/search/")
async def concept_search(input: str):
    namespace = None
    if ":" in input:
        namespace = input.split(":")[0]
        input = input.split(":")[1]

    namespace_query = f"""
        UNION
        {{
            ?uri rdf:type skos:Concept .
            BIND (10 AS ?w)
            FILTER REGEX(STR(?uri), "/{namespace}/{input}", "i")
        }}
    """ if namespace else ""

    query = f"""
        SELECT DISTINCT ?uri (SUM(?w) AS ?weight)
        WHERE {{
            {{
                ?uri rdf:type skos:Concept ;
                    skos:prefLabel ?pl .
                BIND (50 AS ?w)
                FILTER REGEX(?pl, "{input}$", "i")
            }}
            {namespace_query}
            UNION
            {{
                ?uri rdf:type skos:Concept ;
                    skos:altLabel ?al .
                BIND (5 AS ?w)
                FILTER REGEX(?al, "{input}$", "i")
            }}
        }}
        GROUP BY ?uri
        ORDER BY DESC(?weight)
    """
    result = sparql_query(query)

    return result


@app.get("/conceptScheme/search/")
async def concept_scheme_search(input: str):
    namespace = None
    if ":" in input:
        namespace = input.split(":")[0]
        input = input.split(":")[1]

    namespace_query = f"""
            UNION
            {{
                ?uri rdf:type skos:ConceptScheme .
                BIND (10 AS ?w)
                FILTER REGEX(STR(?uri), "/{namespace}/{input}", "i")
            }}
    """ if namespace else ""
    
    query = f"""
        SELECT DISTINCT ?uri (SUM(?w) AS ?weight)
        WHERE {{
            {{
                ?uri rdf:type skos:ConceptScheme ;
                    skos:prefLabel ?pl .
                BIND (50 AS ?w)
                FILTER REGEX(?pl, "{input}$", "i")
            }}
            {namespace_query}
            UNION
            {{
                ?uri rdf:type skos:ConceptScheme ;
                    skos:altLabel ?al .
                BIND (5 AS ?w)
                FILTER REGEX(?al, "{input}$", "i")
            }}
        }}
        GROUP BY ?uri
        ORDER BY DESC(?weight)
    """
    result = sparql_query(query)

    return result


@app.get("/concept/")
async def concept(uri: str):
    return get_concept(uri)


@app.get("/conceptScheme/")
async def conceptScheme(uri: str):
    return get_concept_scheme(uri)


@app.get("/conceptScheme/concepts")
async def concept_scheme_concepts(uri: str):
    return get_concept_scheme_concepts(uri)


# Return list more than one and then weight 