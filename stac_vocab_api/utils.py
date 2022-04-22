from collections import defaultdict
import logging
import os
import pickle
import time

from pydantic import BaseModel
from rdflib import Graph, SKOS, RDF, URIRef
from . import _config as config


__all__ = [
    "sparql_query",
    "get_concept",
    "get_concept_scheme",
    "get_concept_scheme_concepts",
]


def _build_graph() -> Graph:
    """
    Function to build graph from rdf file.
    """
    logging.debug("building graph ({})".format(config.CEDA_VOCAB_LOCATION))

    # create the graph
    graph = Graph()
    graph.bind('skos', SKOS)

    if os.path.isfile(config.CEDA_VOCAB_LOCATION):
        graph.parse(config.CEDA_VOCAB_LOCATION)

    return graph


def _cache_write(cache_object):
    """
    Function to write object to cache.

    :param cache_object: object to be cached
    """
    logging.debug("_cache_write({})".format(cache_object))

    # create dir if not there
    if not os.path.isdir(os.path.dirname(config.CACHE_FILE)):
        os.makedirs(os.path.dirname(config.CACHE_FILE))

    with open(config.CACHE_FILE, "wb") as cache_file:
        pickle.dump(cache_object, cache_file)


def _cache_clear():
    """
    Function to clear cache.
    """
    logging.debug("_cache_clear()")

    # remove the pickle cache
    if os.path.isfile(config.CACHE_FILE):
        os.unlink(config.CACHE_FILE)


def _cache_load() -> Graph:
    """
    Load graph from cache, reload if needed.

    :return: graph
    :rtype: rdflib.Graph
    """
    logging.debug("_cache_load()")

    if config.DEBUG:
        logging.debug("DEBUG so purge cache")
        graph = _cache_reload()

    if os.path.isfile(config.CACHE_FILE):
        logging.debug("getting graph from CACHE_FILE")
        cache_file_age = time.time() - os.stat(config.CACHE_FILE).st_mtime
        if cache_file_age < config.CACHE_HOURS * 3600:
            with open(config.CACHE_FILE, "rb") as f:
                graph = pickle.load(f)
        else:  # old cache file
            logging.debug(f"cache older that {config.CACHE_HOURS} hours rebuilding graph")
            graph = _cache_reload()
    else:
        graph = _build_graph()
        _cache_write(graph)

    return graph


def _cache_reload() -> Graph:
    """
    Clear and rewrite graph to cache.

    :return: graph
    :rtype: rdflib.Graph
    """
    logging.debug("_cache_reload()")

    _cache_clear()
    graph = _build_graph()
    _cache_write(graph)

    return graph


def sparql_query(query: str, reload: bool = False) -> dict:
    """
    Perform a SPARQL query.

    :param query: the SPARQL query
    :param reload: If the graph should be reloaded
    :return: dictionary of query result
    :rtype: dict
    """
    if reload:
        graph = _cache_reload()
    else:
        graph = _cache_load()
    graph = _cache_reload()
    try:
        sparql_result = graph.query(query)

        response = {}

        if len(sparql_result) != 0 and sparql_result.bindings[0] != {}:
            response = {"error": False, "result": []}

            if len(sparql_result) == 1:
                uris = [sparql_result.bindings[0]["uri"]]
            else:
                uris = [uri[0] for uri in sparql_result]

            rdf_type = graph.value(uris[0], RDF.type)

            if rdf_type == SKOS.Concept:
                for uri in uris:
                    response["result"].append(_get_concept_info(graph, uri))
                
            elif rdf_type == SKOS.ConceptScheme:
                for uri in uris:
                    response["result"].append(_get_concept_scheme_info(graph, uri))

        else:
            response = {"error": False, "result": None}

        return response

    except Exception as e:
        response = {
            "error": True,
            "error_reason": f"SPARQL query failed: {e}"
        }

        return response


def get_info_from_uri(graph: Graph, uri: URIRef) -> dict:
    """
    Get information from URI.

    :param graph: The graph
    :param uri: URI of object
    :return: dictionary of information
    :rtype: dict
    """
    response = {"uri": uri}

    if pref_label := graph.value(uri, SKOS.prefLabel):
        response["pref_label"] = pref_label
    
    if alt_label := graph.value(uri, SKOS.altLabel):
        response["alt_label"] = alt_label

    if definition := graph.value(uri, SKOS.definition):
        response["definition"] = definition
    
    return response


def get_concept_from_uri(uri: str, reload: bool = False) -> dict:
    """
    Get a concept from its URI.

    :param uri: URI of concept
    :param reload: If the graph should be reloaded
    :return: dictionary representation of concept
    :rtype: dict
    """
    if reload:
        graph = _cache_reload()
    else:
        graph = _cache_load()
    
    uri = URIRef(uri)

    try:
        result = _get_concept_info(graph, uri)

        if result:
            response = {
                "error": False,
                "result": result
            }
        else:
            response = {
                "error": False,
                "result": None
            }

        return response

    except Exception as e:
        return {
                "error": True,
                "error_reason": f"Concept return failed: {e}"
            }


def _get_concept_info(graph, uri) -> dict:
    """
    Get information on concept.

    :param graph: The graph
    :param uri: URI of concept
    :return: dictionary of concept information
    :rtype: dict
    """
    response = get_info_from_uri(graph, uri)

    concept_scheme = graph.value(uri, SKOS.inScheme)
    response["in_scheme"] = _get_concept_scheme_info(graph, concept_scheme)
    
    return response


def get_concept_scheme(uri: str, reload: bool = False) -> dict:
    """
    Get a concept scheme from its URI.

    :param uri: URI of concept scheme
    :param reload: If the graph should be reloaded
    :return: dictionary representation of concept scheme
    :rtype: dict
    """
    if reload:
        graph = _cache_reload()
    else:
        graph = _cache_load()
    
    uri = URIRef(uri)

    try:
        result = _get_concept_scheme_info(graph, uri)

        if result:
            response = {
                "error": False,
                "result": result
            }
        else:
            response = {
                "error": False,
                "result": None
            }

        return response

    except Exception as e:
        return {
                "error": True,
                "error_reason": f"Concept scheme return failed: {e}"
            }


def _get_concept_scheme_info(graph, uri) -> dict:
    """
    Get information on concept scheme.

    :param graph: The graph
    :param uri: URI of concept scheme
    :return: dictionary of concept scheme information
    :rtype: dict
    """
    response = get_info_from_uri(graph, uri)
    
    if broader_schemes := graph.triples((None, SKOS.broader, uri)):
        for broader_scheme, _, _ in broader_schemes:
            response.setdefault("broader_than", []).append(get_info_from_uri(graph, broader_scheme))

    if narrower_schemes := graph.triples((None, SKOS.narrower, uri)):
        for narrower_scheme, _, _ in narrower_schemes:
            response.setdefault("narrower_than", []).append(get_info_from_uri(graph, narrower_scheme))
    
    return response


def get_concept_scheme_concepts(uri: str, reload: bool = False) -> dict:
    """
    Get concepts for a given concept scheme from its URI.

    :param uri: URI of concept scheme
    :param reload: If the graph should be reloaded
    :return: dictionary representation of concept scheme
    :rtype: dict
    """
    if reload:
        graph = _cache_reload()
    else:
        graph = _cache_load()
    
    uri = URIRef(uri)

    try:
        result = _get_concept_scheme_info(graph, uri)

        if result:
            response = {
                "error": False,
                "result": result
            }
            if concepts := graph.triples((None, SKOS.inScheme, uri)):
                response["result"]["concepts"] = []
                for concept, _, _ in concepts:
                    response["result"]["concepts"].append(get_info_from_uri(graph, concept))
        else:
            response = {
                "error": True,
                "error_reason": f"No concept scheme exist for uri: {uri}"
            }

        return response

    except Exception as e:
        return {
                "error": True,
                "error_reason": f"Concept scheme concepts return failed: {e}"
            }


class IndexerRequest(BaseModel):
    namespace: str
    terms: list[str]
    properties: dict
    strict: bool

def indexer_strict(request: IndexerRequest) -> dict:

    vocab_properties = defaultdict(dict)

    for term, value in request.properties.items():

        if term in request.terms:
            query = f"""
                SELECT ?uri
                WHERE {{
                    {{
                        ?uri rdf:type skos:Concept .
                        FILTER (STR(?uri) = "{request.namespace}/{value}")
                    }}
                }}
            """

            # PREF_LABEL QUERY
            # query = f"""
            #     SELECT ?uri
            #     WHERE {{
            #         {{
            #             ?uri rdf:type skos:Concept ;
            #             skos:prefLabel "{value}"@en .
            #         }}
            #     }}
            # """

            query_result = sparql_query(query)

            print(query_result)

            if result := query_result["result"]:

                concept = result[0]

                # Check if the concept is in a scheme could use pref_label? concept["in_scheme"]["pref_label"].value
                if "in_scheme" in concept and term == concept["in_scheme"]["uri"].removeprefix(f"{request.namespace}/"):

                    concept_scheme = concept["in_scheme"]
                    vocab_properties[request.namespace] |= {term: value}

                    # Check if the concept scheme has a general scheme
                    if "narrower_than" in concept_scheme:

                        general_concept_scheme = concept_scheme["narrower_than"][0]
                        vocab_properties["general"] |= {general_concept_scheme["pref_label"]: value}
                
                else:

                    return {"error": True, "reason": f"{value} not in {term}"}

            else:

                return {"error": True, "reason": f"{value} not in {request.namespace}"}

        else:

            vocab_properties["unspecified_vocab"] |= {term: value}

    return {"error": False, "result": vocab_properties}


def indexer_lenient(request: IndexerRequest) -> dict:

    vocab_properties = defaultdict(dict)

    for term, value in request.properties.items():

        if term in request.terms:

            query = f"""
                SELECT ?uri
                WHERE {{
                    {{
                        ?uri rdf:type skos:ConceptScheme .
                        FILTER (STR(?uri) = "{request.namespace}/{term}")
                    }}
                }}
            """

            query_result = sparql_query(query)

            if result := query_result["result"]:

                concept_scheme = result[0]

                vocab_properties[request.namespace] |= {term: value}

                # Check if the concept scheme has a general scheme
                if "narrower_than" in concept_scheme:

                    general_concept_scheme = concept_scheme["narrower_than"][0]
                    vocab_properties["general"] |= {general_concept_scheme["pref_label"]: value}
            
            else:

                return {"error": True, "reason": f"{term} not in {request.namespace}"}

        else:

            vocab_properties["unspecified_vocab"] |= {term: value}

    return {"error": False, "result": vocab_properties}