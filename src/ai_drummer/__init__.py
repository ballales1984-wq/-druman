"""
ReaperDrummerAI - AI Drum Generator per Reaper

Moduli:
- analyzer: Analizza tracce audio (BPM, beat, onsets, sezioni)
- intent_vector: Estrae intenzione musicale (il cuore del sistema)
- decision_engine: Decide cosa suonare (il cervello reattivo)
- drum_generator: Genera pattern di batteria evolutivi
- humanizer: Aggiunge feel umano (swing, groove, velocity)
- main: Orchestratore principale
"""

from .analyzer import AudioAnalyzer, AudioAnalysis, analyze_reference
from .intent_vector import (
    IntentVector,
    IntentExtractor,
    RealtimeIntentProcessor,
    create_intent_from_analysis,
    GrooveType,
    IntensityLevel,
    SectionType,
)
from .decision_engine import (
    DecisionEngine,
    AdaptiveDecisionEngine,
    DecisionConfig,
    create_reactive_system,
    DrumCommand,
    DrumType,
)
from .drum_generator import (
    DrumGenerator,
    DrumPattern,
    Complexity,
    MusicStyle,
    generate_drum_pattern,
)
from .humanizer import Humanizer, HumanGroove, humanize_midi
from .main import ReaperDrummerAI

__version__ = "1.1.0"
__author__ = "ReaperDrummerAI"

__all__ = [
    "AudioAnalyzer",
    "AudioAnalysis",
    "analyze_reference",
    "IntentVector",
    "IntentExtractor",
    "RealtimeIntentProcessor",
    "create_intent_from_analysis",
    "GrooveType",
    "IntensityLevel",
    "SectionType",
    "DecisionEngine",
    "AdaptiveDecisionEngine",
    "DecisionConfig",
    "create_reactive_system",
    "DrumCommand",
    "DrumType",
    "DrumGenerator",
    "DrumPattern",
    "Complexity",
    "MusicStyle",
    "generate_drum_pattern",
    "Humanizer",
    "HumanGroove",
    "humanize_midi",
    "ReaperDrummerAI",
]
