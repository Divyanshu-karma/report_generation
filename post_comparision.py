import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, List

class DefectType(str, Enum):
    PIPELINE_DEFECT = "PIPELINE_DEFECT"
    EXTRACTION_DEFECT = "EXTRACTION_DEFECT"
    COMPARISON_ENGINE_DEFECT = "COMPARISON_ENGINE_DEFECT"
    NORMALIZATION_GAP = "NORMALIZATION_GAP"
    EXPECTED_DATA_DIFFERENCE = "EXPECTED_DATA_DIFFERENCE"
    UNCLASSIFIED_REVIEW_REQUIRED = "UNCLASSIFIED_REVIEW_REQUIRED"

@dataclass
class ClassifiedFailure:
    file_name: str
    category: str
    gate: str
    record_id: Optional[str]
    field_name: Optional[str]
    json1_value: Any
    json2_value: Any
    raw_reason: str
    defect_type: DefectType
    priority: str
    likely_owner: str
    recommended_action: str

def looks_like_state_law_class_mapping_bug(json1_value: Any, json2_value: Any) -> bool:
    try:
        def extract_ints(val):
            if isinstance(val, (list, tuple)):
                return [int(x) for x in val]
            val_str = str(val)
            val_str = re.sub(r'\[.*?\]', '', val_str)
            val_str = re.sub(r'[\[\]\(\),]', ' ', val_str)
            return [int(s) for s in val_str.split() if s.isdigit()]
            
        ints1 = extract_ints(json1_value)
        ints2 = extract_ints(json2_value)
        
        if not ints1 or not ints2:
            return False
            
        if set(ints1) != set(ints2):
            # If JSON1 contains indexes like 0, 1, 2 and JSON2 contains typical Nice Classes
            if any(x in {0, 1, 2} for x in ints1) and not any(x in {0, 1, 2} for x in ints2):
                return True
    except Exception:
        pass
    return False

EXPECTED_OPTIONAL_FIELDS = {
    "WEB_COMMON_LAW": {"Goods", "Owner"},
    "WEB_DOMAIN": {"Owner", "Goods"},
}

MANDATORY_FIELDS = {
    "STATE_MARKS": {"Trademark", "Owner", "Class"},
    "COMMON_LAW": {"Trademark", "Owner"},
    "BUSINESS_NAME": {"Trademark", "Owner"},
    "WEB_DOMAIN": {"Trademark"},
    "WEB_COMMON_LAW": {"Trademark"},
    "USPTO_MARKS": {"Trademark", "Owner"},
}

def classify_missing_field(category: str, field_name: str, status: str) -> Optional[DefectType]:
    is_optional = field_name in EXPECTED_OPTIONAL_FIELDS.get(category, set())
    is_mandatory = field_name in MANDATORY_FIELDS.get(category, set())
    
    if status == "MISSING_BOTH":
        if is_optional:
            return DefectType.EXPECTED_DATA_DIFFERENCE
        else:
            return DefectType.UNCLASSIFIED_REVIEW_REQUIRED
            
    elif status in ("MISSING_JSON1", "MISSING_JSON2"):
        if is_mandatory:
            return DefectType.EXTRACTION_DEFECT
        elif is_optional:
            return DefectType.EXPECTED_DATA_DIFFERENCE
            
    return None

def classify_failure(
    file_name: str,
    category: str,
    gate: str,
    record_id: str,
    field_name: str,
    json1_value,
    json2_value,
    raw_reason: str
) -> ClassifiedFailure:
    reason_upper = str(raw_reason).upper()
    
    # Category-aware missing field classification
    missing_status = None
    if "[MISSING_BOTH]" in reason_upper:
        missing_status = "MISSING_BOTH"
    elif "[MISSING_JSON1]" in reason_upper:
        missing_status = "MISSING_JSON1"
    elif "[MISSING_JSON2]" in reason_upper:
        missing_status = "MISSING_JSON2"

    if missing_status:
        dt = classify_missing_field(category, field_name, missing_status)
        if dt:
            priority = "LOW"
            likely_owner = "Data Design"
            recommended_action = "No action required, missing optional field is expected for this category."
            
            if dt == DefectType.EXTRACTION_DEFECT:
                priority = "HIGH"
                likely_owner = "Extractor / DB Mapper"
                recommended_action = "Check extractor logs and mappings for missing mandatory field."
            elif dt == DefectType.UNCLASSIFIED_REVIEW_REQUIRED:
                priority = "MEDIUM"
                likely_owner = "Manual Review"
                recommended_action = "Review raw JSON1 and JSON2 values before adding logic."
                
            return ClassifiedFailure(
                file_name=file_name,
                category=category,
                gate=gate,
                record_id=record_id,
                field_name=field_name,
                json1_value=json1_value,
                json2_value=json2_value,
                raw_reason=raw_reason,
                defect_type=dt,
                priority=priority,
                likely_owner=likely_owner,
                recommended_action=recommended_action
            )
    
    if "LIKELY_EXTRACTION_DEFECT" in reason_upper:
        return ClassifiedFailure(
            file_name=file_name,
            category=category,
            gate=gate,
            record_id=record_id,
            field_name=field_name,
            json1_value=json1_value,
            json2_value=json2_value,
            raw_reason=raw_reason,
            defect_type=DefectType.EXTRACTION_DEFECT,
            priority="HIGH",
            likely_owner="State Law Extractor / DB Mapper",
            recommended_action="Check whether JSON1 is storing class indexes or ordinal positions instead of actual Nice Classes."
        )
        
    if gate == "GATE_1":
        return ClassifiedFailure(
            file_name=file_name,
            category=category,
            gate=gate,
            record_id=record_id,
            field_name=field_name,
            json1_value=json1_value,
            json2_value=json2_value,
            raw_reason=raw_reason,
            defect_type=DefectType.PIPELINE_DEFECT,
            priority="HIGH",
            likely_owner="Pipeline / Persistence",
            recommended_action="Verify extraction count, DB persistence count, and category routing."
        )
        
    if "NO VALID RECORDS FOUND" in reason_upper:
        return ClassifiedFailure(
            file_name=file_name,
            category=category,
            gate=gate,
            record_id=record_id,
            field_name=field_name,
            json1_value=json1_value,
            json2_value=json2_value,
            raw_reason=raw_reason,
            defect_type=DefectType.PIPELINE_DEFECT,
            priority="HIGH",
            likely_owner="Pipeline / JSON Export",
            recommended_action="Verify that the RoU pipeline generated and exported JSON for this category."
        )
        
    if field_name == "Class" and looks_like_state_law_class_mapping_bug(json1_value, json2_value):
        return ClassifiedFailure(
            file_name=file_name,
            category=category,
            gate=gate,
            record_id=record_id,
            field_name=field_name,
            json1_value=json1_value,
            json2_value=json2_value,
            raw_reason=raw_reason,
            defect_type=DefectType.EXTRACTION_DEFECT,
            priority="HIGH",
            likely_owner="State Law Extractor / DB Mapper",
            recommended_action="Check whether JSON1 is storing class indexes or ordinal positions instead of actual Nice Classes."
        )
        
    if "AMBIGUOUS" in reason_upper:
        return ClassifiedFailure(
            file_name=file_name,
            category=category,
            gate=gate,
            record_id=record_id,
            field_name=field_name,
            json1_value=json1_value,
            json2_value=json2_value,
            raw_reason=raw_reason,
            defect_type=DefectType.COMPARISON_ENGINE_DEFECT,
            priority="MEDIUM",
            likely_owner="Comparison Engine",
            recommended_action="Improve candidate tie-breaking, matching tiers, or candidate scoring."
        )
        
    if field_name in {"Owner", "Trademark", "Goods"}:
        return ClassifiedFailure(
            file_name=file_name,
            category=category,
            gate=gate,
            record_id=record_id,
            field_name=field_name,
            json1_value=json1_value,
            json2_value=json2_value,
            raw_reason=raw_reason,
            defect_type=DefectType.NORMALIZATION_GAP,
            priority="MEDIUM",
            likely_owner="Normalization Layer",
            recommended_action="Add targeted normalization rule and regression test."
        )
        
    return ClassifiedFailure(
        file_name=file_name,
        category=category,
        gate=gate,
        record_id=record_id,
        field_name=field_name,
        json1_value=json1_value,
        json2_value=json2_value,
        raw_reason=raw_reason,
        defect_type=DefectType.UNCLASSIFIED_REVIEW_REQUIRED,
        priority="MEDIUM",
        likely_owner="Manual Review",
        recommended_action="Review raw JSON1 and JSON2 values before adding logic."
    )

def parse_and_classify_failure(file_name: str, category: str, failure_str: str) -> List[ClassifiedFailure]:
    classified = []
    
    if "): " in failure_str:
        header, rest = failure_str.split("): ", 1)
        if " (Owner: " in header:
            record_id = header.split(" (Owner: ", 1)[0]
        else:
            record_id = header.strip()
    elif ": " in failure_str:
        header, rest = failure_str.split(": ", 1)
        record_id = header.strip()
    else:
        cf = classify_failure(
            file_name=file_name,
            category=category,
            gate="GATE_2",
            record_id="Unknown",
            field_name="Unknown",
            json1_value="N/A",
            json2_value="N/A",
            raw_reason=failure_str
        )
        classified.append(cf)
        return classified
            
    if " | " in rest or any(rest.strip().startswith(f + ":") for f in ["Owner", "Trademark", "Goods", "Class", "Domain", "URL", "SIC", "Registration"]):
        parts = rest.split(" | ")
        for part in parts:
            part = part.strip()
            field_match = re.match(r'^([^:]+):\s*(.*)$', part)
            if field_match:
                field_name = field_match.group(1).strip()
                detail = field_match.group(2).strip()
                
                j1_val = "N/A"
                j2_val = "N/A"
                
                if "J1:" in detail and "J2:" in detail:
                    vals = re.findall(r"J[12]:'(.*?)'", detail)
                    if len(vals) == 2:
                        j1_val, j2_val = vals[0], vals[1]
                    else:
                        vals_no_quotes = re.findall(r"J[12]:(.*?)(?:\s+!=\s+|\s*$)", detail)
                        if len(vals_no_quotes) >= 2:
                            j1_val, j2_val = vals_no_quotes[0].strip(), vals_no_quotes[1].strip()
                elif " != " in detail:
                    vals = detail.split(" != ")
                    if len(vals) == 2:
                        j1_val, j2_val = vals[0].strip(), vals[1].strip()
                        
                cf = classify_failure(
                    file_name=file_name,
                    category=category,
                    gate="GATE_2",
                    record_id=record_id,
                    field_name=field_name,
                    json1_value=j1_val,
                    json2_value=j2_val,
                    raw_reason=part
                )
                classified.append(cf)
            else:
                cf = classify_failure(
                    file_name=file_name,
                    category=category,
                    gate="GATE_2",
                    record_id=record_id,
                    field_name="Unknown",
                    json1_value="N/A",
                    json2_value="N/A",
                    raw_reason=part
                )
                classified.append(cf)
    else:
        field_name = "Record"
        j1_val = "N/A"
        j2_val = "N/A"
        if "No matching JSON1 record found for" in rest:
            quotes = re.findall(r"'(.*?)'", rest)
            if len(quotes) >= 2:
                j2_val = f"Trademark: '{quotes[0]}', Owner: '{quotes[1]}'"
        
        if "NO VALID RECORDS FOUND" in rest.upper():
            field_name = "File"
            
        cf = classify_failure(
            file_name=file_name,
            category=category,
            gate="GATE_2",
            record_id=record_id,
            field_name=field_name,
            json1_value=j1_val,
            json2_value=j2_val,
            raw_reason=rest
        )
        classified.append(cf)
        
    return classified

def generate_defect_summary(failures: List[ClassifiedFailure]) -> List[str]:
    """
    Generates a structured text block summarizing the classified defects.
    """
    if not failures:
        return ["NO DEFECTS DETECTED"]
        
    summary = [
        "",
        "========================================",
        "DEFECT CLASSIFICATION ASSESSMENT SUMMARY",
        "========================================",
    ]
    
    # Counts by defect type
    counts = {}
    for f in failures:
        counts[f.defect_type] = counts.get(f.defect_type, 0) + 1
        
    summary.append("DEFECT COUNTS BY CATEGORY:")
    for dt, count in counts.items():
        summary.append(f"  - {dt.value}: {count}")
        
    summary.append("")
    summary.append("DETAILED DIAGNOSTIC BREAKDOWN:")
    for idx, f in enumerate(failures, start=1):
        summary.append(f"  {idx}. [Gate: {f.gate}] [{f.defect_type.value}] priority={f.priority}")
        summary.append(f"     File     : {f.file_name}")
        summary.append(f"     Category : {f.category}")
        if f.record_id and f.record_id != "N/A":
            summary.append(f"     Record ID: {f.record_id}")
        if f.field_name and f.field_name != "N/A":
            summary.append(f"     Field    : {f.field_name}")
        if f.json1_value != "N/A":
            summary.append(f"     JSON1 Val: {f.json1_value}")
        if f.json2_value != "N/A":
            summary.append(f"     JSON2 Val: {f.json2_value}")
        summary.append(f"     Reason   : {f.raw_reason}")
        summary.append(f"     Owner    : {f.likely_owner}")
        summary.append(f"     Action   : {f.recommended_action}")
        summary.append("")
        
    return summary
