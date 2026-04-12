"""
Vegetation monitoring example: point (sample), line (corridor / span), polygon (work area).

Domains and field lists are illustrative for QA/QC field workflows; adjust for your program.
"""

from __future__ import annotations

# Shared coded domains (file GDB). Names are stable for scripting and AGOL publish prep.
DOMAINS: list[dict] = [
    {
        "name": "vegqc_qc_status",
        "description": "Office QC state for submitted field data",
        "field_type": "TEXT",
        "coded_values": [
            ("DRAFT", "Draft"),
            ("SUBMITTED", "Submitted"),
            ("QC_REVIEW", "QC review"),
            ("QC_APPROVED", "QC approved"),
            ("QC_REJECTED", "QC rejected"),
        ],
    },
    {
        "name": "vegqc_encroachment",
        "description": "Vegetation encroachment relative to clearance",
        "field_type": "TEXT",
        "coded_values": [
            ("NONE", "None / compliant"),
            ("MINOR", "Minor"),
            ("MODERATE", "Moderate"),
            ("SEVERE", "Severe"),
            ("UNKNOWN", "Unknown"),
        ],
    },
    {
        "name": "vegqc_height_class",
        "description": "Vegetation height class at sample point",
        "field_type": "TEXT",
        "coded_values": [
            ("H0", "Below line"),
            ("H1", "At line"),
            ("H2", "Above line"),
            ("H3", "Fall-in risk"),
        ],
    },
    {
        "name": "vegqc_treatment",
        "description": "Treatment or work type for polygon areas",
        "field_type": "TEXT",
        "coded_values": [
            ("NONE", "None"),
            ("MANUAL", "Manual trim"),
            ("MECHANICAL", "Mechanical"),
            ("HERBICIDE", "Herbicide"),
            ("MONITOR_ONLY", "Monitor only"),
        ],
    },
]


def _qc() -> dict:
    return {
        "name": "qc_status",
        "type": "TEXT",
        "alias": "QC status",
        "length": 32,
        "domain": "vegqc_qc_status",
    }


FEATURE_CLASSES: list[dict] = [
    {
        "name": "VegMon_SamplePoint",
        "geometry": "POINT",
        "fields": [
            {
                "name": "inspection_id",
                "type": "TEXT",
                "alias": "Inspection ID",
                "length": 64,
            },
            {
                "name": "sample_date",
                "type": "DATE",
                "alias": "Sample date",
            },
            {
                "name": "species_common",
                "type": "TEXT",
                "alias": "Species (common)",
                "length": 128,
            },
            {
                "name": "height_class",
                "type": "TEXT",
                "alias": "Height class",
                "length": 8,
                "domain": "vegqc_height_class",
            },
            {
                "name": "encroachment",
                "type": "TEXT",
                "alias": "Encroachment",
                "length": 16,
                "domain": "vegqc_encroachment",
            },
            {
                "name": "notes",
                "type": "TEXT",
                "alias": "Notes",
                "length": 500,
            },
            _qc(),
        ],
    },
    {
        "name": "VegMon_CorridorLine",
        "geometry": "POLYLINE",
        "fields": [
            {
                "name": "span_id",
                "type": "TEXT",
                "alias": "Span ID",
                "length": 64,
            },
            {
                "name": "circuit_id",
                "type": "TEXT",
                "alias": "Circuit ID",
                "length": 32,
            },
            {
                "name": "segment_type",
                "type": "TEXT",
                "alias": "Segment type",
                "length": 64,
            },
            {
                "name": "encroachment",
                "type": "TEXT",
                "alias": "Encroachment",
                "length": 16,
                "domain": "vegqc_encroachment",
            },
            {
                "name": "last_trim_date",
                "type": "DATE",
                "alias": "Last trim date",
            },
            {
                "name": "notes",
                "type": "TEXT",
                "alias": "Notes",
                "length": 500,
            },
            _qc(),
        ],
    },
    {
        "name": "VegMon_WorkAreaPolygon",
        "geometry": "POLYGON",
        "fields": [
            {
                "name": "area_id",
                "type": "TEXT",
                "alias": "Area ID",
                "length": 64,
            },
            {
                "name": "work_order_id",
                "type": "TEXT",
                "alias": "Work order ID",
                "length": 64,
            },
            {
                "name": "treatment_type",
                "type": "TEXT",
                "alias": "Treatment type",
                "length": 32,
                "domain": "vegqc_treatment",
            },
            {
                "name": "monitoring_cycle",
                "type": "TEXT",
                "alias": "Monitoring cycle",
                "length": 32,
            },
            {
                "name": "target_complete_date",
                "type": "DATE",
                "alias": "Target complete date",
            },
            {
                "name": "notes",
                "type": "TEXT",
                "alias": "Notes",
                "length": 500,
            },
            _qc(),
        ],
    },
]
