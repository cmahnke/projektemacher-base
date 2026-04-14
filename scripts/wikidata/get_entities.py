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
    'P856', 'P1566', 'P213', 'P214', 'P227', 'P244', 'P268',
    'P269', 'P496', 'P349', 'P1315',
    'P2013', 'P2003', 'P2002', 'P4033', 'P2397', 'P4264',
    'P8687', 'P1651',
    'P460', 'P1889', 'P2860', 'P3342',
    'P1082', 'P2046', 'P2044', 'P2048', 'P2049', 'P2067',
}

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
REQUEST_TIMEOUT = 60
INTER_QUERY_DELAY = 0.5
INCOMING_LIMIT = 1000

# ── Indirect link discovery settings ──
INDIRECT_MAX_HOPS = 2
INDIRECT_RESULTS_LIMIT = 5000
INDIRECT_BATCH_SIZE = 50  # Entities per VALUES batch

# ── Type hierarchy settings ──
HIERARCHY_MAX_DEPTH = 10
HIERARCHY_BATCH_SIZE = 50

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
WD_ENTITY_RE = re.compile(
    r'^http://www\.wikidata\.org/entity/Q\d+$'
)

FETCHED_MARKER = ENRICHMENT['fetchedFrom']
FETCHED_VALUE = Literal("wikidata")

INDIRECT_MARKER = ENRICHMENT['indirectLink']
HIERARCHY_MARKER = ENRICHMENT['hierarchyNode']

RDFLIB_TERM_LOGGER = logging.getLogger('rdflib.term')
PROPERTY_ID_RE = re.compile(r'(P\d+)$')
LABEL_BATCH_SIZE = 50
WIKIPEDIA_SITELINK_BATCH_SIZE = 50

WDT_P31 = URIRef("http://www.wikidata.org/prop/direct/P31")
WDT_P279 = URIRef("http://www.wikidata.org/prop/direct/P279")

# ── JSON-LD about-Referenz-Auflösung: Einstellungen ──
ABOUT_FETCH_TIMEOUT = 30
ABOUT_FETCH_HEADERS = {
    'User-Agent': 'BlogEntityExtractor/1.0 (https://github.com/cmahnke)',
    'Accept': 'application/ld+json, application/json;q=0.9, */*;q=0.1'
}


def build_wikipedia_sitelinks_query(
    entity_uris: list[str], languages: list[str]
) -> str:
    values_entities = " ".join(f"<{u}>" for u in entity_uris)
    site_filters = " || ".join(
        f'?site = <https://{lang}.wikipedia.org/>' for lang in languages
        if lang != 'mul'
    )
    if not site_filters:
        return ""

    return f"""
    PREFIX schema: <http://schema.org/>
    SELECT ?entity ?article ?siteLang WHERE {{
        VALUES ?entity {{ {values_entities} }}
        ?article schema:about ?entity ;
                 schema:isPartOf ?site ;
                 schema:inLanguage ?siteLang .
        FILTER({site_filters})
    }}
    """


def fetch_wikipedia_sitelinks(
    entity_uris: list[str],
    target_graph: Graph,
    languages: list[str]
) -> int:
    if not entity_uris:
        return 0

    wiki_languages = [l for l in languages if l != 'mul']
    if not wiki_languages:
        return 0

    needed = []
    for uri_str in entity_uris:
        uri_ref = URIRef(uri_str)
        has_wiki = False
        for obj in target_graph.objects(uri_ref, SCHEMA_HTTP['sameAs']):
            if 'wikipedia.org' in str(obj):
                has_wiki = True
                break
        if not has_wiki:
            for obj in target_graph.objects(uri_ref, SCHEMA_HTTPS['sameAs']):
                if 'wikipedia.org' in str(obj):
                    has_wiki = True
                    break
        if not has_wiki:
            needed.append(uri_str)

    if not needed:
        return 0

    logger.info(
        f"  Rufe Wikipedia-Sitelinks für {len(needed)} Entities ab "
        f"(Sprachen: {', '.join(wiki_languages)})..."
    )

    total_added = 0

    for batch_start in range(0, len(needed), WIKIPEDIA_SITELINK_BATCH_SIZE):
        batch = needed[batch_start:batch_start + WIKIPEDIA_SITELINK_BATCH_SIZE]
        query = build_wikipedia_sitelinks_query(batch, languages)
        if not query:
            continue

        data = sparql_query_with_retry(query)
        if data is None:
            logger.error("  Wikipedia-Sitelink-Batch fehlgeschlagen")
            continue

        added = 0
        for r in data.get('results', {}).get('bindings', []):
            entity_ref = URIRef(r['entity']['value'])
            article_url = URIRef(r['article']['value'])

            t = (entity_ref, SCHEMA_HTTP['sameAs'], article_url)
            if t not in target_graph:
                target_graph.add(t)
                added += 1

        total_added += added
        time.sleep(INTER_QUERY_DELAY)

    if total_added > 0:
        logger.info(f"  → {total_added} Wikipedia-Sitelink-Triples hinzugefügt")
    return total_added


def bind_standard_prefixes(graph: Graph) -> None:
    for prefix, namespace in NAMESPACE_PREFIXES.items():
        graph.bind(prefix, namespace, override=True)


def build_whitelist_sparql(uri: str, languages: list[str]) -> str:
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
    uri: str, fetch_all: bool, include_statements: bool
) -> str:
    if include_statements:
        return (
            f"SELECT ?s ?p WHERE {{ ?s ?p <{uri}> }} "
            f"LIMIT {INCOMING_LIMIT}"
        )
    elif fetch_all:
        return f"""
        SELECT ?s ?p WHERE {{
            ?s ?p <{uri}> .
            FILTER(
                !STRSTARTS(STR(?s),
                    "http://www.wikidata.org/entity/statement/")
                && !REGEX(STR(?p),
                    "^http://www.wikidata.org/prop/P[0-9]+$")
            )
        }} LIMIT {INCOMING_LIMIT}
        """
    else:
        return f"""
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        SELECT ?s ?p WHERE {{
            ?s ?p <{uri}> .
            FILTER(
                STRSTARTS(STR(?s), "http://www.wikidata.org/entity/Q")
                && STRSTARTS(STR(?p),
                    "http://www.wikidata.org/prop/direct/")
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
                URIRef(
                    f"http://www.wikidata.org/prop/direct-normalized/{pid}"
                ),
                URIRef(f"http://www.wikidata.org/prop/statement/{pid}"),
                URIRef(
                    f"http://www.wikidata.org/prop/statement/value/{pid}"
                ),
                URIRef(f"http://www.wikidata.org/prop/qualifier/{pid}"),
                URIRef(
                    f"http://www.wikidata.org/prop/qualifier/value/{pid}"
                ),
                URIRef(f"http://www.wikidata.org/prop/reference/{pid}"),
                URIRef(
                    f"http://www.wikidata.org/prop/reference/value/{pid}"
                ),
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
        logger.info(
            f"  → {total_added} Property-Label-Triples hinzugefügt"
        )
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
        logger.info(
            f"  → {total_added} Statement-Detail-Triples hinzugefügt"
        )
    return total_added


def is_already_fetched(uri_ref: URIRef, graph: Graph) -> bool:
    return (uri_ref, FETCHED_MARKER, FETCHED_VALUE) in graph


def mark_as_fetched(uri_ref: URIRef, graph: Graph) -> None:
    graph.add((uri_ref, FETCHED_MARKER, FETCHED_VALUE))


def build_language_filter(languages: list[str]) -> str:
    lc = " || ".join(f'LANG(?o) = "{l}"' for l in languages)
    return f"FILTER(!isLiteral(?o) || LANG(?o) = \"\" || {lc})"


def parse_languages(lang_string: str) -> list[str]:
    languages = [
        l.strip().lower() for l in lang_string.split(',') if l.strip()
    ]
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
        logger.warning(
            f"Unbekannte Endung '{ext}'. Fallback: turtle."
        )
        return 'turtle'
    return fmt


def sparql_query_with_retry(query: str) -> dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                SPARQL_URL,
                data={'query': query},
                headers={
                    **SPARQL_HEADERS,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=REQUEST_TIMEOUT
            )
            if resp.status_code == 429:
                ra = resp.headers.get("Retry-After")
                try:
                    w = int(ra) + 1 if ra else None
                except (ValueError, TypeError):
                    w = None
                w = w or (RETRY_BASE_WAIT ** attempt) + 5
                logger.warning(
                    f"Rate limit. Warte {w}s ({attempt+1}/{MAX_RETRIES})"
                )
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
    logger.error(
        f"SPARQL nach {MAX_RETRIES} Versuchen fehlgeschlagen."
    )
    return None


# ─────────────────────────────────────────────────────────────────────
# Type hierarchy resolution (P31 → P279 chain)
# ─────────────────────────────────────────────────────────────────────

def collect_instance_of_types(
    graph: Graph, entity_uris: list[URIRef]
) -> set[str]:
    type_uris = set()
    for entity_uri in entity_uris:
        for obj in graph.objects(entity_uri, WDT_P31):
            obj_str = str(obj)
            if WD_ENTITY_RE.match(obj_str):
                type_uris.add(obj_str)
    return type_uris


def fetch_superclasses_batch(
    class_uris: set[str]
) -> dict[str, list[str]]:
    if not class_uris:
        return {}

    all_uris = sorted(class_uris)
    result: dict[str, list[str]] = {}

    for batch_start in range(0, len(all_uris), HIERARCHY_BATCH_SIZE):
        batch = all_uris[
            batch_start:batch_start + HIERARCHY_BATCH_SIZE
        ]
        values_clause = " ".join(f"<{u}>" for u in batch)

        query = f"""
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        SELECT ?child ?parent WHERE {{
            VALUES ?child {{ {values_clause} }}
            ?child wdt:P279 ?parent .
            FILTER(STRSTARTS(
                STR(?parent),
                "http://www.wikidata.org/entity/Q"
            ))
        }}
        """
        data = sparql_query_with_retry(query)
        if data is None:
            continue

        for r in data.get('results', {}).get('bindings', []):
            child = r['child']['value']
            parent = r['parent']['value']
            result.setdefault(child, []).append(parent)

        time.sleep(INTER_QUERY_DELAY)

    return result


def resolve_type_hierarchies(
    target_graph: Graph,
    entity_uris: list[URIRef],
    languages: list[str],
    label_cache: set[str],
    max_depth: int = HIERARCHY_MAX_DEPTH
) -> bool:
    type_uris = collect_instance_of_types(target_graph, entity_uris)
    if not type_uris:
        logger.info(
            "Typ-Hierarchie: Keine wdt:P31-Typen gefunden – überspringe."
        )
        return False

    logger.info(
        f"\n{'='*60}\n"
        f"Typ-Hierarchie: Löse {len(type_uris)} instance-of Typen auf "
        f"(max {max_depth} Ebenen)\n"
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

        logger.info(
            f"  Ebene {depth}: Prüfe {len(to_query)} Klassen "
            f"auf Oberklassen (P279)..."
        )

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

                marker = (
                    parent_ref, HIERARCHY_MARKER, Literal(True)
                )
                if marker not in target_graph:
                    target_graph.add(marker)

                if parent_uri not in visited:
                    next_level.add(parent_uri)

        for uri_str in to_query:
            if uri_str not in parent_map:
                root_ref = URIRef(uri_str)
                all_hierarchy_entities.add(uri_str)
                marker = (
                    root_ref, HIERARCHY_MARKER, Literal(True)
                )
                if marker not in target_graph:
                    target_graph.add(marker)

        total_triples_added += added_this_level
        if added_this_level > 0:
            logger.info(
                f"    → {added_this_level} P279-Triples, "
                f"{len(next_level)} neue Oberklassen"
            )
        else:
            logger.info(f"    → Keine neuen P279-Triples")

        current_level = next_level

    if depth >= max_depth and current_level:
        logger.warning(
            f"  Tiefe {max_depth} erreicht, "
            f"{len(current_level)} nicht weiter aufgelöst"
        )

    if all_hierarchy_entities:
        label_count = fetch_entity_labels(
            all_hierarchy_entities, target_graph, languages
        )
        total_triples_added += label_count

    if collected_pids:
        plabel_count = fetch_property_labels(
            collected_pids, target_graph, languages, label_cache
        )
        total_triples_added += plabel_count

    logger.info(
        f"\nTyp-Hierarchie: {len(all_hierarchy_entities)} Klassen, "
        f"{total_triples_added} Triples, {depth} Ebenen"
    )

    return total_triples_added > 0


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
        logger.info(
            f"[{current}/{total}] Überspringe {uri}: bereits abgerufen."
        )
        return False

    logger.info(
        f"[{current}/{total}] Hole Wikidata-Statements für: {uri}"
    )

    if fetch_all:
        lf = build_language_filter(languages)
        out_query = (
            f"SELECT ?p ?o WHERE {{ <{uri}> ?p ?o . {lf} }}"
        )
    else:
        out_query = build_whitelist_sparql(uri, languages)

    in_query = build_incoming_sparql(
        uri, fetch_all, include_statements
    )

    wikidata_graph = Graph()
    collected_pids = set()
    collected_stmts = set()
    skipped = 0

    data = sparql_query_with_retry(out_query)
    if data is None:
        logger.error(
            f"Ausgehende Abfrage fehlgeschlagen für {uri}"
        )
    else:
        for r in data.get('results', {}).get('bindings', []):
            p_str = r['p']['value']
            p = URIRef(p_str)
            pid = extract_property_id(p_str)
            if pid:
                collected_pids.add(pid)

            o = parse_sparql_binding_to_rdf(
                r['o'], languages, p_str
            )
            if o is None:
                continue

            o_str = str(o) if isinstance(o, URIRef) else None

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

    data = sparql_query_with_retry(in_query)
    if data is None:
        logger.error(
            f"Eingehende Abfrage fehlgeschlagen für {uri}"
        )
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

    wd_preds = set(wikidata_graph.predicates(subject=uri_ref))
    override_preds = wd_preds & WIKIDATA_OVERRIDES_PROPERTIES
    removed = 0
    for pred in override_preds:
        for t in list(
            target_graph.triples((uri_ref, pred, None))
        ):
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
        stmt_count = fetch_statement_details(
            collected_stmts, target_graph, languages, label_cache
        )

    label_count = 0
    if collected_pids:
        label_count = fetch_property_labels(
            collected_pids, target_graph, languages, label_cache
        )

    wiki_count = fetch_wikipedia_sitelinks(
        [str(uri)], target_graph, languages
    )

    mark_as_fetched(uri_ref, target_graph)

    changed = (
        removed + added + label_count + stmt_count + wiki_count
    ) > 0
    parts = [f"{added} hinzugefügt", f"{removed} ersetzt"]
    if label_count:
        parts.append(f"{label_count} Property-Labels")
    if stmt_count:
        parts.append(f"{stmt_count} Statement-Details")
    if wiki_count:
        parts.append(f"{wiki_count} Wikipedia-Links")
    if skipped:
        parts.append(f"{skipped} gefiltert")
    logger.info(f"  → {', '.join(parts)} für {uri}")

    return changed


# ─────────────────────────────────────────────────────────────────────
# JSON-LD about-Referenz-Auflösung: @id-only about-Objekte abrufen
# ─────────────────────────────────────────────────────────────────────

def _is_id_only_about(about_obj: dict | str) -> str | None:
    """
    Prüft ob ein about-Objekt nur eine @id enthält (kein 'name' o.ä.).
    Gibt die @id-URL zurück falls ja, sonst None.

    Erkennt folgende Muster:
      - {"@id": "https://example.org/thing"}                → id-only
      - {"@id": "https://...", "@type": "Thing"}            → id-only
      - {"@id": "https://...", "name": "Foo"}               → NICHT id-only
      - "https://example.org/thing"                         → id-only (string)
    """
    if isinstance(about_obj, str):
        # Einfache String-Referenz = nur eine ID
        if about_obj.startswith(('http://', 'https://')):
            return about_obj
        return None

    if not isinstance(about_obj, dict):
        return None

    id_value = about_obj.get('@id')
    if not id_value:
        return None

    # Prüfe ob außer @id und @type noch andere Schlüssel vorhanden sind
    meaningful_keys = {
        k for k in about_obj.keys()
        if k not in ('@id', '@type')
    }

    if meaningful_keys:
        # Hat zusätzliche Daten wie 'name', 'description' etc.
        return None

    # Nur @id (und optional @type) vorhanden
    if id_value.startswith(('http://', 'https://')):
        return id_value

    return None


def _extract_jsonld_from_response(
    response_text: str, url: str
) -> list[dict]:
    """
    Versucht JSON-LD aus einer HTTP-Antwort zu extrahieren.
    Unterstützt:
      - Direkte JSON-LD Antwort (Objekt oder Array)
      - HTML mit eingebettetem <script type="application/ld+json">
    Gibt eine Liste von JSON-LD-Objekten zurück.
    """
    results = []

    # Versuch 1: Direktes JSON parsen
    try:
        data = json.loads(response_text)
        if isinstance(data, dict):
            results.append(data)
            return results
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    results.append(item)
            if results:
                return results
    except (json.JSONDecodeError, ValueError):
        pass

    # Versuch 2: JSON-LD aus HTML-Script-Tags extrahieren
    script_pattern = re.compile(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>'
        r'(.*?)</script>',
        re.DOTALL | re.IGNORECASE
    )
    matches = script_pattern.findall(response_text)

    for match in matches:
        try:
            data = json.loads(match.strip())
            if isinstance(data, dict):
                results.append(data)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        results.append(item)
        except (json.JSONDecodeError, ValueError) as e:
            logger.debug(
                f"  JSON-LD Script-Block konnte nicht geparst werden "
                f"von {url}: {e}"
            )

    return results


def _fetch_and_parse_jsonld_url(url: str) -> Graph | None:
    """
    Ruft eine URL ab und versucht JSON-LD daraus zu parsen.
    Gibt einen RDF-Graph zurück oder None bei Fehler.
    """
    logger.debug(f"  Versuche JSON-LD abzurufen von: {url}")

    try:
        resp = requests.get(
            url,
            headers=ABOUT_FETCH_HEADERS,
            timeout=ABOUT_FETCH_TIMEOUT,
            allow_redirects=True
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        logger.debug(f"  Timeout beim Abrufen von {url}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.debug(f"  Verbindungsfehler für {url}: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.debug(f"  HTTP-Fehler für {url}: {e}")
        return None
    except Exception as e:
        logger.debug(f"  Fehler beim Abrufen von {url}: {e}")
        return None

    content_type = resp.headers.get('Content-Type', '').lower()
    response_text = resp.text

    # JSON-LD Objekte aus Antwort extrahieren
    jsonld_objects = _extract_jsonld_from_response(
        response_text, url
    )

    if not jsonld_objects:
        logger.debug(
            f"  Kein JSON-LD in Antwort von {url} gefunden "
            f"(Content-Type: {content_type})"
        )
        return None

    # Alle gefundenen JSON-LD Objekte in einen Graph parsen
    combined_graph = Graph()

    for jsonld_obj in jsonld_objects:
        try:
            jsonld_str = json.dumps(jsonld_obj)
            temp_graph = Graph()
            temp_graph.parse(data=jsonld_str, format='json-ld')
            for triple in temp_graph:
                combined_graph.add(triple)
        except Exception as e:
            logger.debug(
                f"  JSON-LD Objekt von {url} konnte nicht als RDF "
                f"geparst werden: {e}"
            )

    if len(combined_graph) == 0:
        logger.debug(
            f"  JSON-LD von {url} ergab keine RDF-Triples"
        )
        return None

    return combined_graph


def resolve_id_only_abouts(
    raw_json: dict | list, target_graph: Graph
) -> int:
    """
    Durchsucht die rohe JSON-LD Struktur nach about-Objekten die nur
    eine @id enthalten (kein 'name' etc.), ruft deren URL ab, parst
    das Ergebnis als JSON-LD und fügt die Triples dem Graph hinzu.

    Gibt die Anzahl der hinzugefügten Triples zurück.

    Unterstützt sowohl einzelne JSON-LD Objekte als auch @graph-Arrays
    und verschachtelte Strukturen.
    """
    # Sammle alle about-Referenzen die nur @id haben
    id_only_urls: set[str] = set()
    _collect_id_only_abouts(raw_json, id_only_urls)

    if not id_only_urls:
        return 0

    logger.info(
        f"Gefunden: {len(id_only_urls)} about-Referenzen mit nur @id "
        f"(ohne name) – versuche aufzulösen..."
    )

    total_added = 0
    resolved = 0
    failed = 0

    for url in sorted(id_only_urls):
        logger.info(f"  Löse auf: {url}")

        fetched_graph = _fetch_and_parse_jsonld_url(url)

        if fetched_graph is None:
            logger.warning(f"  ✗ Konnte kein JSON-LD laden von: {url}")
            failed += 1
            continue

        # Triples zum Zielgraph hinzufügen
        added = 0
        for triple in fetched_graph:
            if triple not in target_graph:
                target_graph.add(triple)
                added += 1

        if added > 0:
            logger.info(
                f"  ✓ {added} Triples hinzugefügt von: {url} "
                f"({len(fetched_graph)} gesamt in Quelle)"
            )
            total_added += added
            resolved += 1
        else:
            logger.info(
                f"  ○ Alle {len(fetched_graph)} Triples bereits "
                f"vorhanden von: {url}"
            )
            resolved += 1

        # Kurze Pause zwischen Anfragen
        time.sleep(INTER_QUERY_DELAY)

    logger.info(
        f"About-Auflösung: {resolved} aufgelöst, {failed} fehlgeschlagen, "
        f"{total_added} Triples hinzugefügt"
    )

    return total_added


def _collect_id_only_abouts(
    obj: dict | list | str, collected: set[str]
) -> None:
    """
    Rekursiv JSON-LD Struktur durchsuchen und @id-only about-Objekte
    sammeln.
    """
    if isinstance(obj, list):
        for item in obj:
            _collect_id_only_abouts(item, collected)
        return

    if isinstance(obj, str):
        return

    if not isinstance(obj, dict):
        return

    # @graph Container durchsuchen
    if '@graph' in obj:
        _collect_id_only_abouts(obj['@graph'], collected)

    # Prüfe 'about'-Felder (verschiedene Schreibweisen)
    for about_key in ('about', 'schema:about',
                      'http://schema.org/about',
                      'https://schema.org/about'):
        if about_key in obj:
            about_val = obj[about_key]
            if isinstance(about_val, list):
                for item in about_val:
                    url = _is_id_only_about(item)
                    if url:
                        collected.add(url)
                    # Rekursiv in verschachtelte about-Objekte
                    if isinstance(item, dict):
                        _collect_id_only_abouts(item, collected)
            else:
                url = _is_id_only_about(about_val)
                if url:
                    collected.add(url)
                if isinstance(about_val, dict):
                    _collect_id_only_abouts(about_val, collected)

    # Rekursiv alle Werte durchsuchen (für verschachtelte Objekte
    # wie blogPost → about)
    for key, value in obj.items():
        if key.startswith('@'):
            # @context, @id, @type etc. überspringen
            continue
        if key in ('about', 'schema:about',
                   'http://schema.org/about',
                   'https://schema.org/about'):
            # Schon oben behandelt
            continue
        if isinstance(value, (dict, list)):
            _collect_id_only_abouts(value, collected)


def load_schema_graph(input_source: str) -> Graph:
    """
    Lädt JSON-LD von URL oder Datei.
    Prüft about-Objekte die nur @id haben und versucht deren URL
    abzurufen und als JSON-LD dem Graph hinzuzufügen.
    """
    g = Graph()
    raw_json = None

    try:
        if input_source.startswith(('http://', 'https://')):
            logger.info(f"Lade JSON-LD von URL: {input_source}")
            resp = requests.get(
                input_source, timeout=REQUEST_TIMEOUT
            )
            resp.raise_for_status()
            content = resp.text
        else:
            logger.info(f"Lade JSON-LD von Datei: {input_source}")
            if not os.path.exists(input_source):
                logger.error(f"Nicht gefunden: {input_source}")
                sys.exit(1)
            with open(input_source, 'r', encoding='utf-8') as f:
                content = f.read()

        # Rohes JSON parsen für about-Analyse
        try:
            raw_json = json.loads(content)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(
                f"JSON-Voranalyse fehlgeschlagen (about-Auflösung "
                f"wird übersprungen): {e}"
            )

        # Normales RDF-Parsing
        g.parse(data=content, format="json-ld")
        logger.info(f"{len(g)} Triples aus Eingabe geparst.")

    except requests.exceptions.RequestException as e:
        logger.error(f"URL-Fehler: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Parse-Fehler: {e}")
        sys.exit(1)

    # ── @id-only about-Objekte auflösen ──
    if raw_json is not None:
        added = resolve_id_only_abouts(raw_json, g)
        if added > 0:
            logger.info(
                f"Nach about-Auflösung: {len(g)} Triples gesamt"
            )

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
        logger.info(
            f"Gespeichert: {path} ({len(graph)} Triples, {fmt})"
        )
        return True
    except Exception as e:
        logger.error(f"Speicherfehler: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────
# Indirect link discovery – batched approach
# ─────────────────────────────────────────────────────────────────────

def collect_wikidata_entity_uris(
    about_uris: list[URIRef]
) -> list[str]:
    return sorted(set(
        str(u) for u in about_uris
        if WD_ENTITY_RE.match(str(u))
    ))


def fetch_entity_labels(
    entity_uris: set[str],
    target_graph: Graph,
    languages: list[str]
) -> int:
    if not entity_uris:
        return 0

    needed = set()
    for uri_str in entity_uris:
        uri_ref = URIRef(uri_str)
        if not any(target_graph.objects(uri_ref, RDFS.label)):
            needed.add(uri_str)
    if not needed:
        return 0

    logger.info(f"  Rufe Labels für {len(needed)} Entities ab...")
    all_needed = sorted(needed)
    total_added = 0
    lang_filter_parts = " || ".join(
        f'LANG(?label) = "{l}"' for l in languages
    )

    for batch_start in range(0, len(all_needed), LABEL_BATCH_SIZE):
        batch = all_needed[
            batch_start:batch_start + LABEL_BATCH_SIZE
        ]
        values_clause = " ".join(f"<{u}>" for u in batch)

        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?entity ?label WHERE {{
            VALUES ?entity {{ {values_clause} }}
            ?entity rdfs:label ?label .
            FILTER({lang_filter_parts})
        }}
        """
        data = sparql_query_with_retry(query)
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
        time.sleep(INTER_QUERY_DELAY)

    if total_added > 0:
        logger.info(
            f"  → {total_added} Entity-Label-Triples hinzugefügt"
        )
    return total_added


def build_batch_indirect_1hop_query(
    uri_batch: list[str], all_uri_set: set[str]
) -> str:
    values_a = " ".join(f"<{u}>" for u in uri_batch)
    values_all = " ".join(
        f"<{u}>" for u in sorted(all_uri_set)
    )

    return f"""
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT DISTINCT ?a ?b ?mid ?p1 ?p2 ?dir1 ?dir2 WHERE {{
      VALUES ?a {{ {values_a} }}
      VALUES ?b {{ {values_all} }}
      FILTER(?a != ?b)
      FILTER(STR(?a) < STR(?b))
      {{
        ?a ?p1 ?mid .
        ?mid ?p2 ?b .
        BIND("fwd" AS ?dir1) BIND("fwd" AS ?dir2)
      }} UNION {{
        ?mid ?p1 ?a .
        ?mid ?p2 ?b .
        BIND("rev" AS ?dir1) BIND("fwd" AS ?dir2)
      }} UNION {{
        ?a ?p1 ?mid .
        ?b ?p2 ?mid .
        BIND("fwd" AS ?dir1) BIND("rev" AS ?dir2)
      }} UNION {{
        ?mid ?p1 ?a .
        ?b ?p2 ?mid .
        BIND("rev" AS ?dir1) BIND("rev" AS ?dir2)
      }}
      FILTER(STRSTARTS(
          STR(?mid), "http://www.wikidata.org/entity/Q"))
      FILTER(STRSTARTS(
          STR(?p1), "http://www.wikidata.org/prop/direct/"))
      FILTER(STRSTARTS(
          STR(?p2), "http://www.wikidata.org/prop/direct/"))
      FILTER(?mid != ?a && ?mid != ?b)
    }} LIMIT {INDIRECT_RESULTS_LIMIT}
    """


def build_batch_indirect_2hop_query(
    uri_batch: list[str], all_uri_set: set[str]
) -> str:
    values_a = " ".join(f"<{u}>" for u in uri_batch)
    values_all = " ".join(
        f"<{u}>" for u in sorted(all_uri_set)
    )

    return f"""
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT DISTINCT ?a ?b ?mid1 ?mid2 ?p1 ?p2 ?p3 WHERE {{
      VALUES ?a {{ {values_a} }}
      VALUES ?b {{ {values_all} }}
      FILTER(?a != ?b)
      FILTER(STR(?a) < STR(?b))
      ?a ?p1 ?mid1 .
      ?mid1 ?p2 ?mid2 .
      ?mid2 ?p3 ?b .
      FILTER(STRSTARTS(
          STR(?mid1), "http://www.wikidata.org/entity/Q"))
      FILTER(STRSTARTS(
          STR(?mid2), "http://www.wikidata.org/entity/Q"))
      FILTER(STRSTARTS(
          STR(?p1), "http://www.wikidata.org/prop/direct/"))
      FILTER(STRSTARTS(
          STR(?p2), "http://www.wikidata.org/prop/direct/"))
      FILTER(STRSTARTS(
          STR(?p3), "http://www.wikidata.org/prop/direct/"))
      FILTER(?mid1 != ?a && ?mid1 != ?b)
      FILTER(?mid2 != ?a && ?mid2 != ?b)
      FILTER(?mid1 != ?mid2)
    }} LIMIT {INDIRECT_RESULTS_LIMIT}
    """


def discover_indirect_links(
    about_uris: list[URIRef],
    target_graph: Graph,
    languages: list[str],
    label_cache: set[str],
    max_hops: int = INDIRECT_MAX_HOPS
) -> bool:
    wd_uris = collect_wikidata_entity_uris(about_uris)
    if len(wd_uris) < 2:
        logger.info(
            "Indirekte Links: weniger als 2 Wikidata-Entities "
            "– überspringe."
        )
        return False

    all_uri_set = set(wd_uris)
    n_entities = len(wd_uris)
    n_possible_pairs = n_entities * (n_entities - 1) // 2
    n_batches_1hop = (
        (n_entities + INDIRECT_BATCH_SIZE - 1) // INDIRECT_BATCH_SIZE
    )

    logger.info(
        f"\n{'='*60}\n"
        f"Indirekte Links: {n_entities} Entities, "
        f"{n_possible_pairs} mögliche Paare\n"
        f"  Batch-Strategie: {n_batches_1hop} Batch-Queries "
        f"(je ≤{INDIRECT_BATCH_SIZE} Entities × alle {n_entities})\n"
        f"  Max Hops: {max_hops}\n"
        f"{'='*60}"
    )

    total_triples_added = 0
    total_paths_found = 0
    intermediate_entities: set[str] = set()
    collected_pids: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()

    # ── 1-hop batched queries ──
    for batch_idx in range(0, n_entities, INDIRECT_BATCH_SIZE):
        batch = wd_uris[
            batch_idx:batch_idx + INDIRECT_BATCH_SIZE
        ]
        batch_num = batch_idx // INDIRECT_BATCH_SIZE + 1

        logger.info(
            f"  1-Hop Batch {batch_num}/{n_batches_1hop}: "
            f"{len(batch)} Entities als Startpunkte..."
        )

        query = build_batch_indirect_1hop_query(
            batch, all_uri_set
        )
        data = sparql_query_with_retry(query)

        if data is None:
            logger.error(
                f"  1-Hop Batch {batch_num} fehlgeschlagen"
            )
            time.sleep(INTER_QUERY_DELAY)
            continue

        batch_paths = 0
        batch_triples = 0

        for r in data.get('results', {}).get('bindings', []):
            a_uri = r['a']['value']
            b_uri = r['b']['value']
            mid_uri = r['mid']['value']
            p1_uri = r['p1']['value']
            p2_uri = r['p2']['value']
            dir1 = r['dir1']['value']
            dir2 = r['dir2']['value']

            pair_key = (
                (a_uri, b_uri) if a_uri < b_uri
                else (b_uri, a_uri)
            )

            mid_ref = URIRef(mid_uri)
            a_ref = URIRef(a_uri)
            b_ref = URIRef(b_uri)
            p1_ref = URIRef(p1_uri)
            p2_ref = URIRef(p2_uri)

            if dir1 == "fwd":
                t1 = (a_ref, p1_ref, mid_ref)
            else:
                t1 = (mid_ref, p1_ref, a_ref)

            if dir2 == "fwd":
                t2 = (mid_ref, p2_ref, b_ref)
            else:
                t2 = (b_ref, p2_ref, mid_ref)

            added_here = 0
            for triple in [t1, t2]:
                if triple not in target_graph:
                    target_graph.add(triple)
                    added_here += 1

            marker = (
                mid_ref, INDIRECT_MARKER, Literal(True)
            )
            if marker not in target_graph:
                target_graph.add(marker)

            if added_here > 0:
                batch_triples += added_here
                batch_paths += 1

            intermediate_entities.add(mid_uri)
            seen_pairs.add(pair_key)
            for p_str in (p1_uri, p2_uri):
                pid = extract_property_id(p_str)
                if pid:
                    collected_pids.add(pid)

        total_triples_added += batch_triples
        total_paths_found += batch_paths

        if batch_paths > 0:
            logger.info(
                f"    → {batch_paths} Pfade, "
                f"{batch_triples} Triples"
            )

        time.sleep(INTER_QUERY_DELAY)

    # ── 2-hop batched queries ──
    if max_hops >= 2:
        n_batches_2hop = (
            (n_entities + INDIRECT_BATCH_SIZE - 1)
            // INDIRECT_BATCH_SIZE
        )
        logger.info(
            f"\n  2-Hop Durchlauf: "
            f"{n_batches_2hop} Batch-Queries..."
        )

        for batch_idx in range(
            0, n_entities, INDIRECT_BATCH_SIZE
        ):
            batch = wd_uris[
                batch_idx:batch_idx + INDIRECT_BATCH_SIZE
            ]
            batch_num = batch_idx // INDIRECT_BATCH_SIZE + 1

            logger.info(
                f"  2-Hop Batch {batch_num}/{n_batches_2hop}: "
                f"{len(batch)} Entities..."
            )

            query = build_batch_indirect_2hop_query(
                batch, all_uri_set
            )
            data = sparql_query_with_retry(query)

            if data is None:
                logger.error(
                    f"  2-Hop Batch {batch_num} fehlgeschlagen"
                )
                time.sleep(INTER_QUERY_DELAY)
                continue

            batch_paths = 0
            batch_triples = 0

            for r in data.get('results', {}).get('bindings', []):
                a_uri = r['a']['value']
                b_uri = r['b']['value']
                mid1_uri = r['mid1']['value']
                mid2_uri = r['mid2']['value']
                p1_uri = r['p1']['value']
                p2_uri = r['p2']['value']
                p3_uri = r['p3']['value']

                a_ref = URIRef(a_uri)
                b_ref = URIRef(b_uri)
                mid1_ref = URIRef(mid1_uri)
                mid2_ref = URIRef(mid2_uri)

                triples = [
                    (a_ref, URIRef(p1_uri), mid1_ref),
                    (mid1_ref, URIRef(p2_uri), mid2_ref),
                    (mid2_ref, URIRef(p3_uri), b_ref),
                ]

                added_here = 0
                for triple in triples:
                    if triple not in target_graph:
                        target_graph.add(triple)
                        added_here += 1

                for mid_ref in (mid1_ref, mid2_ref):
                    marker = (
                        mid_ref, INDIRECT_MARKER, Literal(True)
                    )
                    if marker not in target_graph:
                        target_graph.add(marker)

                if added_here > 0:
                    batch_triples += added_here
                    batch_paths += 1

                intermediate_entities.add(mid1_uri)
                intermediate_entities.add(mid2_uri)
                for p_str in (p1_uri, p2_uri, p3_uri):
                    pid = extract_property_id(p_str)
                    if pid:
                        collected_pids.add(pid)

            total_triples_added += batch_triples
            total_paths_found += batch_paths

            if batch_paths > 0:
                logger.info(
                    f"    → {batch_paths} Pfade, "
                    f"{batch_triples} Triples"
                )

            time.sleep(INTER_QUERY_DELAY)

    # ── Fetch labels for intermediate entities ──
    new_intermediates = intermediate_entities - all_uri_set
    if new_intermediates:
        label_count = fetch_entity_labels(
            new_intermediates, target_graph, languages
        )
        total_triples_added += label_count

    # ── Property labels ──
    if collected_pids:
        plabels = fetch_property_labels(
            collected_pids, target_graph, languages, label_cache
        )
        total_triples_added += plabels

    logger.info(
        f"\nIndirekte Links Zusammenfassung:\n"
        f"  {total_paths_found} Pfade gefunden\n"
        f"  {len(intermediate_entities)} Zwischen-Entities "
        f"({len(new_intermediates)} neu)\n"
        f"  {len(seen_pairs)} verbundene Paare\n"
        f"  {total_triples_added} Triples hinzugefügt"
    )

    return total_triples_added > 0


def main():
    parser = argparse.ArgumentParser(
        description="Schema.org JSON-LD → Wikidata-Anreicherung"
    )
    parser.add_argument(
        "input", help="URL oder Pfad zur JSON-LD Datei"
    )
    parser.add_argument(
        "-o", "--output", default="enriched_entities.ttl",
        help="Ausgabe-RDF-Datei (Standard: enriched_entities.ttl)"
    )
    parser.add_argument(
        "-l", "--languages",
        default=",".join(DEFAULT_LANGUAGES),
        help=(
            f"Sprachen "
            f"(Standard: {','.join(DEFAULT_LANGUAGES)})"
        )
    )
    parser.add_argument(
        "-a", "--all", action="store_true", dest="fetch_all",
        help=(
            f"Alle Properties statt Auswahl "
            f"({len(DEFAULT_PROPERTIES)} wdt:)"
        )
    )
    parser.add_argument(
        "-s", "--statements", action="store_true",
        help=(
            "Statement-Details (Qualifiers etc.). "
            "Impliziert -a."
        )
    )
    parser.add_argument(
        "-i", "--indirect", action="store_true",
        help=(
            "Suche nach indirekten Verbindungen zwischen Entities "
            "über Zwischen-Knoten (batched SPARQL)."
        )
    )
    parser.add_argument(
        "--indirect-hops", type=int, default=INDIRECT_MAX_HOPS,
        metavar="N",
        help=(
            f"Max Hop-Anzahl für indirekte Pfade "
            f"(1 oder 2, Standard: {INDIRECT_MAX_HOPS}). "
            f"Nur mit -i."
        )
    )
    parser.add_argument(
        "-t", "--type-hierarchy", action="store_true",
        help=(
            "Löst P31→P279 Typ-Hierarchie auf "
            "bis zur Wurzelklasse."
        )
    )
    parser.add_argument(
        "--hierarchy-depth", type=int,
        default=HIERARCHY_MAX_DEPTH,
        metavar="N",
        help=(
            f"Max Tiefe Typ-Hierarchie "
            f"(Standard: {HIERARCHY_MAX_DEPTH}). Nur mit -t."
        )
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Erzwingt Neu-Laden."
    )
    args = parser.parse_args()

    if args.statements:
        args.fetch_all = True

    if args.indirect_hops < 1:
        args.indirect_hops = 1
    elif args.indirect_hops > 2:
        logger.warning(
            f"--indirect-hops={args.indirect_hops} auf 2 begrenzt"
        )
        args.indirect_hops = 2

    if args.hierarchy_depth < 1:
        args.hierarchy_depth = 1

    languages = parse_languages(args.languages)
    logger.info(f"Sprachen: {', '.join(languages)}")

    if args.fetch_all:
        mode = (
            "ALLE + Statements" if args.statements
            else "ALLE Properties"
        )
    else:
        mode = (
            f"Kuratiert ({len(DEFAULT_PROPERTIES)} wdt: + "
            f"{len(DEFAULT_KEEP_PREDICATES)} allgemeine)"
        )
    if args.type_hierarchy:
        mode += (
            f" + Typ-Hierarchie "
            f"(max {args.hierarchy_depth} Ebenen)"
        )
    if args.indirect:
        mode += (
            f" + Indirekte Links "
            f"(max {args.indirect_hops} Hops, batched)"
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
            result_graph.parse(
                source=args.output, format=output_format
            )
            initial = len(result_graph)
            logger.info(
                f"{initial} bestehende Triples geladen."
            )
            bind_standard_prefixes(result_graph)
        except Exception as e:
            logger.warning(f"Laden fehlgeschlagen: {e}")

    label_cache = extract_cached_property_ids(result_graph)

    schema_added = merge_graphs(result_graph, schema_graph)
    logger.info(
        f"{schema_added} Schema.org-Triples "
        f"(Gesamt: {len(result_graph)})"
    )
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

        # ── Type hierarchy ──
        if args.type_hierarchy:
            if resolve_type_hierarchies(
                result_graph, about_uris, languages,
                label_cache, max_depth=args.hierarchy_depth
            ):
                modified = True

        # ── Indirect links (batched) ──
        if args.indirect:
            if discover_indirect_links(
                about_uris, result_graph, languages,
                label_cache, max_hops=args.indirect_hops
            ):
                modified = True

    except KeyboardInterrupt:
        logger.warning("Unterbrochen. Speichere...")
    finally:
        if modified or (initial == 0 and len(result_graph) > 0):
            save_graph(
                result_graph, args.output, output_format
            )
        else:
            logger.info("Keine Änderungen.")

    logger.info(f"Label-Cache: {len(label_cache)} Properties")


if __name__ == "__main__":
    main()