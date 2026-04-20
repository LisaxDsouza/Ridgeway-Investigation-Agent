from .tool_registry import TOOL_REGISTRY

def calculate_incident_confidence(raw_summary: str, tools_used: list):
    """
    Calculates a dynamic confidence score based on:
    1. Heuristic keyword analysis of the agent's summary.
    2. The weighted average reliability of the tools used in the investigation.
    """
    
    # 1. Base Heuristic Score (LLM summary analysis)
    base_score = 0.8
    level = "high"
    
    summary_lower = raw_summary.lower()
    if any(k in summary_lower for k in ["uncertain", "not clear", "needs verification", "unproven"]):
        base_score = 0.4
        level = "low"
    elif any(k in summary_lower for k in ["likely", "probable", "possible"]):
        base_score = 0.6
        level = "medium"
    elif any(k in summary_lower for k in ["confirmed", "verified", "evident", "clear indicator"]):
        base_score = 0.95
        level = "critical"

    # 2. Tool Reliability Multiplier
    if not tools_used:
        # If no tools were used, the confidence is inherently limited
        return base_score * 0.5, "low", "Investigation performed without secondary tool verification."

    reliabilities = []
    for t in tools_used:
        tool_name = t.get("tool")
        meta = TOOL_REGISTRY.get(tool_name)
        if meta:
            reliabilities.append(meta["reliability"])
    
    avg_reliability = sum(reliabilities) / len(reliabilities) if reliabilities else 0.5
    
    # Final confidence is the base score influenced by the tool reliability
    # We use a simple product here, but could be more complex (e.g. root sum square)
    final_confidence = base_score * avg_reliability
    
    # Round to 2 decimal places
    final_confidence = round(final_confidence, 2)
    
    # Determine level based on final score
    if final_confidence >= 0.8:
        final_level = "high"
    elif final_confidence >= 0.5:
        final_level = "medium"
    else:
        final_level = "low"
        
    rationale = f"Based on keyword analysis ({level}) and tool reliability ({avg_reliability:.2f})."
    
    return final_confidence, final_level, rationale
