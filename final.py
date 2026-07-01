import json
import sys
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime

@dataclass
class NormalizedRecord:
    category: str                  # STATE_MARKS / COMMON_LAW / WEB_COMMON_LAW / BUSINESS_NAME / WEB_DOMAIN
    source_side: str               # "json1" or "json2"
    vendor_name: Optional[str] = None

    record_id: Optional[str] = None
    registration_number: Optional[str] = None
    primary_sic: Optional[str] = None

    owner_raw: str = ""
    owner_norm: str = ""
    owner_norm_spaced: str = ""
    owner_norm_compact: str = ""

    trademark_raw: str = ""
    trademark_norm: str = ""

    goods_raw: str = ""
    goods_norm: str = ""

    domain_raw: str = ""
    domain_norm: str = ""

    url_raw: str = ""
    url_norm: str = ""

    class_list: Tuple[int, ...] = ()

    skip_from_gate2: bool = False  # for WEB_DOMAIN rule_filter skip behavior

    raw_payload: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.owner_norm_spaced:
            self.owner_norm_spaced = normalize_owner_spaced(self.owner_raw)
        if not self.owner_norm_compact:
            self.owner_norm_compact = normalize_owner_compact(self.owner_raw)
        if not self.owner_norm:
            self.owner_norm = self.owner_norm_compact
        if isinstance(self.class_list, list):
            self.class_list = tuple(self.class_list)

@dataclass
class CategoryComparisonResult:
    category: str
    passed: int
    total: int
    failures: List[str]
    report_lines: List[str]
    skipped: int = 0
    total_extracted: int = 0

# Unified category mapping for internal comparison
CATEGORY_MAP = {
    "STATE_LAW": "STATE_MARKS",
    "COMMON_LAW": "COMMON_LAW",
    "WEB_COMMON_LAW": "WEB_COMMON_LAW",
    "USPTO": "USPTO_MARKS",
    "FEDERAL_USPTO": "USPTO_MARKS",
    "BUSINESS_NAME": "BUSINESS_NAME",
    "DOMAIN_NAME": "WEB_DOMAIN",
}

def _strip_attached_suffix(token: str) -> str:
    token_upper = token.upper()
    
    # Check CO (length > 2 because it must be attached to something)
    if token_upper.endswith("CO") and len(token_upper) > 2:
        if token_upper not in {
            "MEXICO", "CISCO", "TESCO", "COSTCO", "DISCO", "TACO", "CHICO", "COCO", 
            "TOBACCO", "CALICO", "MARCO", "MONACO", "MOROCCO", "ACAPULCO", "PORTICO", 
            "ROCOCO", "FRESCO", "FRANCISCO"
        }:
            return token[:-2]
            
    # Check INC
    if token_upper.endswith("INC") and len(token_upper) > 3:
        if token_upper not in {"ZINC"}:
            return token[:-3]
            
    # Check LLC
    if token_upper.endswith("LLC") and len(token_upper) > 3:
        return token[:-3]
        
    # Check CORP
    if token_upper.endswith("CORP") and len(token_upper) > 4:
        return token[:-4]
        
    # Check LTD
    if token_upper.endswith("LTD") and len(token_upper) > 3:
        return token[:-3]
        
    return token

def normalize_owner_spaced(name):
    """
    Normalizes company names while preserving word boundaries.
    Example: 'Empire Wine LLC' -> 'EMPIRE WINE'
    """
    if not name:
        return ""
    # Convert to uppercase
    name = str(name).upper()
    
    # Map & to AND to handle 'Crescent Wine & Spirits' vs 'Crescentwineandspirits'
    name = name.replace("&", " AND ")

    # Requirement 3: Normalize acronym punctuation (U.S. -> US)
    name = re.sub(r'\b([A-Z])\.(?=[A-Z]\.|\b)', r'\1', name)

    # Remove apostrophes
    name = name.replace("'", "")
    # Remove other common punctuation and replace with space (ignoring & as it is handled)
    name = re.sub(r'[.,\-():;\"?/]', ' ', name)
    
    # Expand suffixes to ignore common ones (excluding FOOD/FOODS to maintain consistency)
    suffixes = [
        r'\bINC\b', r'\bLTD\b', r'\bCO\b', r'\bCORP\b', 
        r'\bCORPORATED\b', r'\bINCORPORATED\b', r'\bUSA\b', r'\bLLC\b'
    ]
    for suffix in suffixes:
        name = re.sub(suffix, '', name)
        
    # Process tokens to strip attached suffixes
    tokens = name.split(" ")
    processed_tokens = []
    for token in tokens:
        if token:
            processed_tokens.append(_strip_attached_suffix(token))
    name = " ".join(processed_tokens)
    
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def normalize_owner_compact(name):
    """
    Compact owner normalization used as a fallback and for existing candidate keys.
    """
    return re.sub(r'\s+', '', normalize_owner_spaced(name))

def normalize_owner(name):
    """
    Backward-compatible owner normalization. Kept compact so existing candidate keys
    continue matching whitespace-variant owners.
    """
    return normalize_owner_compact(name)

def normalize_goods_services(text):
    """
    Normalizes goods and services text: uppercase, strip, collapse spaces,
    and collapses repeated consecutive phrases.
    """
    if not text:
        return ""
    
    # Basic normalization
    text = re.sub(r'\s+', ' ', str(text).upper()).strip()
    
    # Requirement 1: Collapse repeated consecutive phrases
    # Example: "ABC ABC" -> "ABC"
    # We use a regex that matches a phrase followed by itself one or more times.
    # To keep it safe and avoid accidental over-matching, we look for space-separated identical blocks.
    # This is a bit tricky with regex for long phrases. A better way is a loop or specific split.
    
    words = text.split()
    if not words:
        return ""
        
    def collapse_repeats(word_list):
        n = len(word_list)
        # Try finding repeated sequences of length 1 to n/2
        for length in range(1, n // 2 + 1):
            for i in range(n - 2 * length + 1):
                phrase1 = word_list[i : i + length]
                phrase2 = word_list[i + length : i + 2 * length]
                if phrase1 == phrase2:
                    # Found a repeat. Collapse it and recurse.
                    return collapse_repeats(word_list[: i + length] + word_list[i + 2 * length :])
        return word_list

    collapsed_words = collapse_repeats(words)
    return " ".join(collapsed_words)

def normalize_mark_text(text):
    """
    Normalizes trademark text: uppercase, strip, punctuation normalization.
    """
    if not text:
        return ""
    # Uppercase
    text = str(text).upper()
    # Remove punctuation similar to owner but perhaps less aggressive if needed
    # For now, let's keep it consistent with owner normalization but specific to trademarks
    text = re.sub(r'[.,\-&]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def clean_registration_number(s):
    """
    Strips all non-digit characters for robust matching.
    """
    return "".join(re.findall(r'\d+', str(s or "")))

def normalize_domain_value(value):
    """
    Normalizes a domain-like value without changing the existing text normalization pipeline.
    """
    if not value:
        return ""
    value = str(value).strip().lower()
    value = re.sub(r'^[a-z]+://', '', value)
    value = value.split('/')[0].split('?')[0].split('#')[0]
    value = re.sub(r'^www\.', '', value)
    return value.strip().rstrip('.')

def normalize_url_value(value):
    """
    Normalizes a URL-like value for identity matching.
    """
    if not value:
        return ""
    value = str(value).strip().lower()
    value = re.sub(r'^[a-z]+://', '', value)
    value = re.sub(r'^www\.', '', value)
    return value.strip().rstrip('/')

def _payload_lookup(payload: Dict[str, Any], *keys: str) -> str:
    """
    Case-insensitive payload lookup used only for optional candidate-selection keys.
    """
    if not isinstance(payload, dict):
        return ""
    lowered = {str(k).lower(): v for k, v in payload.items()}
    for key in keys:
        val = lowered.get(key.lower())
        if val not in (None, ""):
            return str(val)
    return ""

def _extract_domain_raw(payload: Dict[str, Any]) -> str:
    return _payload_lookup(
        payload,
        "domain", "domain_name", "domainName", "Domain", "Domain Name",
        "website_domain", "host", "hostname", "dnn"
    )

def _extract_url_raw(payload: Dict[str, Any]) -> str:
    return _payload_lookup(
        payload,
        "url", "URL", "source_url", "website", "website_url", "web_url",
        "link", "page_url", "Web_start_page"
    )

def _record_jurisdiction_norm(record: NormalizedRecord) -> str:
    raw = _payload_lookup(
        record.raw_payload,
        "jurisdiction", "state", "State", "state_name", "business_state",
        "filing_state", "location_state"
    )
    return normalize_mark_text(raw)

def _record_source_norm(record: NormalizedRecord) -> str:
    raw = (
        record.domain_raw
        or record.url_raw
        or _payload_lookup(record.raw_payload, "source", "platform", "site", "website", "publisher", "marketplace")
    )
    return normalize_domain_value(raw) or normalize_mark_text(raw)

def _candidate_display_id(record: NormalizedRecord) -> str:
    if record.record_id:
        return str(record.record_id)
    for key in ("id", "record_id", "Doc No.", "COL", "BUS", "DN", "Nr.", "dnn", "bsn"):
        val = _payload_lookup(record.raw_payload, key)
        if val:
            return val
    parts = [record.registration_number, record.trademark_raw, record.owner_raw]
    return " | ".join([str(p) for p in parts if p]) or "Unknown"

def _dedupe_candidates(candidates: List[NormalizedRecord]) -> List[NormalizedRecord]:
    seen = set()
    unique_candidates = []
    for c in candidates or []:
        if id(c) not in seen:
            seen.add(id(c))
            unique_candidates.append(c)
    return unique_candidates

def _matched_fields(rec2: NormalizedRecord, cand: NormalizedRecord) -> List[str]:
    fields = []
    if rec2.registration_number and cand.registration_number and rec2.registration_number == cand.registration_number:
        fields.append("Registration Number")
    if rec2.domain_norm and cand.domain_norm and rec2.domain_norm == cand.domain_norm:
        fields.append("Domain")
    if rec2.url_norm and cand.url_norm and rec2.url_norm == cand.url_norm:
        fields.append("URL")
    if rec2.trademark_norm and cand.trademark_norm and rec2.trademark_norm == cand.trademark_norm:
        fields.append("Trademark")
    if rec2.owner_norm and cand.owner_norm and rec2.owner_norm == cand.owner_norm:
        fields.append("Owner")
    if rec2.goods_norm and cand.goods_norm and rec2.goods_norm == cand.goods_norm:
        fields.append("Goods")
    if rec2.class_list and cand.class_list and rec2.class_list == cand.class_list:
        fields.append("Class")
    if rec2.primary_sic and cand.primary_sic and rec2.primary_sic == cand.primary_sic:
        fields.append("SIC")
    if _record_jurisdiction_norm(rec2) and _record_jurisdiction_norm(rec2) == _record_jurisdiction_norm(cand):
        fields.append("Jurisdiction/State")
    return fields

def _format_ambiguity_diagnostics(
    rec2: NormalizedRecord,
    candidates: List[NormalizedRecord],
    category: str,
    tier_name: str,
    reason: str
) -> List[str]:
    lines = [
        "AMBIGUOUS MATCH",
        f"Tier: {tier_name}",
        "Candidates:"
    ]
    for idx, cand in enumerate(_dedupe_candidates(candidates), start=1):
        matched = _matched_fields(rec2, cand)
        lines.extend([
            f"Candidate {idx}",
            f"Record ID : {_candidate_display_id(cand)}",
            f"Score : {_score_candidate(rec2, cand, category):g}",
            "Matched : " + (", ".join(matched) if matched else "None")
        ])
    lines.extend(["Reason", reason])
    return lines

def _select_candidate_from_tiers(
    rec2: NormalizedRecord,
    tiers: List[Tuple[str, List[NormalizedRecord]]],
    category: str
) -> Tuple[Optional[NormalizedRecord], bool, List[str], str]:
    """
    Applies existing tier architecture but requires each selected tier to identify one record.
    """
    for tier_name, tier_candidates in tiers:
        unique_candidates = _dedupe_candidates(tier_candidates)
        if not unique_candidates:
            continue
        if len(unique_candidates) == 1:
            return unique_candidates[0], False, [], tier_name
            
        # Apply score-based tie breaker
        if category == "BUSINESS_NAME":
            best_cand, remains_ambiguous = select_unique_best_by_margin(rec2, unique_candidates, category, min_margin=3)
        else:
            best_cand, remains_ambiguous = _find_best_candidate(rec2, unique_candidates, category)
        if not remains_ambiguous and best_cand:
            return best_cand, False, [], tier_name
            
        diagnostics = _format_ambiguity_diagnostics(
            rec2,
            unique_candidates,
            category,
            tier_name,
            "Multiple candidates reached the same matching tier/confidence."
        )
        return None, True, diagnostics, tier_name
    return None, False, [], ""

def looks_like_state_law_class_mapping_bug(json1_classes, json2_classes) -> bool: 
    try: 
        j1 = set(int(x) for x in json1_classes) 
        j2 = set(int(x) for x in json2_classes) 
    except Exception: 
        return False 
 
    if not j1 or not j2: 
        return False 
 
    suspicious_json1 = any(c == 0 or c < 10 for c in j1) 
    valid_json2_nice_classes = any(20 <= c <= 45 for c in j2) 
 
    return suspicious_json1 and valid_json2_nice_classes 

def compare_state_marks(json1_records: List[NormalizedRecord], 
                        json2_records: List[NormalizedRecord]) -> CategoryComparisonResult:
    """
    Comparator for STATE_MARKS. Anchor: registration_number.
    Modernized Approach (Option B): Normalized comparison + class only if both exist.
    """
    # Group JSON 1 by registration number
    json1_map = {}
    for r in json1_records:
        reg = r.registration_number or ""
        if reg not in json1_map:
            json1_map[reg] = []
        json1_map[reg].append(r)
    
    passed = 0
    failures = []
    report_lines = ["CATEGORY: STATE_MARKS GATE 2 REPORT", "="*40]

    for rec2 in json2_records:
        reg_no = rec2.registration_number or ""
        rec_id = rec2.record_id
        
        candidates = json1_map.get(reg_no, [])
        if len(_dedupe_candidates(candidates)) > 1:
            secondary_candidates = [
                c for c in candidates
                if rec2.trademark_norm and rec2.owner_norm
                and c.trademark_norm == rec2.trademark_norm
                and c.owner_norm == rec2.owner_norm
            ]
            if len(_dedupe_candidates(secondary_candidates)) == 1:
                rec1, is_ambiguous, diagnostics, _ = secondary_candidates[0], False, [], "Registration Number + Trademark + Owner"
            else:
                ambiguous_pool = secondary_candidates or candidates
                rec1, is_ambiguous, diagnostics, _ = None, True, _format_ambiguity_diagnostics(
                    rec2,
                    ambiguous_pool,
                    "STATE_MARKS",
                    "Registration Number + Trademark + Owner",
                    f"Registration number '{reg_no}' matched multiple candidates and Trademark + Owner did not identify exactly one record."
                ), "Registration Number + Trademark + Owner"
        else:
            rec1, is_ambiguous, diagnostics, _ = _select_candidate_from_tiers(
                rec2,
                [("Registration Number", candidates)],
                "STATE_MARKS"
            )
        
        if is_ambiguous:
            failures.append(f"{rec_id} (Reg {reg_no}): AMBIGUOUS MATCH - Multiple JSON1 candidates found.")
            report_lines.append(f"FAIL: {rec_id} - Ambiguous candidates")
            report_lines.extend([f"  {line}" for line in diagnostics])
            continue

        if not rec1:
            failures.append(f"{rec_id}: No matching registration number '{reg_no}' found in JSON 1.")
            report_lines.append(f"FAIL: {rec_id} - No matching registration number found")
            continue
            
        match_errors = []
        field_results = []
        
        f_owner = _get_field_match_info(rec1.owner_raw, rec1.owner_norm, rec2.owner_raw, rec2.owner_norm, "Owner")
        field_results.append(f_owner)
        
        f_goods = _get_field_match_info(rec1.goods_raw, rec1.goods_norm, rec2.goods_raw, rec2.goods_norm, "Goods")
        field_results.append(f_goods)
        
        f_tm = _get_field_match_info(rec1.trademark_raw, rec1.trademark_norm, rec2.trademark_raw, rec2.trademark_norm, "Trademark")
        field_results.append(f_tm)
        
        # modernized: compare class only if both are non-empty
        if rec1.class_list and rec2.class_list and rec1.class_list != rec2.class_list:
            if looks_like_state_law_class_mapping_bug(rec1.class_list, rec2.class_list):
                match_errors.append(
                    f"Class: {rec1.class_list} != {rec2.class_list} "
                    "[LIKELY_EXTRACTION_DEFECT: JSON1 class values look like indexes/ordinals]"
                )
            else:
                match_errors.append(f"Class: {rec1.class_list} != {rec2.class_list}")
            
        for fr in field_results:
            if _field_failure(fr["status"]):
                match_errors.append(fr["error"])
        
        if not match_errors:
            passed += 1
            status = _record_status_from_field_results(field_results)
            report_lines.append(f"{status}: {rec_id} (Reg: {reg_no})")
            _append_field_result_info(report_lines, field_results)
        else:
            failures.append(f"{rec_id} (Reg {reg_no}): " + " | ".join(match_errors))
            report_lines.append(f"FAIL/PARTIAL: {rec_id}")
            for err in match_errors: report_lines.append(f"  - {err}")

    return CategoryComparisonResult("STATE_MARKS", passed, len(json2_records), failures, report_lines)


def _score_candidate(rec2: NormalizedRecord, cand: NormalizedRecord, category: str) -> float:
    """
    Heuristic scoring for candidate selection.
    Weights: Trademark (+10), Owner (+8), Goods (+5), Class (+2), SIC (+1).
    """
    score = 0.0
    # Exact Trademark Match
    if rec2.trademark_norm == cand.trademark_norm:
        score += 10.0
    # Exact Owner Match
    if rec2.owner_norm == cand.owner_norm:
        score += 8.0
    # Exact Goods Match
    if rec2.goods_norm == cand.goods_norm:
        score += 5.0
    # Class match (only if both non-empty)
    if rec2.class_list and cand.class_list and rec2.class_list == cand.class_list:
        score += 2.0
    # Primary SIC (Business Name only)
    if category == "BUSINESS_NAME":
        if rec2.primary_sic and cand.primary_sic and rec2.primary_sic == cand.primary_sic:
            score += 1.0
    return score

def business_name_tiebreak_score(rec2: NormalizedRecord, cand: NormalizedRecord) -> float: 
    score = 0.0 
 
    if rec2.trademark_norm == cand.trademark_norm: 
        score += 20.0 
 
    if rec2.owner_norm_spaced == cand.owner_norm_spaced: 
        score += 12.0 
    elif rec2.owner_norm_compact == cand.owner_norm_compact: 
        score += 8.0 
 
    if rec2.goods_norm == cand.goods_norm: 
        score += 10.0 
 
    if rec2.class_list and cand.class_list and rec2.class_list == cand.class_list: 
        score += 5.0 
 
    if rec2.primary_sic and cand.primary_sic and rec2.primary_sic == cand.primary_sic: 
        score += 2.0 
 
    if _record_jurisdiction_norm(rec2) and _record_jurisdiction_norm(rec2) == _record_jurisdiction_norm(cand): 
        score += 8.0 
 
    return score 

def select_unique_best_by_margin(rec2: NormalizedRecord, candidates: List[NormalizedRecord], category: str, min_margin=3) -> Tuple[Optional[NormalizedRecord], bool]: 
    if not candidates:
        return None, False
    scored = sorted( 
        [(business_name_tiebreak_score(rec2, c), c) for c in candidates], 
        key=lambda x: x[0], 
        reverse=True 
    ) 
 
    if len(scored) == 1: 
        return scored[0][1], False 
 
    if scored[0][0] - scored[1][0] >= min_margin: 
        return scored[0][1], False 
 
    return None, True

def _find_best_candidate(rec2: NormalizedRecord, candidates: List[NormalizedRecord], category: str) -> Tuple[Optional[NormalizedRecord], bool]:
    """
    Evaluates every candidate, selects the unique best one.
    Returns (best_candidate, is_ambiguous).
    """
    if not candidates:
        return None, False
    
    # Deduplicate pool by object identity (if multiple tiers combined)
    seen = set()
    unique_candidates = []
    for c in candidates:
        if id(c) not in seen:
            seen.add(id(c))
            unique_candidates.append(c)

    if len(unique_candidates) == 1:
        return unique_candidates[0], False
        
    best_cand = None
    max_score = -1.0
    scores = []
    
    for cand in unique_candidates:
        s = _score_candidate(rec2, cand, category)
        scores.append((s, cand))
        if s > max_score:
            max_score = s
            best_cand = cand
            
    # Check for ambiguity: multiple candidates with the same max_score
    top_candidates = [c for s, c in scores if s == max_score]
    if len(top_candidates) > 1:
        return None, True
        
    return best_cand, False

MISSING_VALUE_TOKENS = {"", "NONE", "NULL", "UNKNOWN", "N/A", "NA", "NONE IDENTIFIED"}

GOODS_SEMANTIC_STOPWORDS = {
    "A", "AN", "THE", "AND", "OR", "FOR", "WITH", "WITHOUT", "INCLUDING", "INCLUDES",
    "INCLUDE", "NAMELY", "OF", "TO", "IN", "ON", "BY", "FROM", "RELATED", "FEATURING",
    "GOOD", "GOODS", "SERVICE", "SERVICES", "PRODUCT", "PRODUCTS", "ITEM", "ITEMS",
    "RETAIL", "WHOLESALE", "ONLINE", "SALE", "SALES", "PROVIDING", "PROVISION", "FOR", "ITEMS"
}

def _is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    return str(value).strip().upper() in MISSING_VALUE_TOKENS

def _field_failure(status: str) -> bool:
    return status in {"FAIL", "MISSING_JSON1", "MISSING_JSON2"}

def _field_status_to_record_status(status: str) -> str:
    return {
        "EXACT": "PASS_EXACT",
        "NORMALIZED": "PASS_NORMALIZED",
        "SUBSTRING": "PASS_SUBSTRING",
        "SEMANTIC_NEAR": "PASS_SEMANTIC_NEAR",
        "MISSING_BOTH": "MISSING_BOTH",
        "SKIPPED_OPTIONAL": "SKIPPED_OPTIONAL",
        "OWNER_WARNING": "OWNER_WARNING",
    }.get(status, status)

def _record_status_from_field_results(field_results: List[Dict[str, Any]]) -> str:
    status_priority = ["EXACT", "NORMALIZED", "SUBSTRING", "SEMANTIC_NEAR", "MISSING_BOTH", "SKIPPED_OPTIONAL", "OWNER_WARNING"]
    current_top = "EXACT"
    for fr in field_results:
        status = fr.get("status")
        if status in status_priority and status_priority.index(status) > status_priority.index(current_top):
            current_top = status
    return _field_status_to_record_status(current_top)

def _append_field_result_info(report_lines: List[str], field_results: List[Dict[str, Any]]) -> None:
    for fr in field_results:
        if fr.get("info") and fr.get("status") != "EXACT":
            report_lines.append(f"  - {fr['info']}")

def _meaningful_goods_words(norm_text: str) -> set:
    words = re.findall(r"[A-Z0-9]+", norm_text or "")
    return {w for w in words if len(w) > 2 and w not in GOODS_SEMANTIC_STOPWORDS}

GOODS_DOMAIN_GROUPS = { 
    "food": {"FOOD", "ICE", "CREAM", "BAKERY", "SNACK", "CANDY", "BEVERAGE", "FROZEN"}, 
    "automotive": {"AUTO", "AUTOMOTIVE", "CAR", "VEHICLE", "DETAILING", "POLISHING"}, 
    "software": {"SOFTWARE", "APPLICATION", "DOWNLOADABLE", "PLATFORM", "MOBILE"}, 
    "domain": {"DOMAIN", "REGISTRATION", "HOSTING", "WEBSITE", "WEB"}, 
    "medical": {"HEALTH", "MEDICAL", "WELLNESS", "PHARMACEUTICAL"}, 
}

def _dominant_goods_groups(words: set) -> set: 
    groups = set() 
    for group, terms in GOODS_DOMAIN_GROUPS.items(): 
        if words.intersection(terms): 
            groups.add(group) 
    return groups

def _semantic_goods_match(n1: str, n2: str) -> Tuple[bool, str]:
    words1 = _meaningful_goods_words(n1)
    words2 = _meaningful_goods_words(n2)
    if not words1 or not words2:
        return False, "No meaningful goods keywords after stopword filtering."

    # Group compatibility check to prevent false positives from generic words
    groups1 = _dominant_goods_groups(words1)
    groups2 = _dominant_goods_groups(words2)
    if groups1 and groups2 and groups1.isdisjoint(groups2):
        return False, f"Different goods domains: {groups1} vs {groups2}"

    overlap = words1.intersection(words2)
    if not overlap:
        return False, "No meaningful domain keyword overlap."

    smaller_set = words1 if len(words1) < len(words2) else words2
    ratio = len(overlap) / len(smaller_set)
    if ratio >= 0.75:
        return True, f"Meaningful keyword overlap {sorted(overlap)} with ratio {ratio:.2f}."
    return False, f"Meaningful keyword overlap ratio {ratio:.2f} below threshold."

def _get_field_match_info(raw1: str, norm1: str, raw2: str, norm2: str, field_name: str) -> Dict[str, Any]:
    """
    Analyzes field matching with explicit method and missing-value statuses.
    """
    s1 = str(raw1 or "").strip()
    s2 = str(raw2 or "").strip()
    missing1 = _is_missing_value(raw1)
    missing2 = _is_missing_value(raw2)

    if missing1 and missing2:
        return {
            "status": "MISSING_BOTH",
            "error": None,
            "info": f"{field_name}: [MISSING_BOTH] JSON1 and JSON2 are both missing."
        }
    if missing1:
        return {
            "status": "MISSING_JSON1",
            "error": f"{field_name}: [MISSING_JSON1] JSON1 missing while JSON2 has '{s2}'",
            "info": None
        }
    if missing2:
        return {
            "status": "MISSING_JSON2",
            "error": f"{field_name}: [MISSING_JSON2] JSON2 missing while JSON1 has '{s1}'",
            "info": None
        }

    if s1 == s2:
        return {
            "status": "EXACT",
            "error": None,
            "info": f"{field_name}: [EXACT] Raw values match exactly."
        }

    if field_name == "Owner":
        spaced1 = normalize_owner_spaced(raw1)
        spaced2 = normalize_owner_spaced(raw2)
        if spaced1 and spaced1 == spaced2:
            return {
                "status": "NORMALIZED",
                "error": None,
                "info": f"{field_name}: [NORMALIZED SPACED] J1:'{s1}' | J2:'{s2}' (Norm: '{spaced1}')"
            }

        compact1 = normalize_owner_compact(raw1)
        compact2 = normalize_owner_compact(raw2)
        if compact1 and compact1 == compact2:
            return {
                "status": "NORMALIZED",
                "error": None,
                "info": f"{field_name}: [NORMALIZED COMPACT FALLBACK] J1:'{s1}' | J2:'{s2}' (Norm: '{compact1}')"
            }
        if spaced1 and spaced2 and (spaced1 in spaced2 or spaced2 in spaced1):
            return {
                "status": "SUBSTRING",
                "error": None,
                "info": f"{field_name}: [SUBSTRING SPACED] One spaced-normalized owner contains the other."
            }
        if compact1 and compact2 and (compact1 in compact2 or compact2 in compact1):
            return {
                "status": "SUBSTRING",
                "error": None,
                "info": f"{field_name}: [SUBSTRING COMPACT FALLBACK] One compact-normalized owner contains the other."
            }
        n1, n2 = spaced1, spaced2
    else:
        n1 = str(norm1 or "").strip()
        n2 = str(norm2 or "").strip()
        if n1 and n1 == n2:
            return {
                "status": "NORMALIZED",
                "error": None,
                "info": f"{field_name}: [NORMALIZED MATCH] J1:'{s1}' | J2:'{s2}' (Norm: '{n1}')"
            }

    if n1 and n2 and (n1 in n2 or n2 in n1):
        return {
            "status": "SUBSTRING",
            "error": None,
            "info": f"{field_name}: [SUBSTRING] One normalized value contains the other."
        }

    if field_name == "Goods" and n1 and n2:
        is_match, reason = _semantic_goods_match(n1, n2)
        if is_match:
            return {
                "status": "SEMANTIC_NEAR",
                "error": None,
                "info": f"{field_name}: [SEMANTIC_NEAR] {reason}"
            }

    return {
        "status": "FAIL",
        "error": f"{field_name}: [FAIL] J1:'{s1}' != J2:'{s2}'",
        "info": None
    }


def compare_common_law(json1_records: List[NormalizedRecord], 
                       json2_records: List[NormalizedRecord]) -> CategoryComparisonResult:
    """
    Comparator for COMMON_LAW. 
    Implements tiered search: Owner+TM -> TM+Goods -> TM -> Owner+Goods -> Owner.
    """
    # Build tiered maps for JSON 1
    maps = {
        "owner_tm": {},
        "goods_tm": {},
        "tm": {},
        "owner_goods": {},
        "owner": {}
    }
    for r in json1_records:
        if r.owner_norm and r.trademark_norm:
            key = f"{r.owner_norm}|{r.trademark_norm}"
            if key not in maps["owner_tm"]: maps["owner_tm"][key] = []
            maps["owner_tm"][key].append(r)
        if r.trademark_norm:
            if r.trademark_norm not in maps["tm"]: maps["tm"][r.trademark_norm] = []
            maps["tm"][r.trademark_norm].append(r)
        if r.owner_norm:
            if r.owner_norm not in maps["owner"]: maps["owner"][r.owner_norm] = []
            maps["owner"][r.owner_norm].append(r)
        if r.goods_norm and r.trademark_norm:
            key = f"{r.goods_norm}|{r.trademark_norm}"
            if key not in maps["goods_tm"]: maps["goods_tm"][key] = []
            maps["goods_tm"][key].append(r)
        if r.owner_norm and r.goods_norm:
            key = f"{r.owner_norm}|{r.goods_norm}"
            if key not in maps["owner_goods"]: maps["owner_goods"][key] = []
            maps["owner_goods"][key].append(r)
            
    passed = 0
    failures = []
    report_lines = ["CATEGORY: COMMON_LAW GATE 2 REPORT", "="*40]

    for rec2 in json2_records:
        rec_id = rec2.record_id
        
        owner_only_candidates = maps["owner"].get(rec2.owner_norm, []) if rec2.owner_norm else []
        if len(_dedupe_candidates(owner_only_candidates)) == 1:
            owner_candidate = _dedupe_candidates(owner_only_candidates)[0]
            if rec2.trademark_norm and owner_candidate.trademark_norm and owner_candidate.trademark_norm != rec2.trademark_norm:
                owner_only_candidates = []
            
        tiers = [
            ("Owner + Trademark", maps["owner_tm"].get(f"{rec2.owner_norm}|{rec2.trademark_norm}", []) if rec2.owner_norm and rec2.trademark_norm else []),
            ("Trademark + Goods", maps["goods_tm"].get(f"{rec2.goods_norm}|{rec2.trademark_norm}", []) if rec2.goods_norm and rec2.trademark_norm else []),
            ("Trademark", maps["tm"].get(rec2.trademark_norm, []) if rec2.trademark_norm else []),
            ("Owner + Goods", maps["owner_goods"].get(f"{rec2.owner_norm}|{rec2.goods_norm}", []) if rec2.owner_norm and rec2.goods_norm else []),
            ("Owner", owner_only_candidates),
        ]
        rec1, is_ambiguous, diagnostics, _ = _select_candidate_from_tiers(rec2, tiers, "COMMON_LAW")
        
        if is_ambiguous:
            failures.append(f"{rec_id}: AMBIGUOUS MATCH - Multiple JSON1 candidates found.")
            report_lines.append(f"FAIL: {rec_id} - Ambiguous candidates")
            report_lines.extend([f"  {line}" for line in diagnostics])
            continue

        if rec1:
            match_errors = []
            field_results = []
            
            f_owner = _get_field_match_info(rec1.owner_raw, rec1.owner_norm, rec2.owner_raw, rec2.owner_norm, "Owner")
            field_results.append(f_owner)
            
            f_goods = _get_field_match_info(rec1.goods_raw, rec1.goods_norm, rec2.goods_raw, rec2.goods_norm, "Goods")
            field_results.append(f_goods)
            
            f_tm = _get_field_match_info(rec1.trademark_raw, rec1.trademark_norm, rec2.trademark_raw, rec2.trademark_norm, "Trademark")
            field_results.append(f_tm)

            if rec1.class_list and rec2.class_list and rec1.class_list != rec2.class_list:
                match_errors.append(f"Class: {rec1.class_list} != {rec2.class_list}")
                
            for fr in field_results:
                if _field_failure(fr["status"]):
                    match_errors.append(fr["error"])
            
            if not match_errors:
                passed += 1
                status = _record_status_from_field_results(field_results)
                report_lines.append(f"{status}: {rec_id} (Owner: {rec2.owner_raw})")
                _append_field_result_info(report_lines, field_results)
            else:
                failures.append(f"{rec_id} (Owner: {rec2.owner_raw}): " + " | ".join(match_errors))
                report_lines.append(f"FAIL/PARTIAL: {rec_id}")
                for err in match_errors: report_lines.append(f"  - {err}")
        else:
            failures.append(f"{rec_id}: No matching JSON1 record found for '{rec2.trademark_raw}' / '{rec2.owner_raw}'")
            report_lines.append(f"FAIL: {rec_id} - No matching record found")

    return CategoryComparisonResult("COMMON_LAW", passed, len(json2_records), failures, report_lines)

def compare_web_common_law(json1_records: List[NormalizedRecord], 
                           json2_records: List[NormalizedRecord]) -> CategoryComparisonResult:
    """
    Comparator for WEB_COMMON_LAW.
    Tiered search: TM+Owner -> TM -> Owner.
    Requirement 4 & 5: Improved owner and goods logic.
    """
    json1_tm_owner_map = {}
    json1_tm_source_map = {}
    json1_tm_map = {}
    json1_owner_map = {}
    
    for r in json1_records:
        # Multi-key for Mark+Owner
        key = f"{r.trademark_norm or ''}|{r.owner_norm or ''}"
        if key not in json1_tm_owner_map: json1_tm_owner_map[key] = []
        json1_tm_owner_map[key].append(r)
        
        if r.trademark_norm:
            if r.trademark_norm not in json1_tm_map: json1_tm_map[r.trademark_norm] = []
            json1_tm_map[r.trademark_norm].append(r)
            source_norm = _record_source_norm(r)
            if source_norm:
                source_key = f"{r.trademark_norm}|{source_norm}"
                if source_key not in json1_tm_source_map: json1_tm_source_map[source_key] = []
                json1_tm_source_map[source_key].append(r)
        if r.owner_norm:
            if r.owner_norm not in json1_owner_map: json1_owner_map[r.owner_norm] = []
            json1_owner_map[r.owner_norm].append(r)
            
    passed = 0
    failures = []
    report_lines = ["CATEGORY: WEB_COMMON_LAW GATE 2 REPORT", "="*40]

    # Requirement 4: Unreliable owner list
    UNRELIABLE_OWNERS = {"SHOP", "BAY", "PINTEREST", "POSTMATES", "MARKETPLACE", "SELLER", "HANDLE", "UNKNOWN"}

    for rec2 in json2_records:
        rec_id = rec2.record_id
        
        rec2_owner_is_unreliable = rec2.owner_norm in UNRELIABLE_OWNERS or not rec2.owner_norm or len(rec2.owner_norm) < 3
        tm_owner_candidates = []
        if not rec2_owner_is_unreliable:
            key = f"{rec2.trademark_norm or ''}|{rec2.owner_norm or ''}"
            tm_owner_candidates = json1_tm_owner_map.get(key, [])

        source_norm = _record_source_norm(rec2)
        tiers = [
            ("Trademark + Owner", tm_owner_candidates),
            ("Trademark + Source/Domain/Platform", json1_tm_source_map.get(f"{rec2.trademark_norm}|{source_norm}", []) if rec2.trademark_norm and source_norm else []),
            ("Trademark", json1_tm_map.get(rec2.trademark_norm, []) if rec2.trademark_norm else []),
            ("Owner", [] if rec2_owner_is_unreliable else json1_owner_map.get(rec2.owner_norm, [])),
        ]
        rec1, is_ambiguous, diagnostics, _ = _select_candidate_from_tiers(rec2, tiers, "WEB_COMMON_LAW")
        
        if is_ambiguous:
            failures.append(f"{rec_id}: AMBIGUOUS MATCH - Multiple JSON1 candidates found.")
            report_lines.append(f"FAIL: {rec_id} - Ambiguous candidates")
            report_lines.extend([f"  {line}" for line in diagnostics])
            continue

        if rec1:
            match_errors = []
            field_results = []
            warning_only = False
            
            # Requirement 5: Missing Goods Handling
            if _is_missing_value(rec2.goods_raw) and not _is_missing_value(rec1.goods_raw):
                field_results.append({"status": "SKIPPED_OPTIONAL", "error": None, "info": "Goods: [SKIPPED_OPTIONAL] Missing in JSON 2 optional web common law field."})
            elif not _is_missing_value(rec2.goods_raw):
                f_goods = _get_field_match_info(rec1.goods_raw, rec1.goods_norm, rec2.goods_raw, rec2.goods_norm, "Goods")
                field_results.append(f_goods)
            else:
                field_results.append(_get_field_match_info(rec1.goods_raw, rec1.goods_norm, rec2.goods_raw, rec2.goods_norm, "Goods"))
            
            # Requirement 4: Owner Unreliable Check
            f_owner = _get_field_match_info(rec1.owner_raw, rec1.owner_norm, rec2.owner_raw, rec2.owner_norm, "Owner")
            if _field_failure(f_owner["status"]):
                # Check if JSON 2 owner is in unreliable list or is very short/generic
                if rec2.owner_norm in UNRELIABLE_OWNERS or not rec2.owner_norm or len(rec2.owner_norm) < 3:
                    f_owner["status"] = "OWNER_WARNING"
                    f_owner["info"] = f"Owner: [WARNING] Unreliable source '{rec2.owner_raw}'"
                
            field_results.append(f_owner)
            
            f_tm = _get_field_match_info(rec1.trademark_raw, rec1.trademark_norm, rec2.trademark_raw, rec2.trademark_norm, "Trademark")
            field_results.append(f_tm)

            if rec1.class_list and rec2.class_list and rec1.class_list != rec2.class_list:
                match_errors.append(f"Class: {rec1.class_list} != {rec2.class_list}")
                
            for fr in field_results:
                if _field_failure(fr["status"]):
                    match_errors.append(fr["error"])
                
            if not match_errors:
                passed += 1
                # Determine top status
                status_priority = ["EXACT", "NORMALIZED", "SUBSTRING", "SEMANTIC_NEAR", "MISSING_BOTH", "SKIPPED_OPTIONAL", "OWNER_WARNING"]
                current_top = "EXACT"
                for fr in field_results:
                    if fr["status"] in status_priority:
                        if status_priority.index(fr["status"]) > status_priority.index(current_top):
                            current_top = fr["status"]
                
                report_lines.append(f"{_field_status_to_record_status(current_top)}: {rec_id} (Mark: {rec2.trademark_raw})")
                for fr in field_results:
                    if fr.get("info"):
                        report_lines.append(f"  - {fr['info']}")
            else:
                failures.append(f"{rec_id}: " + " | ".join(match_errors))
                report_lines.append(f"FAIL/PARTIAL: {rec_id}")
                for err in match_errors: report_lines.append(f"  - {err}")
        else:
            reason = f"No match found for Mark: '{rec2.trademark_raw}' and Owner: '{rec2.owner_raw}'"
            failures.append(f"{rec_id}: {reason}")
            report_lines.append(f"FAIL: {rec_id} - {reason}")

    return CategoryComparisonResult("WEB_COMMON_LAW", passed, len(json2_records), failures, report_lines)


def compare_business_name(json1_records: List[NormalizedRecord], 
                          json2_records: List[NormalizedRecord]) -> CategoryComparisonResult:
    """
    Comparator for BUSINESS_NAME. 
    Tiered search: TM+Owner -> TM+Jurisdiction/State -> Owner+SIC -> SIC.
    """
    maps = {
        "tm_owner": {},
        "tm_jurisdiction": {},
        "owner_sic": {},
        "sic": {}
    }
    for r in json1_records:
        if r.trademark_norm and r.owner_norm:
            key = f"{r.trademark_norm}|{r.owner_norm}"
            if key not in maps["tm_owner"]: maps["tm_owner"][key] = []
            maps["tm_owner"][key].append(r)
        jurisdiction_norm = _record_jurisdiction_norm(r)
        if r.trademark_norm and jurisdiction_norm:
            key = f"{r.trademark_norm}|{jurisdiction_norm}"
            if key not in maps["tm_jurisdiction"]: maps["tm_jurisdiction"][key] = []
            maps["tm_jurisdiction"][key].append(r)
        if r.owner_norm and r.primary_sic:
            key = f"{r.owner_norm}|{r.primary_sic}"
            if key not in maps["owner_sic"]: maps["owner_sic"][key] = []
            maps["owner_sic"][key].append(r)
        if r.primary_sic:
            if r.primary_sic not in maps["sic"]: maps["sic"][r.primary_sic] = []
            maps["sic"][r.primary_sic].append(r)
    
    passed = 0
    total = len(json2_records)
    failures = []
    report_lines = ["CATEGORY: BUSINESS_NAME GATE 2 REPORT", "="*40]

    for rec2 in json2_records:
        rec_id = rec2.record_id
        
        sic_only_candidates = maps["sic"].get(rec2.primary_sic, []) if rec2.primary_sic else []
        if len(_dedupe_candidates(sic_only_candidates)) == 1:
            sic_candidate = _dedupe_candidates(sic_only_candidates)[0]
            if rec2.trademark_norm and sic_candidate.trademark_norm and sic_candidate.trademark_norm != rec2.trademark_norm:
                sic_only_candidates = []

        jurisdiction_norm = _record_jurisdiction_norm(rec2)
        tiers = [
            ("Trademark + Owner", maps["tm_owner"].get(f"{rec2.trademark_norm}|{rec2.owner_norm}", []) if rec2.trademark_norm and rec2.owner_norm else []),
            ("Trademark + Jurisdiction/State", maps["tm_jurisdiction"].get(f"{rec2.trademark_norm}|{jurisdiction_norm}", []) if rec2.trademark_norm and jurisdiction_norm else []),
            ("Owner + SIC", maps["owner_sic"].get(f"{rec2.owner_norm}|{rec2.primary_sic}", []) if rec2.owner_norm and rec2.primary_sic else []),
            ("SIC", sic_only_candidates),
        ]
        rec1, is_ambiguous, diagnostics, _ = _select_candidate_from_tiers(rec2, tiers, "BUSINESS_NAME")
        
        if is_ambiguous:
            failures.append(f"{rec_id}: AMBIGUOUS MATCH - Multiple JSON1 candidates found.")
            report_lines.append(f"FAIL: {rec_id} - Ambiguous candidates")
            report_lines.extend([f"  {line}" for line in diagnostics])
            continue

        if rec1:
            match_errors = []
            field_results = []
            
            f_owner = _get_field_match_info(rec1.owner_raw, rec1.owner_norm, rec2.owner_raw, rec2.owner_norm, "Owner")
            field_results.append(f_owner)
            
            f_goods = _get_field_match_info(rec1.goods_raw, rec1.goods_norm, rec2.goods_raw, rec2.goods_norm, "Goods")
            field_results.append(f_goods)
            
            f_tm = _get_field_match_info(rec1.trademark_raw, rec1.trademark_norm, rec2.trademark_raw, rec2.trademark_norm, "Trademark")
            field_results.append(f_tm)

            if rec1.class_list and rec2.class_list and rec1.class_list != rec2.class_list:
                match_errors.append(f"Class: {rec1.class_list} != {rec2.class_list}")
                
            for fr in field_results:
                if _field_failure(fr["status"]):
                    match_errors.append(fr["error"])
                
            if not match_errors:
                passed += 1
                status = _record_status_from_field_results(field_results)
                report_lines.append(f"{status}: {rec_id} (Mark: {rec2.trademark_raw})")
                _append_field_result_info(report_lines, field_results)
            else:
                failures.append(f"{rec_id}: " + " | ".join(match_errors))
                report_lines.append(f"FAIL/PARTIAL: {rec_id}")
                for err in match_errors: report_lines.append(f"  - {err}")
        else:
            failures.append(f"{rec_id}: No matching JSON1 record found for '{rec2.trademark_raw}' / SIC: '{rec2.primary_sic}'")
            report_lines.append(f"FAIL: {rec_id} - No matching record found")

    return CategoryComparisonResult("BUSINESS_NAME", passed, total, failures, report_lines)

def compare_uspto_marks(json1_records: List[NormalizedRecord], 
                        json2_records: List[NormalizedRecord]) -> CategoryComparisonResult:
    """
    Comparator for USPTO_MARKS (Pattern-6 / Corsearch).
    Mandatory Two-Layer Anchor Matching:
    - PASS: Both Reg and Serial match.
    - PASS WITH WARNING: Either Reg or Serial matches (but not both).
    - FAIL: Neither matches.
    Layer-1: Exact Match. Layer-2: Normalized Match (if L1 doesn't yield a PASS/WARNING).
    """
    passed = 0
    failures = []
    report_lines = ["CATEGORY: USPTO_MARKS GATE 2 REPORT", "="*40]

    for rec2 in json2_records:
        rec_id = rec2.record_id
        reg2_raw = str(rec2.raw_payload.get("Registration_Number") or "").strip()
        ser2_raw = str(rec2.raw_payload.get("Serial_Number") or "").strip()
        reg2_norm = clean_registration_number(reg2_raw)
        ser2_norm = clean_registration_number(ser2_raw)

        best_rec1 = None
        best_match_type = None # "LAYER1" or "LAYER2"
        best_outcome = "FAIL" # "PASS", "PASS_WITH_WARNING", "FAIL"
        best_reg_match = False
        best_ser_match = False

        # Layer 1: Exact
        for r1 in json1_records:
            reg1_raw = str(r1.raw_payload.get("registration_number") or "").strip()
            ser1_raw = str(r1.raw_payload.get("serial_number") or "").strip()
            
            rm = (reg1_raw == reg2_raw)
            sm = (ser1_raw == ser2_raw)
            
            if rm and sm:
                best_rec1, best_match_type, best_outcome, best_reg_match, best_ser_match = r1, "LAYER1", "PASS", True, True
                break
            elif rm or sm:
                if best_outcome != "PASS": # Prioritize full match if multiple candidates existed (unlikely for USPTO)
                    best_rec1, best_match_type, best_outcome, best_reg_match, best_ser_match = r1, "LAYER1", "PASS_WITH_WARNING", rm, sm
        
        # Layer 2: Normalized (Only if L1 didn't yield a match)
        if best_outcome == "FAIL":
            for r1 in json1_records:
                reg1_norm = clean_registration_number(r1.raw_payload.get("registration_number"))
                ser1_norm = clean_registration_number(r1.raw_payload.get("serial_number"))
                
                rm_n = (reg1_norm == reg2_norm)
                sm_n = (ser1_norm == ser2_norm)
                
                if rm_n and sm_n:
                    best_rec1, best_match_type, best_outcome, best_reg_match, best_ser_match = r1, "LAYER2", "PASS", True, True
                    break
                elif rm_n or sm_n:
                    if best_outcome == "FAIL":
                        best_rec1, best_match_type, best_outcome, best_reg_match, best_ser_match = r1, "LAYER2", "PASS_WITH_WARNING", rm_n, sm_n

        # Report Construction
        report_lines.append(f"Record: {rec_id}")
        report_lines.append("Anchor Comparison")
        report_lines.append(f"Registration Number : {'MATCH' if best_reg_match else 'MISMATCH'}")
        report_lines.append(f"Serial Number : {'MATCH' if best_ser_match else 'MISMATCH'}")
        
        status_label = "FAIL"
        if best_outcome == "PASS":
            status_label = f"PASS ({best_match_type} Exact)" if best_match_type == "LAYER1" else f"PASS ({best_match_type} Normalized)"
        elif best_outcome == "PASS_WITH_WARNING":
            status_label = "PASS WITH WARNING"
            
        report_lines.append(f"Anchor Status : {status_label}")
        
        if best_outcome == "PASS_WITH_WARNING":
            reason = ""
            if best_reg_match:
                reason = "Registration Number matched. Serial Number differs between JSON-1 and JSON-2."
            else:
                reason = "Serial Number matched. Registration Number differs between JSON-1 and JSON-2."
            report_lines.append("Reason:")
            report_lines.append(reason)
        elif best_outcome == "FAIL":
            report_lines.append("Reason:")
            report_lines.append("Neither identifier matches. Unable to identify the corresponding USPTO record.")
            
        report_lines.append(f"Layer-2: {'SKIPPED' if best_match_type == 'LAYER1' else 'EXECUTED'}")

        if best_outcome == "FAIL":
            failures.append(f"{rec_id}: No anchor match (Reg: {reg2_raw}, Serial: {ser2_raw})")
            report_lines.append("Overall Result: FAIL")
            report_lines.append("-" * 20)
            continue

        # Field Comparison
        match_errors = []
        rec1 = best_rec1
        
        # Owner
        f_owner = _get_field_match_info(rec1.owner_raw, rec1.owner_norm, rec2.owner_raw, rec2.owner_norm, "Owner")
        report_lines.append(f"Owner: {f_owner['status']}")
        if _field_failure(f_owner["status"]):
            match_errors.append(f_owner["error"])
        elif f_owner.get("info"):
            report_lines.append(f"  - {f_owner['info']}")
            
        f_goods = _get_field_match_info(rec1.goods_raw, rec1.goods_norm, rec2.goods_raw, rec2.goods_norm, "Goods")
        report_lines.append(f"Goods: {f_goods['status']}")
        if _field_failure(f_goods["status"]):
            match_errors.append(f_goods['error'])
        elif f_goods.get("info"):
            report_lines.append(f"  - {f_goods['info']}")
            
        class_match = rec1.class_list == rec2.class_list
        c_status = "PASS" if class_match else "FAIL"
        report_lines.append(f"Class: {c_status}")
        if not class_match:
            match_errors.append(f"Class: {rec1.class_list} != {rec2.class_list}")

        if not match_errors:
            passed += 1 # Count PASS and PASS_WITH_WARNING (if match_errors is empty) as success
            report_lines.append("Overall Result: PASS")
        else:
            failures.append(f"{rec_id}: " + " | ".join(match_errors))
            report_lines.append("Overall Result: FAIL")
            for err in match_errors: report_lines.append(f"  - {err}")
            
        report_lines.append("-" * 20)

    return CategoryComparisonResult("USPTO_MARKS", passed, len(json2_records), failures, report_lines)

def compare_web_domain(json1_records: List[NormalizedRecord], 
                       json2_records: List[NormalizedRecord]) -> CategoryComparisonResult:
    """
    Comparator for WEB_DOMAIN. Implements a 5-tier candidate selection architecture.
    Tier 1: Domain / URL
    Tier 2: Domain + Trademark
    Tier 3: Trademark + Owner
    Tier 4: Trademark + Goods
    Tier 5: Trademark only
    """
    # 1. Build Tiers of Maps for JSON 1
    m1_domain_norm = {}
    m1_url_norm = {}
    m2_domain_tm_norm = {}
    m2_url_tm_norm = {}
    m3_tm_owner_raw = {}
    m3_tm_owner_norm = {}
    m4_tm_goods_raw = {}
    m4_tm_goods_norm = {}
    m5_tm_raw = {}
    m5_tm_norm = {}

    def add_to_map(m, key, record):
        if not key: return
        if key not in m: m[key] = []
        m[key].append(record)

    for r in json1_records:
        add_to_map(m1_domain_norm, r.domain_norm, r)
        add_to_map(m1_url_norm, r.url_norm, r)
        if r.domain_norm and r.trademark_norm:
            add_to_map(m2_domain_tm_norm, f"{r.domain_norm}|{r.trademark_norm}", r)
        if r.url_norm and r.trademark_norm:
            add_to_map(m2_url_tm_norm, f"{r.url_norm}|{r.trademark_norm}", r)
        if r.trademark_raw and r.owner_raw:
            add_to_map(m3_tm_owner_raw, f"{r.trademark_raw}|{r.owner_raw}", r)
        if r.trademark_norm and r.owner_norm:
            add_to_map(m3_tm_owner_norm, f"{r.trademark_norm}|{r.owner_norm}", r)
        if r.trademark_raw and r.goods_raw:
            add_to_map(m4_tm_goods_raw, f"{r.trademark_raw}|{r.goods_raw}", r)
        if r.trademark_norm and r.goods_norm:
            add_to_map(m4_tm_goods_norm, f"{r.trademark_norm}|{r.goods_norm}", r)
        add_to_map(m5_tm_raw, r.trademark_raw, r)
        add_to_map(m5_tm_norm, r.trademark_norm, r)

    passed = 0
    total_effective = 0
    total_skipped = 0
    total_extracted = len(json2_records)
    failures = []
    report_lines = []

    for rec2 in json2_records:
        if rec2.skip_from_gate2:
            total_skipped += 1
            continue
            
        total_effective += 1
        rec_id = rec2.record_id
        
        domain_url_candidates = []
        if rec2.domain_norm:
            domain_url_candidates.extend(m1_domain_norm.get(rec2.domain_norm, []))
        if rec2.url_norm:
            domain_url_candidates.extend(m1_url_norm.get(rec2.url_norm, []))

        domain_tm_candidates = []
        if rec2.domain_norm and rec2.trademark_norm:
            domain_tm_candidates.extend(m2_domain_tm_norm.get(f"{rec2.domain_norm}|{rec2.trademark_norm}", []))
        if rec2.url_norm and rec2.trademark_norm:
            domain_tm_candidates.extend(m2_url_tm_norm.get(f"{rec2.url_norm}|{rec2.trademark_norm}", []))

        rec1 = None
        is_ambiguous = False
        diagnostics = []
        unique_domain_url = _dedupe_candidates(domain_url_candidates)
        if unique_domain_url:
            if len(unique_domain_url) == 1:
                rec1 = unique_domain_url[0]
            else:
                unique_domain_tm = _dedupe_candidates(domain_tm_candidates)
                if len(unique_domain_tm) == 1:
                    rec1 = unique_domain_tm[0]
                else:
                    is_ambiguous = True
                    diagnostics = _format_ambiguity_diagnostics(
                        rec2,
                        unique_domain_tm or unique_domain_url,
                        "WEB_DOMAIN",
                        "Domain + Trademark",
                        "Domain/URL matched multiple candidates and Domain + Trademark did not identify exactly one record."
                    )
        else:
            tiers = [
                ("Domain + Trademark", domain_tm_candidates),
                ("Trademark + Owner", (m3_tm_owner_raw.get(f"{rec2.trademark_raw}|{rec2.owner_raw}") or m3_tm_owner_norm.get(f"{rec2.trademark_norm}|{rec2.owner_norm}") or []) if rec2.trademark_norm and rec2.owner_norm else []),
                ("Trademark + Goods", (m4_tm_goods_raw.get(f"{rec2.trademark_raw}|{rec2.goods_raw}") or m4_tm_goods_norm.get(f"{rec2.trademark_norm}|{rec2.goods_norm}") or []) if rec2.trademark_norm and rec2.goods_norm else []),
                ("Trademark", (m5_tm_raw.get(rec2.trademark_raw) or m5_tm_norm.get(rec2.trademark_norm) or []) if rec2.trademark_norm else []),
            ]
            rec1, is_ambiguous, diagnostics, _ = _select_candidate_from_tiers(rec2, tiers, "WEB_DOMAIN")
        
        if is_ambiguous:
            failures.append(f"{rec_id} (TM: {rec2.trademark_raw}): AMBIGUOUS MATCH - Multiple JSON1 candidates found.")
            report_lines.append(f"FAIL: {rec_id} - Ambiguous candidates")
            report_lines.extend([f"  {line}" for line in diagnostics])
            continue

        if rec1:
            match_errors = []
            field_results = []
            
            f_owner = _get_field_match_info(rec1.owner_raw, rec1.owner_norm, rec2.owner_raw, rec2.owner_norm, "Owner")
            field_results.append(f_owner)
            
            f_goods = _get_field_match_info(rec1.goods_raw, rec1.goods_norm, rec2.goods_raw, rec2.goods_norm, "Goods")
            field_results.append(f_goods)
            
            f_tm = _get_field_match_info(rec1.trademark_raw, rec1.trademark_norm, rec2.trademark_raw, rec2.trademark_norm, "Trademark")
            field_results.append(f_tm)

            if rec1.class_list and rec2.class_list and rec1.class_list != rec2.class_list:
                match_errors.append(f"Class: {rec1.class_list} != {rec2.class_list}")
                
            for fr in field_results:
                if _field_failure(fr["status"]):
                    match_errors.append(fr["error"])
                
            if not match_errors:
                passed += 1
                # Status priority logic similar to WEB_COMMON_LAW
                status_priority = ["EXACT", "NORMALIZED", "SUBSTRING", "SEMANTIC_NEAR", "MISSING_BOTH", "SKIPPED_OPTIONAL", "OWNER_WARNING"]
                current_top = "EXACT"
                for fr in field_results:
                    if fr["status"] in status_priority:
                        if status_priority.index(fr["status"]) > status_priority.index(current_top):
                            current_top = fr["status"]
                
                report_lines.append(f"{_field_status_to_record_status(current_top)}: {rec_id} (TM: {rec2.trademark_raw})")
                for fr in field_results:
                    if fr.get("info"):
                        report_lines.append(f"  - {fr['info']}")
            else:
                failures.append(f"{rec_id} (TM: {rec2.trademark_raw}): " + " | ".join(match_errors))
                report_lines.append(f"FAIL/PARTIAL: {rec_id}")
                for err in match_errors: report_lines.append(f"  - {err}")
        else:
            failures.append(f"{rec_id}: No domain match found for '{rec2.trademark_raw}' / '{rec2.owner_raw}'")
            report_lines.append(f"FAIL: {rec_id} - No match found for record")

    # Final summary assembly
    final_summary = [
        "CATEGORY: WEB_DOMAIN GATE 2 REPORT",
        "="*40,
        f"Total extracted records : {total_extracted}",
        f"Skipped (rule_filter)   : {total_skipped}",
        f"Effective compared      : {total_effective}",
        f"Passed                  : {passed}",
        f"Failed                  : {len(failures)}",
        "="*40
    ]
    full_report_lines = final_summary + report_lines

    return CategoryComparisonResult("WEB_DOMAIN", passed, total_effective, failures, full_report_lines,
                                    skipped=total_skipped, total_extracted=total_extracted)



def normalize_class_list(val):
    """
    Normalizes class list representations into a sorted tuple of integers.
    Handles list of ints: [29, 30]
    Handles string JSON array: '["001", "029"]'
    """
    if val is None:
        return ()
    
    if isinstance(val, (int, float)):
        return (int(val),)
    
    if isinstance(val, str):
        try:
            # Try parsing as JSON first
            parsed = json.loads(val)
            if isinstance(parsed, list):
                val = parsed
            elif isinstance(parsed, (int, float)):
                return (int(parsed),)
            else:
                val = [v.strip() for v in str(val).split(",") if v.strip()]
        except (json.JSONDecodeError, AttributeError):
            # Fallback to simple split
            val = [v.strip() for v in str(val).split(",") if v.strip()]
            
    if isinstance(val, list):
        result = []
        for item in val:
            try:
                # Remove leading zeros and convert to int
                result.append(int(str(item).lstrip('0') or '0'))
            except (ValueError, TypeError):
                continue
        return tuple(sorted(list(set(result))))
        
    return ()


def extract_json1_records(data1) -> List[NormalizedRecord]:
    """
    Parses JSON 1 into canonical NormalizedRecord objects.
    """
    if not isinstance(data1, list):
        raise ValueError("Critical Error: JSON1 payload must be a list of records.")

    records = []
    for block in data1:
        if not isinstance(block, dict):
            continue
        source_type = block.get("source_type")
        category = CATEGORY_MAP.get(source_type)
        if not category:
            continue

        rec = NormalizedRecord(
            category=category,
            source_side="json1",
            owner_raw=str(block.get("owner", "")),
            owner_norm=normalize_owner(block.get("owner", "")),
            trademark_raw=str(block.get("trademark", "")),
            trademark_norm=normalize_mark_text(block.get("trademark", "")),
            goods_raw=str(block.get("goods_services", "")),
            goods_norm=normalize_goods_services(block.get("goods_services", "")),
            domain_raw=_extract_domain_raw(block),
            domain_norm=normalize_domain_value(_extract_domain_raw(block) or _extract_url_raw(block)),
            url_raw=_extract_url_raw(block),
            url_norm=normalize_url_value(_extract_url_raw(block)),
            class_list=normalize_class_list(block.get("class_list")),
            registration_number=clean_registration_number(block.get("registration_number")),
            primary_sic=str(block.get("primary_sic", "")).strip().upper() if block.get("primary_sic") else None,
            raw_payload=block
        )
        records.append(rec)
    return records

def group_records_by_category(records: List[NormalizedRecord]) -> Dict[str, List[NormalizedRecord]]:
    """
    Groups canonical records into category buckets.
    """
    grouped = {}
    for rec in records:
        if rec.category not in grouped:
            grouped[rec.category] = []
        grouped[rec.category].append(rec)
    return grouped

def _extract_json2_state_marks(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    """
    Extracts state mark records from 'state_summary_data'.
    Handles multiple JSON variants (CompuMark, Clarivate).
    """
    records = []
    items = data2.get("state_summary_data")
    if items and isinstance(items, list):
        for item in items:
            # Anchor detection: must have one of these to be counted
            r_id = item.get("us_identifier") or item.get("ST") or item.get("serialnum")
            if not r_id:
                continue
                
            # Perform clean mapping
            clean_payload = {k: v for k, v in item.items() if k not in ["Image_Base64", "state_image_path"]}
            
            records.append(NormalizedRecord(
                category="STATE_MARKS",
                source_side="json2",
                record_id=str(r_id),
                registration_number=clean_registration_number(item.get("registration_no")),
                owner_raw=str(item.get("owner_name", "")),
                owner_norm=normalize_owner(item.get("owner_name", "")),
                goods_raw=str(item.get("goods_services_description", "")),
                goods_norm=normalize_goods_services(item.get("goods_services_description", "")),
                trademark_raw=str(item.get("mark_text", "")),
                trademark_norm=normalize_mark_text(item.get("mark_text", "")),
                domain_raw=_extract_domain_raw(clean_payload),
                domain_norm=normalize_domain_value(_extract_domain_raw(clean_payload) or _extract_url_raw(clean_payload)),
                url_raw=_extract_url_raw(clean_payload),
                url_norm=normalize_url_value(_extract_url_raw(clean_payload)),
                class_list=normalize_class_list(item.get("intl_class")),
                raw_payload=clean_payload
            ))
    return records

def _extract_json2_common_law(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    if _is_web_common_law_records_variant(data2):
        return []
    records = []
    items = data2.get("records")
    if items and isinstance(items, list):
        return_type = str(data2.get("return_type", "")).lower()
        section = data2.get("section", "")
        vendor = data2.get("vendor_name", "")

        # Identify if this section is WEB or standard CL
        common_law_keys = {"COL", "owner_name", "goods_services", "mark_text", "nice_class"}
        is_wrapperless_common_law = any(common_law_keys.issubset(set(item.keys())) for item in items if isinstance(item, dict))
        is_web = ("web_results" in section) or (vendor == "CompuMark" and "Web_start_page" in data2)
        
        for item in items:
            # Pattern 4 check: skip if it's actually a domain record sitting in 'records'
            if "dnn" in item or "bsn" in item:
                continue
                
            cat = "COMMON_LAW" if is_wrapperless_common_law else ("WEB_COMMON_LAW" if is_web else "COMMON_LAW")
            r_id = item.get("Doc No.") or item.get("COL") or item.get("web") or item.get("record_number") or "Unknown"
            
            records.append(NormalizedRecord(
                category=cat,
                source_side="json2",
                vendor_name=vendor,
                record_id=str(r_id),
                owner_raw=str(item.get("owner_name", "")),
                owner_norm=normalize_owner(item.get("owner_name", "")),
                goods_raw=str(item.get("goods_services", "")),
                goods_norm=normalize_goods_services(item.get("goods_services", "")),
                trademark_raw=str(item.get("mark_text", "")),
                trademark_norm=normalize_mark_text(item.get("mark_text", "")),
                domain_raw=_extract_domain_raw(item),
                domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
                url_raw=_extract_url_raw(item),
                url_norm=normalize_url_value(_extract_url_raw(item)),
                class_list=normalize_class_list(item.get("nice_class")),
                raw_payload=item
            ))
    return records

def _is_web_common_law_records_variant(data2: Any) -> bool:
    """
    Identifies the new Pattern-3 (WEB_COMMON_LAW) JSON variant:
    - root object (data2) is a dict containing "records"
    - "records" is a list
    - each dict in "records" contains: "Url" (or "URL"), "Page Title" (or "Web Page Title"), "mark_text", "owner_name"
    """
    if not isinstance(data2, dict):
        return False
    items = data2.get("records")
    if not isinstance(items, list) or len(items) == 0:
        return False
    
    dict_items = [itm for itm in items if isinstance(itm, dict)]
    if not dict_items:
        return False
        
    for itm in dict_items:
        keys = set(itm.keys())
        has_mark = "mark_text" in keys
        has_owner = "owner_name" in keys
        has_url = "Url" in keys or "URL" in keys
        has_title = "Page Title" in keys or "Web Page Title" in keys
        if not (has_mark and has_owner and has_url and has_title):
            return False
            
    return True

def _extract_domain_from_url(url: str) -> str:
    if not url:
        return ""
    domain = re.sub(r'^[a-zA-Z]+://', '', url)
    domain = domain.split('/')[0].split('?')[0].split('#')[0]
    return domain

def _extract_json2_web_common_law_records_variant(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    if not _is_web_common_law_records_variant(data2):
        return []
    
    records = []
    items = data2.get("records", [])
    for item in items:
        if not isinstance(item, dict):
            continue
            
        url_raw = str(item.get("Url") or item.get("URL") or "").strip()
        domain_raw = _extract_domain_from_url(url_raw)
        raw_payload = {k: v for k, v in item.items() if "image" not in k.lower()}
        nice_class = item.get("nice_class")
        class_list = normalize_class_list(nice_class)
        
        trademark_raw = str(item.get("mark_text", ""))
        owner_raw = str(item.get("owner_name", ""))
        goods_raw = str(item.get("goods_services", ""))
        
        records.append(NormalizedRecord(
            category="WEB_COMMON_LAW",
            source_side="json2",
            record_id="Unknown",
            owner_raw=owner_raw,
            owner_norm=normalize_owner(owner_raw),
            trademark_raw=trademark_raw,
            trademark_norm=normalize_mark_text(trademark_raw),
            goods_raw=goods_raw,
            goods_norm=normalize_goods_services(goods_raw),
            domain_raw=domain_raw,
            domain_norm=normalize_domain_value(domain_raw or url_raw),
            url_raw=url_raw,
            url_norm=normalize_url_value(url_raw),
            class_list=class_list,
            raw_payload=raw_payload
        ))
    return records

def _extract_json2_business_names(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    records = []
    items = data2.get("business_records")
    if items and isinstance(items, list):
        for item in items:
            records.append(NormalizedRecord(
                category="BUSINESS_NAME",
                source_side="json2",
                record_id=str(item.get("bsn", "Unknown")),
                primary_sic=str(item.get("primary_sic", "")).strip().upper(),
                owner_raw=str(item.get("owner_name", "")),
                owner_norm=normalize_owner(item.get("owner_name", "")),
                goods_raw=str(item.get("Goods/Services", "")),
                goods_norm=normalize_goods_services(item.get("Goods/Services", "")),
                trademark_raw=str(item.get("cited_mark", "")),
                trademark_norm=normalize_mark_text(item.get("cited_mark", "")),
                domain_raw=_extract_domain_raw(item),
                domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
                url_raw=_extract_url_raw(item),
                url_norm=normalize_url_value(_extract_url_raw(item)),
                class_list=normalize_class_list(item.get("final_nice_class") or item.get("nice_class")),
                raw_payload=item
            ))
    return records

def _extract_json2_clarivate_web_common_law(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    """
    Extends Pattern 3 support for Clarivate 'web_common_law_overview_data' variant.
    Maps to WEB_COMMON_LAW category.
    """
    records = []
    items = data2.get("web_common_law_overview_data", [])
    if not isinstance(items, list): return records
    
    for item in items:
        records.append(NormalizedRecord(
            category="WEB_COMMON_LAW",
            source_side="json2",
            record_id=str(item.get("Record Nr.", "Unknown")),
            primary_sic="",
            owner_raw="",
            owner_norm="",
            goods_raw="",
            goods_norm="",
            trademark_raw=str(item.get("Web Page Title", "")),
            trademark_norm=normalize_mark_text(item.get("Web Page Title", "")),
            domain_raw=_extract_domain_raw(item),
            domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
            url_raw=_extract_url_raw(item),
            url_norm=normalize_url_value(_extract_url_raw(item)),
            class_list=tuple(),
            raw_payload={k: v for k, v in item.items() if "image" not in k.lower()}
        ))
    return records

def _extract_json2_clarivate_common_law(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    """
    Extends Pattern 2 support for Clarivate 'common_law_database_overview_data' variant.
    Maps to COMMON_LAW category.
    """
    records = []
    outer = data2.get("common_law_database_overview_data", {})
    if not isinstance(outer, dict): return records
    
    # Process both pools
    pool_identical = outer.get("Identical Names", [])
    pool_similar = outer.get("Similar Names", [])
    
    all_items = []
    if isinstance(pool_identical, list): all_items.extend(pool_identical)
    if isinstance(pool_similar, list): all_items.extend(pool_similar)
    
    for item in all_items:
        r_id = item.get("Nr.") or item.get("COL") or "Unknown"
        
        records.append(NormalizedRecord(
            category="COMMON_LAW",
            source_side="json2",
            record_id=str(r_id),
            owner_raw=str(item.get("owner_name", "")),
            owner_norm=normalize_owner(item.get("owner_name", "")),
            goods_raw=str(item.get("goods_services", "")),
            goods_norm=normalize_goods_services(item.get("goods_services", "")),
            trademark_raw=str(item.get("mark_text", "")),
            trademark_norm=normalize_mark_text(item.get("mark_text", "")),
            domain_raw=_extract_domain_raw(item),
            domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
            url_raw=_extract_url_raw(item),
            url_norm=normalize_url_value(_extract_url_raw(item)),
            class_list=normalize_class_list(item.get("nice_class")),
            raw_payload=item
        ))
    return records

def _extract_json2_clarivate_business_names(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    """
    Extends Pattern 4 support for Clarivate 'business_names_overview_data' variant.
    """
    records = []
    outer = data2.get("business_names_overview_data", {})
    if not isinstance(outer, dict): return records
    
    # Process both pools
    pool_identical = outer.get("Identical Names", [])
    pool_similar = outer.get("Similar Names", [])
    
    all_items = []
    if isinstance(pool_identical, list): all_items.extend(pool_identical)
    if isinstance(pool_similar, list): all_items.extend(pool_similar)
    
    for item in all_items:
        records.append(NormalizedRecord(
            category="BUSINESS_NAME",
            source_side="json2",
            record_id=str(item.get("BUS") or item.get("Nr.", "Unknown")),
            primary_sic=str(item.get("SIC Code", "")).strip().upper(),
            owner_raw=str(item.get("owner_name", "")),
            owner_norm=normalize_owner(item.get("owner_name", "")),
            goods_raw=str(item.get("Goods/Services", "")),
            goods_norm=normalize_goods_services(item.get("Goods/Services", "")),
            trademark_raw=str(item.get("mark_text", "")),
            trademark_norm=normalize_mark_text(item.get("mark_text", "")),
            domain_raw=_extract_domain_raw(item),
            domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
            url_raw=_extract_url_raw(item),
            url_norm=normalize_url_value(_extract_url_raw(item)),
            class_list=normalize_class_list(item.get("final_nice_class") or item.get("nice_class")),
            raw_payload=item
        ))
    return records

def _extract_json2_business_names_variant(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    """
    Extends Pattern 4 support for 'business_names_data' variant.
    """
    records = []
    items = data2.get("business_names_data")
    if items and isinstance(items, list):
        for item in items:
            records.append(NormalizedRecord(
                category="BUSINESS_NAME",
                source_side="json2",
                record_id=str(item.get("BUS", "Unknown")),
                primary_sic=str(item.get("SIC Code", "")).strip().upper(),
                owner_raw=str(item.get("owner_name", "")),
                owner_norm=normalize_owner(item.get("owner_name", "")),
                goods_raw=str(item.get("Goods/Services", "")),
                goods_norm=normalize_goods_services(item.get("Goods/Services", "")),
                trademark_raw=str(item.get("mark_text", "")),
                trademark_norm=normalize_mark_text(item.get("mark_text", "")),
                domain_raw=_extract_domain_raw(item),
                domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
                url_raw=_extract_url_raw(item),
                url_norm=normalize_url_value(_extract_url_raw(item)),
                class_list=normalize_class_list(item.get("final_nice_class") or item.get("nice_class")),
                raw_payload=item
            ))
    return records

def _extract_json2_business_names_root_list(data2: List[Dict[str, Any]]) -> List[NormalizedRecord]:
    """
    Extends Pattern 4 support for JSON2 payloads whose root is directly a list.
    """
    records = []
    if not data2 or not all(isinstance(item, dict) for item in data2):
        return records

    bsn_business_keys = {"bsn", "primary_sic", "Goods/Services", "owner_name"}
    bus_business_keys = {"BUS", "SIC Code", "Goods/Services", "owner_name"}
    sic_mark_business_keys = {"owner_name", "mark_text", "Goods/Services", "SIC Code"}
    if not any(
        bsn_business_keys.issubset(set(item.keys()))
        or bus_business_keys.issubset(set(item.keys()))
        or sic_mark_business_keys.issubset(set(item.keys()))
        for item in data2
    ):
        return records

    for item in data2:
        records.append(NormalizedRecord(
            category="BUSINESS_NAME",
            source_side="json2",
            record_id=str(item.get("bsn") or item.get("BUS", "Unknown")),
            primary_sic=str(item.get("primary_sic") or item.get("SIC Code", "")).strip().upper(),
            owner_raw=str(item.get("owner_name", "")),
            owner_norm=normalize_owner(item.get("owner_name", "")),
            goods_raw=str(item.get("Goods/Services", "")),
            goods_norm=normalize_goods_services(item.get("Goods/Services", "")),
            trademark_raw=str(item.get("cited_mark") or item.get("mark_text", "")),
            trademark_norm=normalize_mark_text(item.get("cited_mark") or item.get("mark_text", "")),
            domain_raw=_extract_domain_raw(item),
            domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
            url_raw=_extract_url_raw(item),
            url_norm=normalize_url_value(_extract_url_raw(item)),
            class_list=normalize_class_list(item.get("final_nice_class") or item.get("nice_class")),
            raw_payload=item
        ))
    return records

def _extract_json2_web_domains_root_list(data2: List[Dict[str, Any]]) -> List[NormalizedRecord]:
    """
    Extends Pattern 5 support for JSON2 payloads whose root is directly a list.
    """
    records = []
    if not data2 or not all(isinstance(item, dict) for item in data2):
        return records

    domain_keys = {"dnn", "domain_name", "owner_nameD", "mark_text"}
    mark_domain_keys = {"mark_text", "owner_nameD", "goods_services", "Web Page Information"}
    if not any(
        domain_keys.issubset(set(item.keys())) or mark_domain_keys.issubset(set(item.keys()))
        for item in data2
    ):
        return records

    for item in data2:
        is_rule_filter = item.get("goods_services_source") == "rule_filter"
        goods_value = item.get("goods_services", "")
        if isinstance(goods_value, list):
            goods_value = "; ".join(str(v) for v in goods_value)
        domain_raw = _extract_domain_raw(item) or str(item.get("mark_text", ""))
        records.append(NormalizedRecord(
            category="WEB_DOMAIN",
            source_side="json2",
            record_id=str(item.get("dnn", "Unknown")),
            owner_raw=str(item.get("owner_nameD", "")),
            owner_norm=normalize_owner(item.get("owner_nameD", "")),
            trademark_raw=str(item.get("mark_text", "")),
            trademark_norm=normalize_mark_text(item.get("mark_text", "")),
            goods_raw=str(goods_value),
            goods_norm=normalize_goods_services(goods_value),
            domain_raw=domain_raw,
            domain_norm=normalize_domain_value(domain_raw or _extract_url_raw(item)),
            url_raw=_extract_url_raw(item),
            url_norm=normalize_url_value(_extract_url_raw(item)),
            class_list=normalize_class_list(item.get("nice_class")),
            skip_from_gate2=is_rule_filter,
            raw_payload=item
        ))
    return records

def _extract_json2_web_domains(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    records = []
    items = data2.get("records")
    # Domains only exist in Pattern 4 which also has business_records
    if items and isinstance(items, list) and "business_records" in data2:
        for item in items:
            if "dnn" in item:
                is_rule_filter = item.get("goods_services_source") == "rule_filter"
                records.append(NormalizedRecord(
                    category="WEB_DOMAIN",
                    source_side="json2",
                    record_id=str(item.get("dnn", "Unknown")),
                    owner_raw=str(item.get("owner_nameD", "")),
                    owner_norm=normalize_owner(item.get("owner_nameD", "")),
                    trademark_raw=str(item.get("mark_text", "")),
                    trademark_norm=normalize_mark_text(item.get("mark_text", "")),
                    goods_raw=str(item.get("goods_services", "")),
                    goods_norm=normalize_goods_services(item.get("goods_services", "")),
                    domain_raw=_extract_domain_raw(item),
                    domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
                    url_raw=_extract_url_raw(item),
                    url_norm=normalize_url_value(_extract_url_raw(item)),
                    class_list=normalize_class_list(item.get("nice_class")),
                    skip_from_gate2=is_rule_filter,
                    raw_payload=item
                ))
    return records

def _extract_json2_web_domains_variant(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    """
    Extends Pattern 5 support for 'domain_names_data' variant.
    """
    records = []
    items = data2.get("domain_names_data")
    if items and isinstance(items, list):
        for item in items:
            records.append(NormalizedRecord(
                category="WEB_DOMAIN",
                source_side="json2",
                record_id=str(item.get("DN", "Unknown")),
                owner_raw=str(item.get("owner_nameD", "")),
                owner_norm=normalize_owner(item.get("owner_nameD", "")),
                trademark_raw=str(item.get("mark_text", "")),
                trademark_norm=normalize_mark_text(item.get("mark_text", "")),
                goods_raw=str(item.get("goods_services", "")),
                goods_norm=normalize_goods_services(item.get("goods_services", "")),
                domain_raw=_extract_domain_raw(item),
                domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
                url_raw=_extract_url_raw(item),
                url_norm=normalize_url_value(_extract_url_raw(item)),
                class_list=normalize_class_list(item.get("nice_class")),
                raw_payload=item
            ))
    return records

def _extract_json2_clarivate_web_domains(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    """
    Extends Pattern 5 support for Clarivate 'Identical Names' and 'Similar Names' variant.
    """
    records = []
    
    # Process both pools
    pool_identical = data2.get("Identical Names", [])
    pool_similar = data2.get("Similar Names", [])
    
    # Combined list for iteration
    all_items = []
    if isinstance(pool_identical, list): all_items.extend(pool_identical)
    if isinstance(pool_similar, list): all_items.extend(pool_similar)
    
    for item in all_items:
        records.append(NormalizedRecord(
            category="WEB_DOMAIN",
            source_side="json2",
            record_id=str(item.get("Nr.", "Unknown")),
            owner_raw=str(item.get("owner_nameD", "")),
            owner_norm=normalize_owner(item.get("owner_nameD", "")),
            trademark_raw=str(item.get("mark_text", "")),
            trademark_norm=normalize_mark_text(item.get("mark_text", "")),
            goods_raw=str(item.get("goods_services", "")),
            goods_norm=normalize_goods_services(item.get("goods_services", "")),
            domain_raw=_extract_domain_raw(item),
            domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
            url_raw=_extract_url_raw(item),
            url_norm=normalize_url_value(_extract_url_raw(item)),
            class_list=normalize_class_list(item.get("nice_class")),
            raw_payload=item
        ))
    return records

def _extract_json2_federal_citations(data2: Dict[str, Any]) -> List[NormalizedRecord]:
    """
    Extends Pattern-6 support for 'corsearch' federal citations.
    Only counts records where DocID starts with 'UF-'.
    Maps to USPTO_MARKS category.
    """
    records = []
    results = data2.get("results", {})
    corsearch = results.get("corsearch", {})
    items = corsearch.get("Federal_Citations", [])
    
    if not isinstance(items, list): return records
    
    for item in items:
        doc_id = str(item.get("DocID", ""))
        # Core Requirement: Only count UF- records for Gate-1
        if doc_id.startswith("UF-"):
            # Specialized Goods extraction: extract 'Description' from the nested Goods_Services object
            gs_obj = item.get("Goods_Services", {})
            goods_desc = ""
            if isinstance(gs_obj, dict):
                # Typically there's one class key like "030"
                for cls_key in gs_obj:
                    val = gs_obj[cls_key]
                    if isinstance(val, dict) and "Description" in val:
                        goods_desc = val["Description"]
                        break
            
            records.append(NormalizedRecord(
                category="USPTO_MARKS",
                source_side="json2",
                record_id=doc_id,
                registration_number=clean_registration_number(item.get("Registration_Number")),
                owner_raw=str(item.get("Owner", "")),
                owner_norm=normalize_owner(item.get("Owner", "")),
                goods_raw=str(goods_desc),
                goods_norm=normalize_goods_services(goods_desc),
                trademark_raw=str(item.get("Trademark", "")),
                trademark_norm=normalize_mark_text(item.get("Trademark", "")),
                domain_raw=_extract_domain_raw(item),
                domain_norm=normalize_domain_value(_extract_domain_raw(item) or _extract_url_raw(item)),
                url_raw=_extract_url_raw(item),
                url_norm=normalize_url_value(_extract_url_raw(item)),
                class_list=normalize_class_list(item.get("Class")),
                raw_payload=item
            ))
    return records

def extract_json2_records(data2) -> List[NormalizedRecord]:
    """
    Parses JSON 2 into canonical NormalizedRecord objects using helper extractors.
    """
    if isinstance(data2, list):
        records = _extract_json2_business_names_root_list(data2)
        if records:
            return records
        return _extract_json2_web_domains_root_list(data2)

    records = []
    
    # Validation: if keys exist, they must be lists
    for key in ["state_summary_data", "records", "business_records", "business_names_data", "domain_names_data", "Identical Names", "Similar Names"]:
        val = data2.get(key)
        if val is not None and not isinstance(val, list):
            raise ValueError(f"Invalid JSON 2: '{key}' must be a list if present.")

    records.extend(_extract_json2_state_marks(data2))
    records.extend(_extract_json2_common_law(data2))
    records.extend(_extract_json2_web_common_law_records_variant(data2))
    records.extend(_extract_json2_business_names(data2))
    records.extend(_extract_json2_business_names_variant(data2))
    records.extend(_extract_json2_web_domains(data2))
    records.extend(_extract_json2_web_domains_variant(data2))
    records.extend(_extract_json2_clarivate_web_domains(data2))
    records.extend(_extract_json2_clarivate_business_names(data2))
    records.extend(_extract_json2_clarivate_web_common_law(data2))
    records.extend(_extract_json2_clarivate_common_law(data2))
    records.extend(_extract_json2_federal_citations(data2))
    
    return records

def compare_category_counts(json1_by_cat: Dict[str, List[NormalizedRecord]], 
                            json2_by_cat: Dict[str, List[NormalizedRecord]]) -> Tuple[bool, str]:
    """
    Compares record counts per category.
    Returns (match_ok, failure_reason)
    """
    # Categories to check are those present in JSON 2
    # This preserves existing behavior where we only check what the current pattern reports
    relevant_categories = list(json2_by_cat.keys())
    
    failures = []
    print("\n--- GATE 1: CATEGORY COUNT VERIFICATION ---")
    for cat in relevant_categories:
        c1 = len(json1_by_cat.get(cat, []))
        c2 = len(json2_by_cat.get(cat, []))
        print(f"{cat:15}: JSON 1 = {c1:3}, JSON 2 = {c2:3}")
        if c1 != c2:
            failures.append(f"{cat}: JSON 1 count = {c1}, JSON 2 count = {c2}")
            
    if not failures:
        return True, ""
    else:
        return False, "; ".join(failures)
def run_gate2(json1_by_cat: Dict[str, List[NormalizedRecord]], 
              json2_by_cat: Dict[str, List[NormalizedRecord]]) -> List[CategoryComparisonResult]:
    """
    Orchestrates Gate 2 comparison for all categories present in JSON 2.
    """
    results = []
    
    # State Marks
    if "STATE_MARKS" in json2_by_cat:
        results.append(compare_state_marks(json1_by_cat.get("STATE_MARKS", []), json2_by_cat["STATE_MARKS"]))
        
    # Common Law
    if "COMMON_LAW" in json2_by_cat:
        results.append(compare_common_law(json1_by_cat.get("COMMON_LAW", []), json2_by_cat["COMMON_LAW"]))
        
    # Web Common Law
    if "WEB_COMMON_LAW" in json2_by_cat:
        results.append(compare_web_common_law(json1_by_cat.get("WEB_COMMON_LAW", []), json2_by_cat["WEB_COMMON_LAW"]))
        
    # Business Name
    if "BUSINESS_NAME" in json2_by_cat:
        results.append(compare_business_name(json1_by_cat.get("BUSINESS_NAME", []), json2_by_cat["BUSINESS_NAME"]))
        
    # Web Domain
    if "WEB_DOMAIN" in json2_by_cat:
        results.append(compare_web_domain(json1_by_cat.get("WEB_DOMAIN", []), json2_by_cat["WEB_DOMAIN"]))
        
    # USPTO Marks (Pattern-6)
    if "USPTO_MARKS" in json2_by_cat:
        # For Pattern-6, we filter specifically for those records in the comparison function
        results.append(compare_uspto_marks(json1_by_cat.get("USPTO_MARKS", []), json2_by_cat["USPTO_MARKS"]))
        
    return results

def process_single_json2(json2_path: str, json1_by_cat: Dict[str, List[NormalizedRecord]]) -> Tuple[str, List[str], bool, List[Any]]:
    """
    Processes a single JSON2 file against pre-loaded JSON1 data.
    Returns (filename, report_lines, is_pass, file_failures).
    """
    fname = os.path.basename(json2_path)
    print(f"\n{'='*60}")
    print(f"PROCESSING: {fname}")
    print(f"{'='*60}")
    
    file_failures = []
    
    try:
        with open(json2_path, "r", encoding="utf-8") as f:
            data2 = json.load(f)
        
        json2_records = extract_json2_records(data2)
        if not json2_records:
            msg = f"ERROR: No valid records found in {fname}"
            from post_comparison import classify_failure
            file_failures.append(classify_failure(
                file_name=fname,
                category="ALL",
                gate="GATE_2",
                record_id="N/A",
                field_name="File",
                json1_value="N/A",
                json2_value="N/A",
                raw_reason=msg
            ))
            print(msg)
            return fname, [msg], False, file_failures
            
        json2_by_cat = group_records_by_category(json2_records)
        
        # Gate 1
        match_ok, g1_reason = compare_category_counts(json1_by_cat, json2_by_cat)
        g1_status = "PASS" if match_ok else "FAIL"
        
        report_lines = [
            f"========================================",
            f"FILE: {fname}",
            f"========================================",
            f"Gate-1 Status: {g1_status}",
        ]
        if not match_ok:
            report_lines.append(f"Gate-1 Failure Reason: {g1_reason}")
            print(f"Gate-1 FAILED: {g1_reason}")
            from post_comparison import classify_failure
            for cat in json2_by_cat:
                c1 = len(json1_by_cat.get(cat, []))
                c2 = len(json2_by_cat.get(cat, []))
                if c1 != c2:
                    file_failures.append(classify_failure(
                        file_name=fname,
                        category=cat,
                        gate="GATE_1",
                        record_id="N/A",
                        field_name="Count",
                        json1_value=c1,
                        json2_value=c2,
                        raw_reason=f"Count mismatch: JSON 1 count = {c1}, JSON 2 count = {c2}"
                    ))
            # Even if Gate 1 fails, we return False but keep the report
            return fname, report_lines, False, file_failures
            
        print("Gate-1 PASSED.")
        
        # Gate 2
        print("Starting Gate-2 Deep Field Comparison...")
        results = run_gate2(json1_by_cat, json2_by_cat)
        
        is_g2_pass = True
        g2_report_parts = []
        from post_comparison import parse_and_classify_failure
        for res in results:
            # Console output
            print(f"\n  Category: {res.category}")
            if res.category == "WEB_DOMAIN" and res.total_extracted > 0:
                print(f"    Total extracted: {res.total_extracted} | Skipped: {res.skipped} | Effective: {res.total}")
                print(f"    Passed: {res.passed} | Failed: {len(res.failures)}")
            else:
                print(f"    Result: {res.passed}/{res.total} records passed.")
            
            if res.failures:
                print(f"    Failures/Mismatches:")
                for fail in res.failures:
                    print(f"      - {fail}")
                    file_failures.extend(parse_and_classify_failure(fname, res.category, fail))
            
            if res.passed != res.total:
                is_g2_pass = False
            
            # Report assembly
            g2_report_parts.extend(res.report_lines)
            g2_report_parts.append("")
            
        g2_status = "PASS" if is_g2_pass else "FAIL"
        report_lines.append(f"Gate-2 Status: {g2_status}")
        report_lines.append("-" * 40)
        report_lines.extend(g2_report_parts)
        
        return fname, report_lines, is_g2_pass, file_failures
        
    except Exception as e:
        err_msg = f"CRITICAL ERROR processing {fname}: {e}"
        print(err_msg)
        return fname, [f"FILE: {fname}", err_msg], False, []

def main():
    if len(sys.argv) < 3:
        print("Usage: python comparition_v1.py <path_to_json1> <path_to_json2_file1> [path_to_json2_file2] ...")
        sys.exit(1)

    path1 = sys.argv[1]
    json2_paths = sys.argv[2:]

    try:
        with open(path1, "r", encoding="utf-8") as f: 
            data1 = json.load(f)
    except Exception as e:
        print(f"Error reading JSON1 file: {e}")
        sys.exit(1)

    # 1. Extraction and Grouping for JSON1 (Constant)
    try:
        json1_records = extract_json1_records(data1)
        json1_by_cat = group_records_by_category(json1_records)
    except Exception as e:
        print(f"JSON1 Extraction Error: {e}")
        sys.exit(1)

    all_file_reports = []
    final_summary_stats = []
    all_classified_failures = []

    # 2. Process each JSON2 file
    for p2 in json2_paths:
        fname, report_lines, is_pass, file_failures = process_single_json2(p2, json1_by_cat)
        all_file_reports.extend(report_lines)
        all_file_reports.append("\n" + "="*60 + "\n") # Big separator between files
        all_classified_failures.extend(file_failures)
        
        status_str = "PASS" if is_pass else "FAIL"
        final_summary_stats.append((fname, status_str))

    # 3. Generate Final Summary
    summary_block = [
        "==============================",
        "FINAL SUMMARY",
        "=============================="
    ]
    all_passed = True
    for fname, status in final_summary_stats:
        summary_block.append(f"{fname:30} : {status}")
        if status == "FAIL":
            all_passed = False
            
    # Include Defect Classification report block
    from post_comparison import generate_defect_summary, DefectType
    defect_summary_lines = generate_defect_summary(all_classified_failures)
    
    # 4. Write Unified Report
    # Construct concise Defect Summary block
    defect_counts = {dt: 0 for dt in DefectType}
    for f in all_classified_failures:
        if hasattr(f, "defect_type"):
            defect_counts[f.defect_type] = defect_counts.get(f.defect_type, 0) + 1
            
    defect_summary_sec = [
        "======================",
        "DEFECT SUMMARY",
        "================",
    ]
    for dt in DefectType:
        defect_summary_sec.append(f"{dt.value}: {defect_counts[dt]}")

    combined_report = ["GATE 2 UNIFIED COMPARISON REPORT", "="*40, ""]
    combined_report.extend(all_file_reports)
    combined_report.extend(summary_block)
    combined_report.append("")
    combined_report.extend(defect_summary_lines)
    combined_report.append("")
    combined_report.extend(defect_summary_sec)

    # Required Business Rule: Timestamp-based unique report in comparision_result folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(script_dir, "comparision_result")
    os.makedirs(output_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"rou_comparison_{timestamp}.txt"
    report_path = os.path.join(output_folder, report_filename)

    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write("\n".join(combined_report))
    
    print(f"\nUnified comparison report written to:\n{report_path}")
    
    print("\n" + "\n".join(summary_block))
    
    if all_classified_failures:
        print("\n" + "\n".join(defect_summary_lines))
        
    print("\n" + "\n".join(defect_summary_sec))

    if all_passed:
        print("\nOVERALL STATUS: PASS")
        sys.exit(0)
    else:
        print("\nOVERALL STATUS: FAIL (One or more patterns failed)")
        sys.exit(1)

if __name__ == "__main__":
    main()
