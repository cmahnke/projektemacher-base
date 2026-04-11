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

# Logging Setup
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

ENRICHMENT = Namespace("urn:enrichment:")

NAMESPACE_PREFIXES = {
    'schema': SCHEMA_HTTP,
    'schemas': SCHEMA_HTTPS,
    'wd': WD,
    'wdt': WDT,
    'wdtn': WDTN,
    'p': P,
    'ps': PS,
    'psv': PSV,
    'psn': PSN,
    'pq': PQ,
    'pqv': PQV,
    'pqn': PQN,
    'pr': PR,
    'prv': PRV,
    'prn': PRN,
    'wdref': WDREF,
    'wdv': WDVALUE,
    'wikibase': WIKIBASE,
    'wdqs': WDQS,
    'prov': PROV,
    'wdno': WDNO,
    'skos': SKOS,
    'owl': OWL,
    'rdfs': RDFS,
    'rdf': RDF,
    'xsd': XSD_NS,
    'enrichment': ENRICHMENT,
}

# ── Kuratierte Property-Whitelist für Default-Modus ──
DEFAULT_PROPERTIES = {
    # Klassifikation & Typ
    'P31', 'P279', 'P361', 'P527', 'P1552', 'P910', 'P1269',
    # Namen, Titel & Bezeichnungen
    'P1448', 'P1449', 'P1559', 'P1705', 'P742', 'P735', 'P734',
    'P1477', 'P2561', 'P1476', 'P1680', 'P528', 'P1813', 'P2562',
    'P138', 'P97',
    # Beschreibung & Zusammenfassung
    'P1343', 'P973', 'P935', 'P373',
    # Bild & Medien
    'P18', 'P154', 'P242', 'P41', 'P94', 'P10', 'P51',
    'P158', 'P948', 'P6802', 'P4291', 'P3451', 'P8517',
    'P1442', 'P109',
    # Geografie
    'P625', 'P17', 'P131', 'P36', 'P150', 'P30', 'P206',
    'P421', 'P47', 'P706', 'P1376', 'P276', 'P291', 'P840',
    'P937', 'P551',
    # Zeit & Geschichte
    'P571', 'P576', 'P580', 'P582', 'P585', 'P569', 'P570',
    'P577', 'P1319', 'P1326',
    # Personen
    'P21', 'P27', 'P19', 'P20', 'P106', 'P39', 'P69', 'P108',
    'P22', 'P25', 'P26', 'P40', 'P3373', 'P184', 'P1066', 'P737',
    'P1412', 'P103', 'P140', 'P172', 'P119', 'P463', 'P241',
    'P410', 'P166', 'P1411', 'P511', 'P1035', 'P1971',
    # Organisationen
    'P112', 'P159', 'P169', 'P488', 'P127', 'P355', 'P749',
    'P452', 'P1128', 'P1454', 'P740',
    # Werke & Kreation
    'P50', 'P57', 'P86', 'P170', 'P175', 'P136', 'P364', 'P495',
    'P123', 'P407', 'P921', 'P144', 'P747', 'P1433', 'P655',
    'P58', 'P162', 'P161', 'P725', 'P676', 'P264', 'P449',
    'P750', 'P272', 'P179', 'P155', 'P156', 'P629', 'P953',
    'P212', 'P957', 'P236', 'P356',
    # Externe Links & wichtige IDs
    'P856', 'P1566', 'P213', 'P214', 'P227', 'P244', 'P268',
    'P269', 'P496', 'P349', 'P1315',
    # Social Media & Web
    'P2013', 'P2003', 'P2002', 'P4033', 'P2397', 'P4264',
    'P8687', 'P1651',
    # Beziehungen
    'P460', 'P1889', 'P2860', 'P3342',
    # Mengen & Statistik
    'P1082', 'P2046', 'P2044', 'P2048', 'P2049', 'P2067',
}

# Non-wdt Prädikate die im Default-Modus immer behalten werden
DEFAULT_KEEP_PREDICATES = {
    str(RDF.type),
    str(RDFS.label),
    str(RDFS.comment),
    'http://schema.org/name',
    'http://schema.org/description',
    'http://schema.org/image',
    'http://schema.org/url',
    'http://schema.org/sameAs',
    'http://schema.org/alternateName',
    'http://schema.org/about',
    'http://schema.org/mainEntity',
    'http://schema.org/subjectOf',
    'http://schema.org/identifier',
    'http://schema.org/inLanguage',
    'http://schema.org/dateCreated',
    'http://schema.org/dateModified',
    'http://schema.org/datePublished',
    'http://schema.org/headline',
    'http://schema.org/abstract',
    'http://schema.org/text',
    'http://schema.org/thumbnailUrl',
    'http://schema.org/contentUrl',
    'http://schema.org/encodingFormat',
    'http://schema.org/license',
    'http://schema.org/copyrightHolder',
    'http://schema.org/author',
    'http://schema.org/creator',
    'https://schema.org/name',
    'https://schema.org/description',
    'https://schema.org/image',
    'https://schema.org/url',
    'https://schema.org/sameAs',
    'https://schema.org/alternateName',
    'https://schema.org/about',
    'https://schema.org/mainEntity',
    'https://schema.org/subjectOf',
    'https://schema.org/identifier',
    'https://schema.org/inLanguage',
    'https://schema.org/dateCreated',
    'https://schema.org/dateModified',
    'https://schema.org/datePublished',
    'https://schema.org/headline',
    'https://schema.org/abstract',
    'https://schema.org/text',
    'https://schema.org/thumbnailUrl',
    'https://schema.org/contentUrl',
    'https://schema.org/encodingFormat',
    'https://schema.org/license',
    'https://schema.org/copyrightHolder',
    'https://schema.org/author',
    'https://schema.org/creator',
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
REQUEST_TIMEOUT = 30
INTER_QUERY_DELAY = 0.5
INCOMING_LIMIT = 1000

DEFAULT_LANGUAGES = ['en', 'de']
ALWAYS_INCLUDE_LANG = 'mul'

FORMAT_MAP = {
    '.ttl': 'turtle',
    '.jsonld': 'json-ld',
    '.json': 'json-ld',
    '.xml': 'xml',
    '.rdf': 'xml',
    '.nt': 'nt',
    '.n3': 'n3',
    '.trig': 'trig',
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
    'http://schema.org/name',
    'http://schema.org/description',
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
    URIRef('http://schema.org/name'),
    URIRef('https://schema.org/name'),
    URIRef('http://schema.org/description'),
    URIRef('https://schema.org/description'),
    URIRef('http://schema.org/alternateName'),
    URIRef('https://schema.org/alternateName'),
    URIRef('http://schema.org/image'),
    URIRef('https://schema.org/image'),
    URIRef('http://schema.org/url'),
    URIRef('https://schema.org/url'),
    URIRef('http://schema.org/sameAs'),
    URIRef('https://schema.org/sameAs'),
    URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
    URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
    URIRef('http://www.w3.org/2004/02/skos/core#altLabel'),
}

STATEMENT_NODE_RE = re.compile(
    r'^http://www\.wikidata\.org/entity/statement/'
)
PROP_STATEMENT_LINK_RE = re.compile(
    r'^http://www\.wikidata\.org/prop/P\d+$'
)
# Pattern für Wikidata Q-Item Entity URIs
WD_ENTITY_RE = re.compile(
    r'^http://www\.wikidata\.org/entity/Q\d+$'
)

FETCHED_MARKER = ENRICHMENT['fetchedFrom']
FETCHED_VALUE = Literal("wikidata")

RDFLIB_TERM_LOGGER = logging.getLogger('rdflib.term')
PROPERTY_ID_RE = re.compile(r'(P\d+)$')
LABEL_BATCH_SIZE = 50


def bind_standard_prefixes(graph: Graph) -> None:
    """Bindet alle bekannten Namespace-Prefixe an den Graph."""
    for prefix, namespace in NAMESPACE_PREFIXES.items():
        graph.bind(prefix, namespace, override=True)


def build_whitelist_sparql(uri: str, languages: list[str]) -> str:
    """Baut SPARQL-Abfrage für Whitelist-Properties (Default-Modus)."""
    lang_filter = build_language_filter(languages)
    wdt_values = " ".join(f"wdt:{pid}" for pid in sorted(DEFAULT_PROPERTIES))
    other_preds = " ".join(f"<{p}>" for p in sorted(DEFAULT_KEEP_PREDICATES))

    return f"""
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT ?p ?o WHERE {{
        {{
            VALUES ?p {{ {wdt_values} }}
            <{uri}> ?p ?o .
        }} UNION {{
            VALUES ?p {{ {other_preds} }}
            <{uri}> ?p ?o .
        }}
        {lang_filter}
    }}
    """


def build_incoming_sparql(
    uri: str,
    fetch_all: bool,
    include_statements: bool
) -> str:
    """
    Baut SPARQL-Abfrage für eingehende Triples.

    Default-Modus: Nur Q-Entities als Subject, nur wdt: Prädikate
    -a Modus: Alle Subjects, filtert Statement-Nodes (ohne -s)
    -s Modus: Alles
    """
    if include_statements:
        # Alles
        return (
            f"SELECT ?s ?p WHERE {{ ?s ?p <{uri}> }} "
            f"LIMIT {INCOMING_LIMIT}"
        )
    elif fetch_all:
        # Alle außer Statement-Nodes als Subject
        return f"""
        SELECT ?s ?p WHERE {{
            ?s ?p <{uri}> .
            FILTER(
                !STRSTARTS(STR(?s), "http://www.wikidata.org/entity/statement/")
                && !REGEX(STR(?p), "^http://www.wikidata.org/prop/P[0-9]+$")
            )
        }} LIMIT {INCOMING_LIMIT}
        """
    else:
        # Default: nur Q-Entities als Subject, nur wdt: Prädikate
        return f"""
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        SELECT ?s ?p WHERE {{
            ?s ?p <{uri}> .
            FILTER(
                STRSTARTS(STR(?s), "http://www.wikidata.org/entity/Q")
                && STRSTARTS(STR(?p), "http://www.wikidata.org/prop/direct/")
            )
        }} LIMIT {INCOMING_LIMIT}
        """


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


def safe_literal(
    value: str, datatype: str | None = None, lang: str | None = None
) -> Literal:
    if datatype and not is_valid_python_date(value, datatype):
        logger.debug(f"Datumswert außerhalb Python-Grenzen: '{value}'")
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
        logger.info(
            f"Label-Cache: {len(cached)} Property-Labels aus Graph geladen"
        )
    return cached


def parse_sparql_binding_to_rdf(
    binding: dict,
    languages: list[str] | None = None,
    predicate_str: str | None = None
) -> URIRef | Literal | None:
    if binding['type'] == 'uri':
        return URIRef(binding['value'])
    elif binding['type'] in ('literal', 'typed-literal'):
        o_lang = binding.get('xml:lang')
        o_datatype = binding.get('datatype')
        o_value = binding['value']
        if languages and predicate_str:
            if not is_literal_in_allowed_languages(
                o_value, o_lang, o_datatype, predicate_str, languages
            ):
                return None
        return safe_literal(value=o_value, datatype=o_datatype, lang=o_lang)
    return None


def fetch_property_labels(
    property_ids: set[str], target_graph: Graph,
    languages: list[str], label_cache: set[str]
) -> int:
    if not property_ids:
        return 0
    uncached = property_ids - label_cache
    if not uncached:
        return 0

    logger.info(
        f"  Rufe Labels für {len(uncached)} neue Properties ab "
        f"({len(property_ids) - len(uncached)} im Cache)"
    )

    all_uncached = sorted(uncached)
    total_added = 0

    for batch_start in range(0, len(all_uncached), LABEL_BATCH_SIZE):
        batch = all_uncached[batch_start:batch_start + LABEL_BATCH_SIZE]
        values_clause = " ".join(f"wd:{pid}" for pid in batch)
        lang_filter = " || ".join(
            f'LANG(?label) = "{l}"' for l in languages
        )

        query = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?prop ?label WHERE {{
            VALUES ?prop {{ {values_clause} }}
            ?prop rdfs:label ?label .
            FILTER({lang_filter})
        }}
        """

        data = sparql_query_with_retry(query)
        if data is None:
            logger.error("  Property-Label-Batch fehlgeschlagen")
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
            time.sleep(INTER_QUERY_DELAY)

    if total_added > 0:
        logger.info(f"  → {total_added} Property-Label-Triples hinzugefügt")
    return total_added


def fetch_statement_details(
    statement_uris: set[str], target_graph: Graph,
    languages: list[str], label_cache: set[str]
) -> int:
    if not statement_uris:
        return 0

    logger.info(
        f"  Rufe Details für {len(statement_uris)} Statement-Nodes ab..."
    )

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
            VALUES ?stmt {{ {vc} }}
            ?stmt ?p ?o .
            {lang_filter}
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
        time.sleep(INTER_QUERY_DELAY)

    if collected_pids:
        total_added += fetch_property_labels(
            collected_pids, target_graph, languages, label_cache
        )

    if total_added > 0:
        logger.info(f"  → {total_added} Statement-Detail-Triples hinzugefügt")
    return total_added


def is_already_fetched(uri_ref: URIRef, graph: Graph) -> bool:
    return (uri_ref, FETCHED_MARKER, FETCHED_VALUE) in graph


def mark_as_fetched(uri_ref: URIRef, graph: Graph) -> None:
    graph.add((uri_ref, FETCHED_MARKER, FETCHED_VALUE))


def build_language_filter(languages: list[str]) -> str:
    lc = " || ".join(f'LANG(?o) = "{l}"' for l in languages)
    return f"FILTER(!isLiteral(?o) || LANG(?o) = \"\" || {lc})"


def parse_languages(lang_string: str) -> list[str]:
    languages = [l.strip().lower() for l in lang_string.split(',') if l.strip()]
    if not languages:
        languages = DEFAULT_LANGUAGES.copy()
    if ALWAYS_INCLUDE_LANG not in languages:
        languages.append(ALWAYS_INCLUDE_LANG)
    return languages


def is_literal_in_allowed_languages(
    value: str, lang: str | None, datatype: str | None,
    predicate: str, allowed: list[str]
) -> bool:
    if not lang or lang == '':
        return True
    if predicate in LANG_SENSITIVE_PROPERTIES:
        return lang in allowed
    return True


def should_include_outgoing_triple(
    predicate_str: str,
    object_str: str | None,
    include_statements: bool
) -> bool:
    """Filtert ausgehende Triples: Statement-Links ohne -s."""
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


def sparql_query_with_retry(query: str) -> dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(
                SPARQL_URL, params={'query': query},
                headers=SPARQL_HEADERS, timeout=REQUEST_TIMEOUT
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


def fetch_wikidata_statements(
    uri: str, target_graph: Graph,
    current: int, total: int,
    languages: list[str], label_cache: set[str],
    fetch_all: bool = False, include_statements: bool = False,
    force_update: bool = False
) -> bool:
    if "wikidata.org/entity/" not in str(uri):
        return False

    uri_ref = URIRef(uri)

    if not force_update and is_already_fetched(uri_ref, target_graph):
        logger.info(f"[{current}/{total}] Überspringe {uri}: bereits abgerufen.")
        return False

    logger.info(f"[{current}/{total}] Hole Wikidata-Statements für: {uri}")

    # ── Ausgehende Query ──
    if fetch_all:
        lf = build_language_filter(languages)
        out_query = f"SELECT ?p ?o WHERE {{ <{uri}> ?p ?o . {lf} }}"
    else:
        out_query = build_whitelist_sparql(uri, languages)

    # ── Eingehende Query (mit Filter je nach Modus) ──
    in_query = build_incoming_sparql(uri, fetch_all, include_statements)

    wikidata_graph = Graph()
    collected_pids = set()
    collected_stmts = set()
    skipped = 0

    # Ausgehend
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

            # Im -a Modus: Statement-Links filtern
            if fetch_all and not should_include_outgoing_triple(
                p_str, o_str, include_statements
            ):
                skipped += 1
                continue

            if (include_statements and isinstance(o, URIRef)
                    and is_statement_node(str(o))):
                collected_stmts.add(str(o))

            wikidata_graph.add((uri_ref, p, o))

    time.sleep(INTER_QUERY_DELAY)

    # Eingehend (bereits serverseitig gefiltert)
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

    time.sleep(INTER_QUERY_DELAY)

    # Override
    wd_preds = set(wikidata_graph.predicates(subject=uri_ref))
    override_preds = wd_preds & WIKIDATA_OVERRIDES_PROPERTIES
    removed = 0
    for pred in override_preds:
        for t in list(target_graph.triples((uri_ref, pred, None))):
            target_graph.remove(t)
            removed += 1
    if removed:
        logger.info(f"  → {removed} Override-Triples entfernt")

    # Einfügen
    added = 0
    for t in wikidata_graph:
        if t not in target_graph:
            target_graph.add(t)
            added += 1

    # Statements
    stmt_count = 0
    if include_statements and collected_stmts:
        stmt_count = fetch_statement_details(
            collected_stmts, target_graph, languages, label_cache
        )

    # Labels
    label_count = 0
    if collected_pids:
        label_count = fetch_property_labels(
            collected_pids, target_graph, languages, label_cache
        )

    mark_as_fetched(uri_ref, target_graph)

    changed = (removed + added + label_count + stmt_count) > 0
    parts = [f"{added} hinzugefügt", f"{removed} ersetzt"]
    if label_count:
        parts.append(f"{label_count} Property-Labels")
    if stmt_count:
        parts.append(f"{stmt_count} Statement-Details")
    if skipped:
        parts.append(f"{skipped} gefiltert")
    logger.info(f"  → {', '.join(parts)} für {uri}")

    return changed


def load_schema_graph(input_source: str) -> Graph:
    g = Graph()
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
        g.parse(data=content, format="json-ld")
        logger.info(f"{len(g)} Triples aus Eingabe geparst.")
    except requests.exceptions.RequestException as e:
        logger.error(f"URL-Fehler: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Parse-Fehler: {e}")
        sys.exit(1)
    return g


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


def main():
    parser = argparse.ArgumentParser(
        description="Schema.org JSON-LD → Wikidata-Anreicherung"
    )
    parser.add_argument("input", help="URL oder Pfad zur JSON-LD Datei")
    parser.add_argument(
        "-o", "--output", default="enriched_entities.ttl",
        help="Ausgabe-RDF-Datei (Standard: enriched_entities.ttl)"
    )
    parser.add_argument(
        "-l", "--languages", default=",".join(DEFAULT_LANGUAGES),
        help=f"Sprachen (Standard: {','.join(DEFAULT_LANGUAGES)})"
    )
    parser.add_argument(
        "-a", "--all", action="store_true", dest="fetch_all",
        help=f"Alle Properties statt Auswahl ({len(DEFAULT_PROPERTIES)} wdt:)"
    )
    parser.add_argument(
        "-s", "--statements", action="store_true",
        help="Statement-Details (Qualifiers etc.). Impliziert -a."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Erzwingt Neu-Laden."
    )
    args = parser.parse_args()

    if args.statements:
        args.fetch_all = True

    languages = parse_languages(args.languages)
    logger.info(f"Sprachen: {', '.join(languages)}")

    if args.fetch_all:
        mode = "ALLE + Statements" if args.statements else "ALLE Properties"
    else:
        mode = (
            f"Kuratiert ({len(DEFAULT_PROPERTIES)} wdt: + "
            f"{len(DEFAULT_KEEP_PREDICATES)} allgemeine)"
        )
    logger.info(f"Modus: {mode}")

    output_format = detect_rdf_format(args.output)
    schema_graph = load_schema_graph(args.input)
    about_uris = extract_about_uris(schema_graph)
    logger.info(f"{len(about_uris)} 'about'-URIs extrahiert.")

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

    try:
        for i, uri in enumerate(about_uris, 1):
            if fetch_wikidata_statements(
                uri, result_graph, i, len(about_uris),
                languages=languages, label_cache=label_cache,
                fetch_all=args.fetch_all,
                include_statements=args.statements,
                force_update=args.force
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