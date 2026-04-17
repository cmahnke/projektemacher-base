import os
import sys
import json
import re
import warnings
import requests
import argparse
import logging
import time
from datetime import datetime
from rdflib import Graph, URIRef, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS, OWL, SKOS, XSD as XSD_NS

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ── Namespaces ──
SCHEMA_HTTP = Namespace("http://schema.org/")
SCHEMA_HTTPS = Namespace("https://schema.org/")
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")
WDTN = Namespace("http://www.wikidata.org/prop/direct-normalized/")
P = Namespace("http://www.wikidata.org/prop/")
PS = Namespace("http://www.wikidata.org/prop/statement/")
PSV = Namespace("http://www.wikidata.org/prop/statement/value/")
PSN = Namespace("http://www.wikidata.org/prop/statement/value-normalized/")
PQ = Namespace("http://www.wikidata.org/prop/qualifier/")
PQV = Namespace("http://www.wikidata.org/prop/qualifier/value/")
PQN = Namespace("http://www.wikidata.org/prop/qualifier/value-normalized/")
PR = Namespace("http://www.wikidata.org/prop/reference/")
PRV = Namespace("http://www.wikidata.org/prop/reference/value/")
PRN = Namespace("http://www.wikidata.org/prop/reference/value-normalized/")
WDREF = Namespace("http://www.wikidata.org/reference/")
WDVALUE = Namespace("http://www.wikidata.org/value/")
WIKIBASE = Namespace("http://wikiba.se/ontology#")
WDQS = Namespace("http://wikiba.se/queryService#")
PROV = Namespace("http://www.w3.org/ns/prov#")
WDNO = Namespace("http://www.wikidata.org/prop/novalue/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
IIIF_PREZI = Namespace("http://iiif.io/api/presentation/3#")
IIIF_IMAGE = Namespace("http://iiif.io/api/image/3#")
EXIF = Namespace("http://www.w3.org/2003/12/exif/ns#")
OA = Namespace("http://www.w3.org/ns/oa#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
DCTYPES = Namespace("http://purl.org/dc/dcmitype/")

ENRICHMENT = Namespace("urn:enrichment:")

NAMESPACE_PREFIXES = {
    'schema': SCHEMA_HTTP, 'schemas': SCHEMA_HTTPS,
    'wd': WD, 'wdt': WDT, 'wdtn': WDTN,
    'p': P, 'ps': PS, 'psv': PSV, 'psn': PSN,
    'pq': PQ, 'pqv': PQV, 'pqn': PQN,
    'pr': PR, 'prv': PRV, 'prn': PRN,
    'wdref': WDREF, 'wdv': WDVALUE,
    'wikibase': WIKIBASE, 'wdqs': WDQS,
    'prov': PROV, 'wdno': WDNO,
    'crm': CRM, 'iiif-prezi': IIIF_PREZI,
    'iiif-image': IIIF_IMAGE, 'exif': EXIF,
    'oa': OA, 'dc': DC, 'dcterms': DCTERMS,
    'dcTypes': DCTYPES,
    'skos': SKOS, 'owl': OWL, 'rdfs': RDFS, 'rdf': RDF,
    'xsd': XSD_NS, 'enrichment': ENRICHMENT,
}

DEFAULT_PROPERTIES = {
    'P31', 'P279', 'P361', 'P527', 'P1552', 'P910', 'P1269',
    'P1448', 'P1449', 'P1559', 'P1705', 'P742', 'P735', 'P734',
    'P1477', 'P2561', 'P1476', 'P1680', 'P528', 'P1813', 'P2562',
    'P138', 'P97',
    'P1343', 'P973', 'P935', 'P373',
    'P18', 'P154', 'P242', 'P41', 'P94', 'P10', 'P51',
    'P158', 'P948', 'P6802', 'P4291', 'P3451', 'P8517',
    'P1442', 'P109',
    'P625', 'P17', 'P131', 'P36', 'P150', 'P30', 'P206',
    'P421', 'P47', 'P706', 'P1376', 'P276', 'P291', 'P840',
    'P937', 'P551',
    'P571', 'P576', 'P580', 'P582', 'P585', 'P569', 'P570',
    'P577', 'P1319', 'P1326',
    'P21', 'P27', 'P19', 'P20', 'P106', 'P39', 'P69', 'P108',
    'P22', 'P25', 'P26', 'P40', 'P3373', 'P184', 'P1066', 'P737',
    'P1412', 'P103', 'P140', 'P172', 'P119', 'P463', 'P241',
    'P410', 'P166', 'P1411', 'P511', 'P1035', 'P1971',
    'P112', 'P159', 'P169', 'P488', 'P127', 'P355', 'P749',
    'P452', 'P1128', 'P1454', 'P740',
    'P50', 'P57', 'P86', 'P170', 'P175', 'P136', 'P364', 'P495',
    'P123', 'P407', 'P921', 'P144', 'P747', 'P1433', 'P655',
    'P58', 'P162', 'P161', 'P725', 'P676', 'P264', 'P449',
    'P750', 'P272', 'P179', 'P155', 'P156', 'P629', 'P953',
    'P212', 'P957', 'P236', 'P356',
    'P460', 'P1889', 'P2860', 'P3342',
    'P1082', 'P2046', 'P2044', 'P2048', 'P2049', 'P2067',
}

_identifier_properties_cache: set[str] | None = None

ENTITY_BASE_CLASSES = {
    'Q5',         # human
    'Q17334923',  # location
    'Q43229',     # organization
    'Q1656682',   # event
    'Q386724',    # work
    'Q15642541',  # human-geographic territorial entity
    'Q16334295',  # group of humans
}
CLASSIFY_BATCH_SIZE = 50

# ── Properties deren Werte über P279 aufgelöst werden sollen ──
# Zusätzlich zu P31 (instance of) werden auch die Werte dieser
# Properties transitiv über P279 (subclass of) aufgelöst.
# So kann z.B. P106=Q1028181 (Maler) → P279* → Q483507 (Künstler)
# in Queries genutzt werden.
HIERARCHY_RESOLVE_PROPERTIES = {
    'P31',   # instance of (immer)
    'P106',  # occupation
    'P136',  # genre
    'P101',  # field of work
    'P452',  # industry
    'P279',  # subclass of (die Kette selbst)
    'P1435', # heritage designation
    'P31',   # redundant aber explizit
}

DEFAULT_KEEP_PREDICATES = {
    str(RDF.type), str(RDFS.label), str(RDFS.comment),
    'http://schema.org/name', 'http://schema.org/description',
    'http://schema.org/image', 'http://schema.org/url',
    'http://schema.org/sameAs', 'http://schema.org/alternateName',
    'http://schema.org/about', 'http://schema.org/mainEntity',
    'http://schema.org/subjectOf', 'http://schema.org/identifier',
    'http://schema.org/inLanguage', 'http://schema.org/dateCreated',
    'http://schema.org/dateModified', 'http://schema.org/datePublished',
    'http://schema.org/headline', 'http://schema.org/abstract',
    'http://schema.org/text', 'http://schema.org/thumbnailUrl',
    'http://schema.org/contentUrl', 'http://schema.org/encodingFormat',
    'http://schema.org/license', 'http://schema.org/copyrightHolder',
    'http://schema.org/author', 'http://schema.org/creator',
    'https://schema.org/name', 'https://schema.org/description',
    'https://schema.org/image', 'https://schema.org/url',
    'https://schema.org/sameAs', 'https://schema.org/alternateName',
    'https://schema.org/about', 'https://schema.org/mainEntity',
    'https://schema.org/subjectOf', 'https://schema.org/identifier',
    'https://schema.org/inLanguage', 'https://schema.org/dateCreated',
    'https://schema.org/dateModified', 'https://schema.org/datePublished',
    'https://schema.org/headline', 'https://schema.org/abstract',
    'https://schema.org/text', 'https://schema.org/thumbnailUrl',
    'https://schema.org/contentUrl', 'https://schema.org/encodingFormat',
    'https://schema.org/license', 'https://schema.org/copyrightHolder',
    'https://schema.org/author', 'https://schema.org/creator',
    'http://www.w3.org/2004/02/skos/core#prefLabel',
    'http://www.w3.org/2004/02/skos/core#altLabel',
    'http://www.w3.org/2004/02/skos/core#notation',
    'http://www.w3.org/2004/02/skos/core#definition',
    'http://www.w3.org/2004/02/skos/core#note',
    'http://www.w3.org/2004/02/skos/core#scopeNote',
    'http://www.w3.org/2004/02/skos/core#example',
    'http://www.w3.org/2002/07/owl#sameAs',
    'http://wikiba.se/ontology#sitelinks',
    'http://wikiba.se/ontology#identifiers',
    'http://wikiba.se/ontology#statements',
}

SPARQL_URL = "https://query.wikidata.org/sparql"
SPARQL_HEADERS = {
    'User-Agent': 'BlogEntityExtractor/1.0 (https://github.com/cmahnke)',
    'Accept': 'application/sparql-results+json'
}
MAX_RETRIES = 5
RETRY_BASE_WAIT = 2
REQUEST_TIMEOUT = 60
INCOMING_LIMIT = 1000
HIERARCHY_MAX_DEPTH = 10
HIERARCHY_BATCH_SIZE = 50
DEFAULT_LANGUAGES = ['en', 'de']
ALWAYS_INCLUDE_LANG = 'mul'

CONFIG = {
    'query_delay': 1.0,
}

FORMAT_MAP = {
    '.ttl': 'turtle', '.jsonld': 'json-ld', '.json': 'json-ld',
    '.xml': 'xml', '.rdf': 'xml', '.nt': 'nt', '.n3': 'n3', '.trig': 'trig',
}

DATETIME_YEAR_MIN = 1
DATETIME_YEAR_MAX = 9999
DATETIME_YEAR_RE = re.compile(r'^(-?\d+)-')

DATE_DATATYPES = {
    str(XSD.dateTime), str(XSD.date), str(XSD.gYear), str(XSD.gYearMonth),
    "http://www.w3.org/2001/XMLSchema#dateTime",
    "http://www.w3.org/2001/XMLSchema#date",
    "http://www.w3.org/2001/XMLSchema#gYear",
    "http://www.w3.org/2001/XMLSchema#gYearMonth",
}

LANG_SENSITIVE_PROPERTIES = {
    'http://www.w3.org/2000/01/rdf-schema#label',
    'http://schema.org/name', 'http://schema.org/description',
    'http://www.w3.org/2004/02/skos/core#prefLabel',
    'http://www.w3.org/2004/02/skos/core#altLabel',
    'http://schema.org/alternateName',
    'http://www.wikidata.org/prop/direct/P1448',
    'http://www.wikidata.org/prop/direct/P1449',
    'http://www.wikidata.org/prop/direct/P1559',
    'http://www.wikidata.org/prop/direct/P1705',
    'http://www.wikidata.org/prop/direct/P742',
    'http://www.wikidata.org/prop/direct/P2561',
    'http://www.wikidata.org/prop/direct/P1813',
    'http://www.wikidata.org/prop/direct/P1476',
    'http://www.wikidata.org/prop/direct/P1680',
}

WIKIDATA_OVERRIDES_PROPERTIES = {
    URIRef('http://schema.org/name'), URIRef('https://schema.org/name'),
    URIRef('http://schema.org/description'), URIRef('https://schema.org/description'),
    URIRef('http://schema.org/alternateName'), URIRef('https://schema.org/alternateName'),
    URIRef('http://schema.org/image'), URIRef('https://schema.org/image'),
    URIRef('http://schema.org/url'), URIRef('https://schema.org/url'),
    URIRef('http://schema.org/sameAs'), URIRef('https://schema.org/sameAs'),
    URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
    URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
    URIRef('http://www.w3.org/2004/02/skos/core#altLabel'),
}

STATEMENT_NODE_RE = re.compile(r'^http://www\.wikidata\.org/entity/statement/')
PROP_STATEMENT_LINK_RE = re.compile(r'^http://www\.wikidata\.org/prop/P\d+$')
WD_ENTITY_RE = re.compile(r'^http://www\.wikidata\.org/entity/Q\d+$')
WD_ENTITY_BROAD_RE = re.compile(
    r'^https?://(?:www\.)?wikidata\.org/(?:entity|wiki)/(Q\d+)$'
)

FETCHED_MARKER = ENRICHMENT['fetchedFrom']
FETCHED_VALUE = Literal("wikidata")
HIERARCHY_MARKER = ENRICHMENT['hierarchyNode']

RDFLIB_TERM_LOGGER = logging.getLogger('rdflib.term')
PROPERTY_ID_RE = re.compile(r'(P\d+)$')
LABEL_BATCH_SIZE = 50
WIKIPEDIA_SITELINK_BATCH_SIZE = 50

WDT_P31 = URIRef("http://www.wikidata.org/prop/direct/P31")
WDT_P279 = URIRef("http://www.wikidata.org/prop/direct/P279")

ABOUT_FETCH_TIMEOUT = 30
ABOUT_FETCH_HEADERS = {
    'User-Agent': 'BlogEntityExtractor/1.0 (https://github.com/cmahnke)',
    'Accept': 'application/ld+json, application/json;q=0.9, */*;q=0.1'
}

GETTY_AAT_URL_RE = re.compile(r'^https?://vocab\.getty\.edu/aat/(\d+)/?$')
GETTY_AAT_PAGE_RE = re.compile(r'^https?://vocab\.getty\.edu/page/aat/(\d+)/?$')


def query_delay():
    time.sleep(CONFIG['query_delay'])


# ── Identifier-Properties ──

def fetch_identifier_properties() -> set[str]:
    global _identifier_properties_cache
    if _identifier_properties_cache is not None:
        return _identifier_properties_cache
    logger.info("Lade externe Identifier-Properties von Wikidata...")
    data = sparql_query_with_retry("""
    PREFIX wikibase: <http://wikiba.se/ontology#>
    SELECT DISTINCT ?prop WHERE {
        ?prop a wikibase:Property ;
              wikibase:propertyType wikibase:ExternalId .
    }
    """)
    if data is None:
        logger.warning("Konnte Identifier-Properties nicht laden.")
        _identifier_properties_cache = set()
        return _identifier_properties_cache
    props = set()
    for r in data.get('results', {}).get('bindings', []):
        pid = extract_property_id(r['prop']['value'])
        if pid:
            props.add(pid)
    _identifier_properties_cache = props
    logger.info(f"  → {len(props)} externe Identifier-Properties geladen")
    return _identifier_properties_cache


def get_effective_properties(include_identifiers: bool = True) -> set[str]:
    effective = DEFAULT_PROPERTIES.copy()
    if include_identifiers:
        id_props = fetch_identifier_properties()
        if id_props:
            before = len(effective)
            effective.update(id_props)
            added = len(effective) - before
            if added > 0:
                logger.info(
                    f"  Property-Whitelist: {before} kuratierte + {len(id_props)} Identifier "
                    f"= {len(effective)} ({added} neu)"
                )
    return effective


# ── URI-Erkennung ──

def _normalize_wikidata_uri(url: str) -> str | None:
    m = WD_ENTITY_BROAD_RE.match(url)
    if m:
        return f"http://www.wikidata.org/entity/{m.group(1)}"
    return None

def _resolve_getty_aat_url(url: str) -> str | None:
    m = GETTY_AAT_URL_RE.match(url)
    if m:
        return f"http://vocab.getty.edu/aat/{m.group(1)}.jsonld"
    m = GETTY_AAT_PAGE_RE.match(url)
    if m:
        return f"http://vocab.getty.edu/aat/{m.group(1)}.jsonld"
    return None


# ── Hilfsfunktionen ──

def bind_standard_prefixes(graph: Graph) -> None:
    for prefix, namespace in NAMESPACE_PREFIXES.items():
        graph.bind(prefix, namespace, override=True)

def build_language_filter(languages: list[str]) -> str:
    lc = " || ".join(f'LANG(?o) = "{l}"' for l in languages)
    return f'FILTER(!isLiteral(?o) || LANG(?o) = "" || {lc})'

def parse_languages(lang_string: str) -> list[str]:
    languages = [l.strip().lower() for l in lang_string.split(',') if l.strip()]
    if not languages:
        languages = DEFAULT_LANGUAGES.copy()
    if ALWAYS_INCLUDE_LANG not in languages:
        languages.append(ALWAYS_INCLUDE_LANG)
    return languages

def is_literal_in_allowed_languages(
    value: str, lang: str | None, datatype: str | None, predicate: str, allowed: list[str]
) -> bool:
    if not lang or lang == '':
        return True
    if predicate in LANG_SENSITIVE_PROPERTIES:
        return lang in allowed
    return True

def should_include_outgoing_triple(predicate_str: str, object_str: str | None, include_statements: bool) -> bool:
    if include_statements:
        return True
    if is_statement_link_predicate(predicate_str):
        return False
    if object_str and is_statement_node(object_str):
        return False
    return True

def detect_rdf_format(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    fmt = FORMAT_MAP.get(ext)
    if fmt is None:
        logger.warning(f"Unbekannte Endung '{ext}'. Fallback: turtle.")
        return 'turtle'
    return fmt

def is_valid_python_date(lexical_value: str, datatype: str) -> bool:
    if datatype not in DATE_DATATYPES:
        return True
    match = DATETIME_YEAR_RE.match(lexical_value)
    if not match:
        return True
    try:
        year = int(match.group(1))
    except ValueError:
        return True
    return DATETIME_YEAR_MIN <= year <= DATETIME_YEAR_MAX

def safe_literal(value: str, datatype: str | None = None, lang: str | None = None) -> Literal:
    if datatype and not is_valid_python_date(value, datatype):
        prev = RDFLIB_TERM_LOGGER.level
        RDFLIB_TERM_LOGGER.setLevel(logging.ERROR)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                lit = Literal(value, datatype=URIRef(datatype))
        finally:
            RDFLIB_TERM_LOGGER.setLevel(prev)
        return lit
    if lang:
        return Literal(value, lang=lang)
    elif datatype:
        return Literal(value, datatype=URIRef(datatype))
    else:
        return Literal(value)

def extract_property_id(uri_str: str) -> str | None:
    match = PROPERTY_ID_RE.search(uri_str)
    return match.group(1) if match else None

def is_statement_node(uri_str: str) -> bool:
    return bool(STATEMENT_NODE_RE.match(uri_str))

def is_statement_link_predicate(predicate_str: str) -> bool:
    return bool(PROP_STATEMENT_LINK_RE.match(predicate_str))

def extract_cached_property_ids(graph: Graph) -> set[str]:
    cached = set()
    for subject in graph.subjects(RDFS.label, None):
        pid = extract_property_id(str(subject))
        if pid:
            cached.add(pid)
    if cached:
        logger.info(f"Label-Cache: {len(cached)} Property-Labels aus Graph geladen")
    return cached

def parse_sparql_binding_to_rdf(
    binding: dict, languages: list[str] | None = None, predicate_str: str | None = None
) -> URIRef | Literal | None:
    if binding['type'] == 'uri':
        return URIRef(binding['value'])
    elif binding['type'] in ('literal', 'typed-literal'):
        o_lang = binding.get('xml:lang')
        o_datatype = binding.get('datatype')
        o_value = binding['value']
        if languages and predicate_str:
            if not is_literal_in_allowed_languages(o_value, o_lang, o_datatype, predicate_str, languages):
                return None
        return safe_literal(value=o_value, datatype=o_datatype, lang=o_lang)
    return None

def is_already_fetched(uri_ref: URIRef, graph: Graph) -> bool:
    return (uri_ref, FETCHED_MARKER, FETCHED_VALUE) in graph

def mark_as_fetched(uri_ref: URIRef, graph: Graph) -> None:
    graph.add((uri_ref, FETCHED_MARKER, FETCHED_VALUE))

def merge_graphs(target: Graph, source: Graph) -> int:
    before = len(target)
    for t in source:
        if t not in target:
            target.add(t)
    return len(target) - before

def save_graph(graph: Graph, path: str, fmt: str) -> bool:
    try:
        bind_standard_prefixes(graph)
        graph.serialize(destination=path, format=fmt)
        logger.info(f"Gespeichert: {path} ({len(graph)} Triples, {fmt})")
        return True
    except Exception as e:
        logger.error(f"Speicherfehler: {e}")
        return False


# ── SPARQL ──

def sparql_query_with_retry(query: str) -> dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                SPARQL_URL, data={'query': query},
                headers={**SPARQL_HEADERS, 'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 429:
                ra = resp.headers.get("Retry-After")
                try:
                    w = int(ra) + 1 if ra else None
                except (ValueError, TypeError):
                    w = None
                w = w or (RETRY_BASE_WAIT ** attempt) + 5
                logger.warning(f"Rate limit. Warte {w}s ({attempt+1}/{MAX_RETRIES})")
                time.sleep(w)
                continue
            if resp.status_code >= 500:
                w = (RETRY_BASE_WAIT ** attempt) + 1
                logger.warning(f"Server {resp.status_code}. Warte {w}s")
                time.sleep(w)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            time.sleep((RETRY_BASE_WAIT ** attempt) + 1)
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Verbindungsfehler: {e}")
            time.sleep((RETRY_BASE_WAIT ** attempt) + 2)
        except Exception as e:
            logger.error(f"Fehler: {e}")
            if attempt >= MAX_RETRIES - 1:
                return None
            time.sleep(1)
    logger.error(f"SPARQL nach {MAX_RETRIES} Versuchen fehlgeschlagen.")
    return None


def build_whitelist_sparql(uri: str, languages: list[str], properties: set[str]) -> str:
    lang_filter = build_language_filter(languages)
    wdt_values = " ".join(f"wdt:{pid}" for pid in sorted(properties))
    other_preds = " ".join(f"<{p}>" for p in sorted(DEFAULT_KEEP_PREDICATES))
    return f"""
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT ?p ?o WHERE {{
        {{ VALUES ?p {{ {wdt_values} }} <{uri}> ?p ?o . }}
        UNION
        {{ VALUES ?p {{ {other_preds} }} <{uri}> ?p ?o . }}
        {lang_filter}
    }}
    """

def build_whitelist_sparql_with_classification(
    uri: str, languages: list[str], properties: set[str]
) -> str:
    lang_filter = build_language_filter(languages)
    wdt_values = " ".join(f"wdt:{pid}" for pid in sorted(properties))
    other_preds = " ".join(f"<{p}>" for p in sorted(DEFAULT_KEEP_PREDICATES))
    base_values = " ".join(f"wd:{qid}" for qid in sorted(ENTITY_BASE_CLASSES))
    return f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT ?p ?o WHERE {{
        {{ VALUES ?p {{ {wdt_values} }} <{uri}> ?p ?o . }}
        UNION
        {{ VALUES ?p {{ {other_preds} }} <{uri}> ?p ?o . }}
        UNION
        {{
            VALUES ?baseClass {{ {base_values} }}
            <{uri}> wdt:P31/wdt:P279* ?baseClass .
            BIND(wdt:P31 AS ?p)
            BIND(?baseClass AS ?o)
        }}
        {lang_filter}
    }}
    """

def build_incoming_sparql(uri: str, fetch_all: bool, include_statements: bool) -> str:
    if include_statements:
        return f"SELECT ?s ?p WHERE {{ ?s ?p <{uri}> }} LIMIT {INCOMING_LIMIT}"
    elif fetch_all:
        return f"""
        SELECT ?s ?p WHERE {{
            ?s ?p <{uri}> .
            FILTER(!STRSTARTS(STR(?s), "http://www.wikidata.org/entity/statement/")
                && !REGEX(STR(?p), "^http://www.wikidata.org/prop/P[0-9]+$"))
        }} LIMIT {INCOMING_LIMIT}
        """
    else:
        return f"""
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        SELECT ?s ?p WHERE {{
            ?s ?p <{uri}> .
            FILTER(STRSTARTS(STR(?s), "http://www.wikidata.org/entity/Q")
                && STRSTARTS(STR(?p), "http://www.wikidata.org/prop/direct/"))
        }} LIMIT {INCOMING_LIMIT}
        """


# ── Wikipedia Sitelinks – gesammelt ──

def build_wikipedia_sitelinks_query(entity_uris: list[str], languages: list[str]) -> str:
    values_entities = " ".join(f"<{u}>" for u in entity_uris)
    site_filters = " || ".join(
        f'?site = <https://{lang}.wikipedia.org/>' for lang in languages if lang != 'mul'
    )
    if not site_filters:
        return ""
    return f"""
    PREFIX schema: <http://schema.org/>
    SELECT ?entity ?article ?siteLang WHERE {{
        VALUES ?entity {{ {values_entities} }}
        ?article schema:about ?entity ; schema:isPartOf ?site ; schema:inLanguage ?siteLang .
        FILTER({site_filters})
    }}
    """

def fetch_all_wikipedia_sitelinks(
    entity_uris: list[str], target_graph: Graph, languages: list[str]
) -> int:
    if not entity_uris:
        return 0
    wiki_languages = [l for l in languages if l != 'mul']
    if not wiki_languages:
        return 0
    needed = []
    for uri_str in entity_uris:
        uri_ref = URIRef(uri_str)
        if not WD_ENTITY_RE.match(uri_str):
            continue
        has_wiki = any('wikipedia.org' in str(o)
                       for o in target_graph.objects(uri_ref, SCHEMA_HTTP['sameAs']))
        if not has_wiki:
            has_wiki = any('wikipedia.org' in str(o)
                          for o in target_graph.objects(uri_ref, SCHEMA_HTTPS['sameAs']))
        if not has_wiki:
            needed.append(uri_str)
    if not needed:
        return 0
    logger.info(f"\nWikipedia-Sitelinks: {len(needed)} Entities...")
    total_added = 0
    for bs in range(0, len(needed), WIKIPEDIA_SITELINK_BATCH_SIZE):
        batch = needed[bs:bs + WIKIPEDIA_SITELINK_BATCH_SIZE]
        query = build_wikipedia_sitelinks_query(batch, languages)
        if not query:
            continue
        data = sparql_query_with_retry(query)
        if data is None:
            continue
        added = 0
        for r in data.get('results', {}).get('bindings', []):
            t = (URIRef(r['entity']['value']), SCHEMA_HTTP['sameAs'], URIRef(r['article']['value']))
            if t not in target_graph:
                target_graph.add(t)
                added += 1
        total_added += added
        query_delay()
    if total_added > 0:
        logger.info(f"  → {total_added} Wikipedia-Sitelink-Triples hinzugefügt")
    return total_added


# ── Label-Fetching ──

def fetch_property_labels(
    property_ids: set[str], target_graph: Graph, languages: list[str], label_cache: set[str]
) -> int:
    if not property_ids:
        return 0
    uncached = property_ids - label_cache
    if not uncached:
        return 0
    logger.info(f"  Rufe Labels für {len(uncached)} neue Properties ab ({len(property_ids)-len(uncached)} im Cache)")
    all_uncached = sorted(uncached)
    total_added = 0
    for bs in range(0, len(all_uncached), LABEL_BATCH_SIZE):
        batch = all_uncached[bs:bs + LABEL_BATCH_SIZE]
        values_clause = " ".join(f"wd:{pid}" for pid in batch)
        lang_filter = " || ".join(f'LANG(?label) = "{l}"' for l in languages)
        data = sparql_query_with_retry(f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?prop ?label WHERE {{
            VALUES ?prop {{ {values_clause} }}
            ?prop rdfs:label ?label . FILTER({lang_filter})
        }}
        """)
        if data is None:
            continue
        added = 0
        for result in data.get('results', {}).get('bindings', []):
            prop_uri = URIRef(result['prop']['value'])
            lv = result['label']['value']
            ll = result['label'].get('xml:lang')
            label = Literal(lv, lang=ll) if ll else Literal(lv)
            t = (prop_uri, RDFS.label, label)
            if t not in target_graph:
                target_graph.add(t)
                added += 1
        for pid in batch:
            eu = URIRef(f"http://www.wikidata.org/entity/{pid}")
            for tu in [
                URIRef(f"http://www.wikidata.org/prop/direct/{pid}"),
                URIRef(f"http://www.wikidata.org/prop/direct-normalized/{pid}"),
                URIRef(f"http://www.wikidata.org/prop/statement/{pid}"),
                URIRef(f"http://www.wikidata.org/prop/statement/value/{pid}"),
                URIRef(f"http://www.wikidata.org/prop/qualifier/{pid}"),
                URIRef(f"http://www.wikidata.org/prop/qualifier/value/{pid}"),
                URIRef(f"http://www.wikidata.org/prop/reference/{pid}"),
                URIRef(f"http://www.wikidata.org/prop/reference/value/{pid}"),
                URIRef(f"http://www.wikidata.org/prop/{pid}"),
                URIRef(f"http://www.wikidata.org/prop/novalue/{pid}"),
            ]:
                for label in target_graph.objects(eu, RDFS.label):
                    t = (tu, RDFS.label, label)
                    if t not in target_graph:
                        target_graph.add(t)
                        added += 1
            label_cache.add(pid)
        total_added += added
        if len(all_uncached) > LABEL_BATCH_SIZE:
            query_delay()
    if total_added > 0:
        logger.info(f"  → {total_added} Property-Label-Triples hinzugefügt")
    return total_added

def preload_property_labels(
    effective_properties: set[str], target_graph: Graph,
    languages: list[str], label_cache: set[str]
) -> int:
    uncached = effective_properties - label_cache
    if not uncached:
        logger.info(f"Property-Labels: Alle {len(effective_properties)} bereits im Cache.")
        return 0
    logger.info(f"Lade {len(uncached)} Property-Labels vorab ({len(label_cache)} im Cache)...")
    return fetch_property_labels(uncached, target_graph, languages, label_cache)

def fetch_entity_labels(entity_uris: set[str], target_graph: Graph, languages: list[str]) -> int:
    if not entity_uris:
        return 0
    needed = {u for u in entity_uris if not any(target_graph.objects(URIRef(u), RDFS.label))}
    if not needed:
        return 0
    logger.info(f"  Rufe Labels für {len(needed)} Entities ab...")
    all_needed = sorted(needed)
    total_added = 0
    lang_filter_parts = " || ".join(f'LANG(?label) = "{l}"' for l in languages)
    for bs in range(0, len(all_needed), LABEL_BATCH_SIZE):
        batch = all_needed[bs:bs + LABEL_BATCH_SIZE]
        values_clause = " ".join(f"<{u}>" for u in batch)
        data = sparql_query_with_retry(f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?entity ?label WHERE {{
            VALUES ?entity {{ {values_clause} }}
            ?entity rdfs:label ?label . FILTER({lang_filter_parts})
        }}
        """)
        if data is None:
            continue
        added = 0
        for r in data.get('results', {}).get('bindings', []):
            e_uri = URIRef(r['entity']['value'])
            lv = r['label']['value']
            ll = r['label'].get('xml:lang')
            label = Literal(lv, lang=ll) if ll else Literal(lv)
            t = (e_uri, RDFS.label, label)
            if t not in target_graph:
                target_graph.add(t)
                added += 1
        total_added += added
        query_delay()
    if total_added > 0:
        logger.info(f"  → {total_added} Entity-Label-Triples hinzugefügt")
    return total_added


# ── Statement Details ──

def fetch_statement_details(
    statement_uris: set[str], target_graph: Graph, languages: list[str], label_cache: set[str]
) -> int:
    if not statement_uris:
        return 0
    logger.info(f"  Rufe Details für {len(statement_uris)} Statement-Nodes ab...")
    lang_filter = build_language_filter(languages)
    total_added = 0
    collected_pids = set()
    STMT_BATCH = 20
    all_stmts = sorted(statement_uris)
    for bs in range(0, len(all_stmts), STMT_BATCH):
        batch = all_stmts[bs:bs + STMT_BATCH]
        vc = " ".join(f"<{u}>" for u in batch)
        data = sparql_query_with_retry(f"""
        SELECT ?stmt ?p ?o WHERE {{
            VALUES ?stmt {{ {vc} }} ?stmt ?p ?o . {lang_filter}
        }}
        """)
        if data is None:
            continue
        added = 0
        for r in data.get('results', {}).get('bindings', []):
            su = URIRef(r['stmt']['value'])
            ps = r['p']['value']
            p = URIRef(ps)
            pid = extract_property_id(ps)
            if pid:
                collected_pids.add(pid)
            o = parse_sparql_binding_to_rdf(r['o'], languages, ps)
            if o is None:
                continue
            t = (su, p, o)
            if t not in target_graph:
                target_graph.add(t)
                added += 1
        total_added += added
        query_delay()
    if collected_pids:
        total_added += fetch_property_labels(collected_pids, target_graph, languages, label_cache)
    if total_added > 0:
        logger.info(f"  → {total_added} Statement-Detail-Triples hinzugefügt")
    return total_added


# ─────────────────────────────────────────────────────────────────────
# Type Hierarchy (P279 Auflösung)
#
# Sammelt Werte von konfigurierbaren Properties (P31, P106, P136, ...)
# aus dem Graph und löst deren P279-Kette transitiv auf.
# So wird z.B. P106=Q1028181 (Maler) → P279 → Q483507 (Künstler)
# als explizites Triple im Graph verfügbar.
# ─────────────────────────────────────────────────────────────────────

def collect_values_for_hierarchy(
    graph: Graph, entity_uris: list[URIRef], properties: set[str]
) -> set[str]:
    """
    Sammelt alle Q-Entity-Werte der angegebenen Properties
    für die gegebenen Entities aus dem Graph.
    """
    value_uris = set()
    for pid in properties:
        pred = URIRef(f"http://www.wikidata.org/prop/direct/{pid}")
        for entity_uri in entity_uris:
            for obj in graph.objects(entity_uri, pred):
                obj_str = str(obj)
                if WD_ENTITY_RE.match(obj_str):
                    value_uris.add(obj_str)
    return value_uris


def fetch_superclasses_batch(class_uris: set[str]) -> dict[str, list[str]]:
    if not class_uris:
        return {}
    all_uris = sorted(class_uris)
    result: dict[str, list[str]] = {}
    for bs in range(0, len(all_uris), HIERARCHY_BATCH_SIZE):
        batch = all_uris[bs:bs + HIERARCHY_BATCH_SIZE]
        values_clause = " ".join(f"<{u}>" for u in batch)
        data = sparql_query_with_retry(f"""
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        SELECT ?child ?parent WHERE {{
            VALUES ?child {{ {values_clause} }}
            ?child wdt:P279 ?parent .
            FILTER(STRSTARTS(STR(?parent), "http://www.wikidata.org/entity/Q"))
        }}
        """)
        if data is None:
            continue
        for r in data.get('results', {}).get('bindings', []):
            result.setdefault(r['child']['value'], []).append(r['parent']['value'])
        query_delay()
    return result


def resolve_type_hierarchies(
    target_graph: Graph, entity_uris: list[URIRef],
    languages: list[str], label_cache: set[str],
    max_depth: int = HIERARCHY_MAX_DEPTH,
    resolve_properties: set[str] | None = None
) -> bool:
    """
    Löst P279-Hierarchien auf für Werte von konfigurierbaren Properties.

    Standardmäßig werden Werte von HIERARCHY_RESOLVE_PROPERTIES aufgelöst
    (P31, P106, P136, P101, P452, P279, P1435).

    Für jede gefundene Q-Entity als Wert dieser Properties wird die
    P279-Kette (subclass of) transitiv aufgelöst und als explizite
    Triples im Graph gespeichert.
    """
    if resolve_properties is None:
        resolve_properties = HIERARCHY_RESOLVE_PROPERTIES

    # Sammle alle Q-Entity-Werte der zu resolvenden Properties
    type_uris = collect_values_for_hierarchy(
        target_graph, entity_uris, resolve_properties
    )

    if not type_uris:
        logger.info("Typ-Hierarchie: Keine aufzulösenden Werte gefunden – überspringe.")
        return False

    prop_list = ", ".join(f"P{p}" if not p.startswith('P') else p for p in sorted(resolve_properties))
    logger.info(
        f"\n{'='*60}\n"
        f"Typ-Hierarchie: {len(type_uris)} Werte aus {len(resolve_properties)} Properties\n"
        f"  Properties: {prop_list}\n"
        f"  Max Tiefe: {max_depth}\n"
        f"{'='*60}"
    )

    total_triples_added = 0
    all_hierarchy_entities: set[str] = set()
    collected_pids: set[str] = {'P279'}
    current_level = type_uris.copy()
    visited: set[str] = set()
    depth = 0

    while current_level and depth < max_depth:
        depth += 1
        to_query = current_level - visited
        if not to_query:
            break
        logger.info(f"  Ebene {depth}: {len(to_query)} Klassen...")
        parent_map = fetch_superclasses_batch(to_query)
        visited.update(to_query)
        next_level: set[str] = set()
        added_this_level = 0
        for child_uri, parent_uris in parent_map.items():
            child_ref = URIRef(child_uri)
            all_hierarchy_entities.add(child_uri)
            for parent_uri in parent_uris:
                parent_ref = URIRef(parent_uri)
                all_hierarchy_entities.add(parent_uri)
                t = (child_ref, WDT_P279, parent_ref)
                if t not in target_graph:
                    target_graph.add(t)
                    added_this_level += 1
                marker = (parent_ref, HIERARCHY_MARKER, Literal(True))
                if marker not in target_graph:
                    target_graph.add(marker)
                if parent_uri not in visited:
                    next_level.add(parent_uri)
        for uri_str in to_query:
            if uri_str not in parent_map:
                all_hierarchy_entities.add(uri_str)
                marker = (URIRef(uri_str), HIERARCHY_MARKER, Literal(True))
                if marker not in target_graph:
                    target_graph.add(marker)
        total_triples_added += added_this_level
        logger.info(f"    → {added_this_level} P279-Triples, {len(next_level)} neue")
        current_level = next_level

    if depth >= max_depth and current_level:
        logger.warning(f"  Tiefe {max_depth} erreicht, {len(current_level)} offen")

    if all_hierarchy_entities:
        total_triples_added += fetch_entity_labels(
            all_hierarchy_entities, target_graph, languages
        )
    if collected_pids:
        total_triples_added += fetch_property_labels(
            collected_pids, target_graph, languages, label_cache
        )

    logger.info(
        f"\nTyp-Hierarchie: {len(all_hierarchy_entities)} Klassen, "
        f"{total_triples_added} Triples, {depth} Ebenen"
    )
    return total_triples_added > 0


# ── Entity-Klassifizierung (Batch-Fallback für -a Modus) ──

def classify_entities_batch(
    about_uris: list[URIRef], target_graph: Graph, languages: list[str]
) -> bool:
    wd_uris = [str(u) for u in about_uris if WD_ENTITY_RE.match(str(u))]
    if not wd_uris:
        return False
    base_class_refs = {
        URIRef(f"http://www.wikidata.org/entity/{qid}") for qid in ENTITY_BASE_CLASSES
    }
    needed = []
    for uri_str in wd_uris:
        uri_ref = URIRef(uri_str)
        if not set(target_graph.objects(uri_ref, WDT_P31)) & base_class_refs:
            needed.append(uri_str)
    if not needed:
        return False
    base_class_values = " ".join(f"wd:{qid}" for qid in sorted(ENTITY_BASE_CLASSES))
    logger.info(f"\nEntity-Klassifizierung: {len(needed)} Entities...")
    total_added = 0
    classified_count = 0
    base_labels_needed: set[str] = set()
    for bs in range(0, len(needed), CLASSIFY_BATCH_SIZE):
        batch = needed[bs:bs + CLASSIFY_BATCH_SIZE]
        values_entities = " ".join(f"<{u}>" for u in batch)
        data = sparql_query_with_retry(f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        SELECT ?entity ?baseClass WHERE {{
            VALUES ?entity {{ {values_entities} }}
            VALUES ?baseClass {{ {base_class_values} }}
            ?entity wdt:P31/wdt:P279* ?baseClass .
        }}
        """)
        if data is None:
            query_delay()
            continue
        entity_bases: dict[str, set[str]] = {}
        for r in data.get('results', {}).get('bindings', []):
            entity_bases.setdefault(r['entity']['value'], set()).add(r['baseClass']['value'])
        added = 0
        for entity_uri, base_uris in entity_bases.items():
            entity_ref = URIRef(entity_uri)
            entity_new = False
            for base_uri in base_uris:
                base_ref = URIRef(base_uri)
                t = (entity_ref, WDT_P31, base_ref)
                if t not in target_graph:
                    target_graph.add(t)
                    added += 1
                    entity_new = True
                    base_labels_needed.add(base_uri)
            if entity_new:
                classified_count += 1
        total_added += added
        query_delay()
    if base_labels_needed:
        total_added += fetch_entity_labels(base_labels_needed, target_graph, languages)
    if classified_count > 0:
        logger.info(f"  → {classified_count} Entities klassifiziert, {total_added} Triples")
    return total_added > 0


# ── Wikidata Statement Fetching ──

def fetch_wikidata_statements(
    uri: str, target_graph: Graph, current: int, total: int,
    languages: list[str], label_cache: set[str],
    effective_properties: set[str],
    fetch_all: bool = False, include_statements: bool = False,
    force_update: bool = False, classify: bool = True
) -> bool:
    canonical = _normalize_wikidata_uri(str(uri))
    if canonical:
        uri = canonical
    if "wikidata.org/entity/" not in str(uri):
        return False
    uri_ref = URIRef(uri)
    if not force_update and is_already_fetched(uri_ref, target_graph):
        logger.info(f"[{current}/{total}] Überspringe {uri}: bereits abgerufen.")
        return False
    logger.info(f"[{current}/{total}] Hole Wikidata-Statements für: {uri}")
    if fetch_all:
        lf = build_language_filter(languages)
        out_query = f"SELECT ?p ?o WHERE {{ <{uri}> ?p ?o . {lf} }}"
    elif classify:
        out_query = build_whitelist_sparql_with_classification(uri, languages, effective_properties)
    else:
        out_query = build_whitelist_sparql(uri, languages, effective_properties)
    in_query = build_incoming_sparql(uri, fetch_all, include_statements)
    wikidata_graph = Graph()
    collected_pids = set()
    collected_stmts = set()
    skipped = 0
    data = sparql_query_with_retry(out_query)
    if data is None:
        logger.error(f"Ausgehende Abfrage fehlgeschlagen für {uri}")
    else:
        for r in data.get('results', {}).get('bindings', []):
            p_str = r['p']['value']
            p = URIRef(p_str)
            pid = extract_property_id(p_str)
            if pid:
                collected_pids.add(pid)
            o = parse_sparql_binding_to_rdf(r['o'], languages, p_str)
            if o is None:
                continue
            o_str = str(o) if isinstance(o, URIRef) else None
            if fetch_all and not should_include_outgoing_triple(p_str, o_str, include_statements):
                skipped += 1
                continue
            if include_statements and isinstance(o, URIRef) and is_statement_node(str(o)):
                collected_stmts.add(str(o))
            wikidata_graph.add((uri_ref, p, o))
    query_delay()
    data = sparql_query_with_retry(in_query)
    if data is None:
        logger.error(f"Eingehende Abfrage fehlgeschlagen für {uri}")
    else:
        for r in data.get('results', {}).get('bindings', []):
            s = URIRef(r['s']['value'])
            p_str = r['p']['value']
            p = URIRef(p_str)
            pid = extract_property_id(p_str)
            if pid:
                collected_pids.add(pid)
            wikidata_graph.add((s, p, uri_ref))
    query_delay()
    wd_preds = set(wikidata_graph.predicates(subject=uri_ref))
    override_preds = wd_preds & WIKIDATA_OVERRIDES_PROPERTIES
    removed = 0
    for pred in override_preds:
        for t in list(target_graph.triples((uri_ref, pred, None))):
            target_graph.remove(t)
            removed += 1
    if removed:
        logger.info(f"  → {removed} Override-Triples entfernt")
    added = 0
    for t in wikidata_graph:
        if t not in target_graph:
            target_graph.add(t)
            added += 1
    stmt_count = 0
    if include_statements and collected_stmts:
        stmt_count = fetch_statement_details(collected_stmts, target_graph, languages, label_cache)
    label_count = 0
    new_pids = collected_pids - label_cache
    if new_pids:
        label_count = fetch_property_labels(new_pids, target_graph, languages, label_cache)
    mark_as_fetched(uri_ref, target_graph)
    changed = (removed + added + label_count + stmt_count) > 0
    parts = [f"{added} hinzugefügt", f"{removed} ersetzt"]
    if label_count:
        parts.append(f"{label_count} Labels")
    if stmt_count:
        parts.append(f"{stmt_count} Statements")
    if skipped:
        parts.append(f"{skipped} gefiltert")
    logger.info(f"  → {', '.join(parts)} für {uri}")
    return changed


# ── JSON-LD about-Referenz-Auflösung ──

def _is_id_only_about(about_obj: dict | str) -> str | None:
    if isinstance(about_obj, str):
        if about_obj.startswith(('http://', 'https://')):
            return about_obj
        return None
    if not isinstance(about_obj, dict):
        return None
    id_value = about_obj.get('@id')
    if not id_value:
        return None
    meaningful_keys = {k for k in about_obj.keys() if k not in ('@id', '@type')}
    if meaningful_keys:
        return None
    if id_value.startswith(('http://', 'https://')):
        return id_value
    return None

def _collect_id_only_abouts(obj: dict | list | str, collected: set[str]) -> None:
    if isinstance(obj, list):
        for item in obj:
            _collect_id_only_abouts(item, collected)
        return
    if not isinstance(obj, dict):
        return
    if '@graph' in obj:
        _collect_id_only_abouts(obj['@graph'], collected)
    about_keys = ('about', 'schema:about', 'http://schema.org/about', 'https://schema.org/about')
    for about_key in about_keys:
        if about_key in obj:
            about_val = obj[about_key]
            if isinstance(about_val, list):
                for item in about_val:
                    url = _is_id_only_about(item)
                    if url:
                        collected.add(url)
                    if isinstance(item, dict):
                        _collect_id_only_abouts(item, collected)
            else:
                url = _is_id_only_about(about_val)
                if url:
                    collected.add(url)
                if isinstance(about_val, dict):
                    _collect_id_only_abouts(about_val, collected)
    for key, value in obj.items():
        if key.startswith('@') or key in about_keys:
            continue
        if isinstance(value, (dict, list)):
            _collect_id_only_abouts(value, collected)

def _extract_jsonld_from_response(response_text: str, url: str) -> list[dict]:
    try:
        data = json.loads(response_text)
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    except (json.JSONDecodeError, ValueError):
        pass
    results = []
    script_pattern = re.compile(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.DOTALL | re.IGNORECASE
    )
    for match in script_pattern.findall(response_text):
        try:
            data = json.loads(match.strip())
            if isinstance(data, dict):
                results.append(data)
            elif isinstance(data, list):
                results.extend(item for item in data if isinstance(item, dict))
        except (json.JSONDecodeError, ValueError):
            pass
    return results

def _fetch_and_parse_jsonld_url(url: str) -> Graph | None:
    getty_url = _resolve_getty_aat_url(url)
    if getty_url:
        logger.info(f"    Erkannt als getty-aat: {url}")
        headers = dict(ABOUT_FETCH_HEADERS)
        headers['Accept'] = 'application/ld+json, application/json;q=0.9'
        try:
            resp = requests.get(getty_url, headers=headers,
                                timeout=ABOUT_FETCH_TIMEOUT, allow_redirects=True)
            resp.raise_for_status()
            g = Graph()
            g.parse(data=resp.text, format='json-ld')
            if len(g) > 0:
                return g
        except Exception as e:
            logger.debug(f"    Getty-AAT-Abruf fehlgeschlagen: {e}")
    try:
        resp = requests.get(url, headers=ABOUT_FETCH_HEADERS,
                            timeout=ABOUT_FETCH_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.debug(f"  Fehler beim Abrufen von {url}: {e}")
        return None
    content_type = resp.headers.get('Content-Type', '').lower()
    if any(ct in content_type for ct in ('json', 'ld+json')):
        try:
            g = Graph()
            g.parse(data=resp.text, format='json-ld')
            if len(g) > 0:
                return g
        except Exception:
            pass
    jsonld_objects = _extract_jsonld_from_response(resp.text, url)
    if not jsonld_objects:
        return None
    combined_graph = Graph()
    for jsonld_obj in jsonld_objects:
        try:
            temp_graph = Graph()
            temp_graph.parse(data=json.dumps(jsonld_obj), format='json-ld')
            for triple in temp_graph:
                combined_graph.add(triple)
        except Exception:
            pass
    return combined_graph if len(combined_graph) > 0 else None

def _collect_linked_data_uris_from_graph(graph: Graph) -> tuple[set[str], set[str]]:
    wikidata_uris: set[str] = set()
    getty_aat_uris: set[str] = set()
    all_uris: set[str] = set()
    for s, p, o in graph:
        if isinstance(s, URIRef):
            all_uris.add(str(s))
        if isinstance(o, URIRef):
            all_uris.add(str(o))
    for uri_str in all_uris:
        canonical_wd = _normalize_wikidata_uri(uri_str)
        if canonical_wd:
            wikidata_uris.add(canonical_wd)
            continue
        if _resolve_getty_aat_url(uri_str):
            getty_aat_uris.add(uri_str)
    return (wikidata_uris, getty_aat_uris)

def _fetch_getty_uris_into_graph(getty_uris: set[str], target_graph: Graph) -> int:
    if not getty_uris:
        return 0
    needed = set()
    for uri_str in getty_uris:
        if not any(target_graph.objects(URIRef(uri_str), RDFS.label)):
            needed.add(uri_str)
    if not needed:
        return 0
    logger.info(f"  Rufe {len(needed)} Getty AAT Einträge ab...")
    total_added = 0
    for url in sorted(needed):
        getty_jsonld_url = _resolve_getty_aat_url(url)
        if not getty_jsonld_url:
            continue
        logger.info(f"    Getty AAT: {url}")
        headers = dict(ABOUT_FETCH_HEADERS)
        headers['Accept'] = 'application/ld+json, application/json;q=0.9'
        try:
            resp = requests.get(getty_jsonld_url, headers=headers,
                                timeout=ABOUT_FETCH_TIMEOUT, allow_redirects=True)
            resp.raise_for_status()
            g = Graph()
            g.parse(data=resp.text, format='json-ld')
            added = merge_graphs(target_graph, g)
            if added > 0:
                logger.info(f"    ✓ {added} Triples ({len(g)} gesamt)")
                total_added += added
        except Exception as e:
            logger.warning(f"    ✗ Fehler: {e}")
        query_delay()
    if total_added > 0:
        logger.info(f"  → {total_added} Getty-AAT-Triples hinzugefügt")
    return total_added

def resolve_about_references(
    raw_json: dict | list, schema_graph: Graph
) -> tuple[Graph, set[str]]:
    id_only_urls: set[str] = set()
    _collect_id_only_abouts(raw_json, id_only_urls)
    if not id_only_urls:
        logger.info("About-Auflösung: Keine @id-only about-Referenzen gefunden.")
        wd_uris, getty_uris = _collect_linked_data_uris_from_graph(schema_graph)
        _fetch_getty_uris_into_graph(getty_uris, schema_graph)
        return (schema_graph, wd_uris)
    wikidata_from_ids: set[str] = set()
    non_wikidata_urls: set[str] = set()
    for url in id_only_urls:
        canonical = _normalize_wikidata_uri(url)
        if canonical:
            wikidata_from_ids.add(canonical)
        else:
            non_wikidata_urls.add(url)
    parts = []
    if wikidata_from_ids:
        parts.append(f"{len(wikidata_from_ids)} Wikidata (→ SPARQL)")
    if non_wikidata_urls:
        parts.append(f"{len(non_wikidata_urls)} andere (→ JSON-LD)")
    logger.info(f"About-Auflösung: {len(id_only_urls)} @id-only URLs ({', '.join(parts)})")
    total_added = 0
    resolved = 0
    failed = 0
    for url in sorted(non_wikidata_urls):
        getty_url = _resolve_getty_aat_url(url)
        source_label = 'getty-aat' if getty_url else 'generisch'
        logger.info(f"  Löse auf [{source_label}]: {url}")
        fetched_graph = _fetch_and_parse_jsonld_url(url)
        if fetched_graph is None:
            logger.warning(f"  ✗ Konnte kein JSON-LD laden von: {url}")
            failed += 1
            continue
        added = merge_graphs(schema_graph, fetched_graph)
        if added > 0:
            logger.info(f"  ✓ {added} Triples von: {url}")
            total_added += added
        else:
            logger.info(f"  ○ Bereits vorhanden von: {url}")
        resolved += 1
        query_delay()
    if non_wikidata_urls:
        logger.info(f"About-Auflösung: {resolved} aufgelöst, {failed} fehlgeschlagen, {total_added} Triples")
    wd_uris_from_graph, getty_uris_from_graph = _collect_linked_data_uris_from_graph(schema_graph)
    all_wikidata_uris = wikidata_from_ids | wd_uris_from_graph
    _fetch_getty_uris_into_graph(getty_uris_from_graph, schema_graph)
    if all_wikidata_uris:
        logger.info(f"About-Auflösung: {len(all_wikidata_uris)} Wikidata-URIs (→ SPARQL)")
    return (schema_graph, all_wikidata_uris)


# ── Graph Loading ──

def load_schema_graph(input_source: str) -> tuple[Graph, dict | list | None]:
    g = Graph()
    raw_json = None
    try:
        if input_source.startswith(('http://', 'https://')):
            logger.info(f"Lade JSON-LD von URL: {input_source}")
            resp = requests.get(input_source, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            content = resp.text
        else:
            logger.info(f"Lade JSON-LD von Datei: {input_source}")
            if not os.path.exists(input_source):
                logger.error(f"Nicht gefunden: {input_source}")
                sys.exit(1)
            with open(input_source, 'r', encoding='utf-8') as f:
                content = f.read()
        try:
            raw_json = json.loads(content)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"JSON-Voranalyse fehlgeschlagen: {e}")
        g.parse(data=content, format="json-ld")
        logger.info(f"{len(g)} Triples aus Eingabe geparst.")
    except requests.exceptions.RequestException as e:
        logger.error(f"URL-Fehler: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Parse-Fehler: {e}")
        sys.exit(1)
    return (g, raw_json)

def extract_about_uris(schema_graph: Graph) -> list[URIRef]:
    blogs = (
        list(schema_graph.subjects(RDF.type, SCHEMA_HTTP.Blog))
        + list(schema_graph.subjects(RDF.type, SCHEMA_HTTPS.Blog))
    )
    if not blogs:
        logger.error("KEIN Blog-Entity gefunden!")
        types = set(schema_graph.objects(None, RDF.type))
        if types:
            logger.info(f"Typen: {[str(t) for t in types]}")
        sys.exit(1)
    logger.info(f"{len(blogs)} Blog-Entities gefunden")
    results = schema_graph.query("""
    PREFIX s_http: <http://schema.org/>
    PREFIX s_https: <https://schema.org/>
    SELECT DISTINCT ?about WHERE {
        {
            ?blog a s_http:Blog .
            ?blog (s_http:blogPost|s_http:blogPosting) ?post .
            ?post s_http:about ?about .
        } UNION {
            ?blog a s_https:Blog .
            ?blog (s_https:blogPost|s_https:blogPosting) ?post .
            ?post s_https:about ?about .
        }
        FILTER(isURI(?about))
    }
    """)
    seen = set()
    uris = []
    for row in results:
        s = str(row.about)
        if s not in seen:
            seen.add(s)
            uris.append(row.about)
    return uris


# ── Main ──

def main():
    parser = argparse.ArgumentParser(description="Schema.org JSON-LD → Wikidata-Anreicherung")
    parser.add_argument("input", help="URL oder Pfad zur JSON-LD Datei")
    parser.add_argument("-o", "--output", default="enriched_entities.ttl",
                        help="Ausgabe-RDF-Datei (Standard: enriched_entities.ttl)")
    parser.add_argument("-l", "--languages", default=",".join(DEFAULT_LANGUAGES),
                        help=f"Sprachen (Standard: {','.join(DEFAULT_LANGUAGES)})")
    parser.add_argument("-a", "--all", action="store_true", dest="fetch_all",
                        help=f"Alle Properties statt Auswahl ({len(DEFAULT_PROPERTIES)} kuratierte)")
    parser.add_argument("-s", "--statements", action="store_true",
                        help="Statement-Details (Qualifiers etc.). Impliziert -a.")
    parser.add_argument("-t", "--type-hierarchy", action="store_true",
                        help="Löst P279-Hierarchie auf für P31, P106, P136 etc.")
    parser.add_argument("--hierarchy-depth", type=int, default=HIERARCHY_MAX_DEPTH, metavar="N",
                        help=f"Max Tiefe (Standard: {HIERARCHY_MAX_DEPTH}). Nur mit -t.")
    parser.add_argument("--no-identifiers", action="store_true",
                        help="Keine externen Identifier-Properties dynamisch laden.")
    parser.add_argument("--no-classify", action="store_true",
                        help="Keine Basisklassen-Klassifizierung.")
    parser.add_argument("--delay", type=float, default=CONFIG['query_delay'], metavar="SEC",
                        help=f"Delay zwischen SPARQL-Queries in Sekunden (Standard: {CONFIG['query_delay']})")
    parser.add_argument("--force", action="store_true", help="Erzwingt Neu-Laden.")
    args = parser.parse_args()

    CONFIG['query_delay'] = max(0.0, args.delay)

    if args.statements:
        args.fetch_all = True
    if args.hierarchy_depth < 1:
        args.hierarchy_depth = 1

    languages = parse_languages(args.languages)
    logger.info(f"Sprachen: {', '.join(languages)}")
    logger.info(f"Query-Delay: {CONFIG['query_delay']}s")

    include_identifiers = not args.no_identifiers and not args.fetch_all
    classify = not args.no_classify

    if args.fetch_all:
        effective_properties = DEFAULT_PROPERTIES
        mode = "ALLE + Statements" if args.statements else "ALLE Properties"
    else:
        effective_properties = get_effective_properties(include_identifiers=include_identifiers)
        id_count = len(effective_properties) - len(DEFAULT_PROPERTIES)
        mode = f"Kuratiert ({len(DEFAULT_PROPERTIES)} + {id_count} ID + {len(DEFAULT_KEEP_PREDICATES)} allg.)"

    if args.type_hierarchy:
        mode += f" + Hierarchie(max {args.hierarchy_depth}, Props: {','.join(sorted(HIERARCHY_RESOLVE_PROPERTIES))})"
    if classify:
        mode += " + Basisklassen"
    logger.info(f"Modus: {mode}")

    output_format = detect_rdf_format(args.output)
    schema_graph, raw_json = load_schema_graph(args.input)

    extra_wikidata_uris: set[str] = set()
    if raw_json is not None:
        schema_graph, extra_wikidata_uris = resolve_about_references(raw_json, schema_graph)

    about_uris = extract_about_uris(schema_graph)
    logger.info(f"{len(about_uris)} 'about'-URIs extrahiert.")

    existing_uri_strs = {str(u) for u in about_uris}
    added_wd_count = 0
    for wd_uri in sorted(extra_wikidata_uris):
        if wd_uri not in existing_uri_strs:
            about_uris.append(URIRef(wd_uri))
            existing_uri_strs.add(wd_uri)
            added_wd_count += 1
    if added_wd_count > 0:
        logger.info(f"{added_wd_count} zusätzliche Wikidata-URIs (Gesamt: {len(about_uris)})")

    result_graph = Graph()
    bind_standard_prefixes(result_graph)
    initial = 0
    if os.path.exists(args.output):
        try:
            result_graph.parse(source=args.output, format=output_format)
            initial = len(result_graph)
            logger.info(f"{initial} bestehende Triples geladen.")
            bind_standard_prefixes(result_graph)
        except Exception as e:
            logger.warning(f"Laden fehlgeschlagen: {e}")

    label_cache = extract_cached_property_ids(result_graph)
    schema_added = merge_graphs(result_graph, schema_graph)
    logger.info(f"{schema_added} Schema.org-Triples (Gesamt: {len(result_graph)})")
    modified = schema_added > 0

    if not about_uris:
        logger.warning("Keine URIs. Nur Schema.org-Daten.")
        if modified or initial == 0:
            save_graph(result_graph, args.output, output_format)
        return

    # Optimierung 5: Property-Labels vorladen
    if not args.fetch_all:
        preload_count = preload_property_labels(
            effective_properties, result_graph, languages, label_cache
        )
        if preload_count > 0:
            modified = True

    try:
        # Hauptdurchlauf
        for i, uri in enumerate(about_uris, 1):
            if fetch_wikidata_statements(
                uri, result_graph, i, len(about_uris),
                languages=languages, label_cache=label_cache,
                effective_properties=effective_properties,
                fetch_all=args.fetch_all, include_statements=args.statements,
                force_update=args.force,
                classify=(classify and not args.fetch_all)
            ):
                modified = True

        # Fallback-Klassifizierung für -a Modus
        if classify and args.fetch_all:
            if classify_entities_batch(about_uris, result_graph, languages):
                modified = True

        # Optimierung 6: Wikipedia-Sitelinks gesammelt
        all_wd_uris = [str(u) for u in about_uris if WD_ENTITY_RE.match(str(u))]
        wiki_count = fetch_all_wikipedia_sitelinks(all_wd_uris, result_graph, languages)
        if wiki_count > 0:
            modified = True

        # Typ-Hierarchie: löst P279-Ketten für P31, P106, P136 etc. auf
        if args.type_hierarchy:
            if resolve_type_hierarchies(
                result_graph, about_uris, languages,
                label_cache, max_depth=args.hierarchy_depth
            ):
                modified = True

    except KeyboardInterrupt:
        logger.warning("Unterbrochen. Speichere...")
    finally:
        if modified or (initial == 0 and len(result_graph) > 0):
            save_graph(result_graph, args.output, output_format)
        else:
            logger.info("Keine Änderungen.")

    logger.info(f"Label-Cache: {len(label_cache)} Properties")


if __name__ == "__main__":
    main()