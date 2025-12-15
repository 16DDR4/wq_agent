
CUTOFF_RULE_SCHEMA = {
    "type": "object",
    "properties": {
        "alpha_id": {"type": "string"},

        "alpha_context": {
            "type": "object",
            "properties": {
                "region": {"type": "string"},          # USA / CHN / etc
                "frequency": {"type": "string"},       # D1 / D5
                "theme": {"type": "string"},           # PV / MODEL / etc
                "universe": {"type": "string"},        # TOP3000 / TOP1000
            },
            "required": ["region", "frequency"]
        },

        "metrics": {
            "type": "object",
            "properties": {
                "fitness": {"type": "number"},
                "sharpe": {"type": "number"},
                "turnover": {"type": "number"},
                "weight_concentration": {"type": "number"},
                "sub_universe_sharpe": {"type": "number"},
                "ladder_sharpe": {
                    "type": "object",
                    "additionalProperties": {"type": "number"}
                }
            },
            "required": ["fitness", "sharpe"]
        },

        "cutoff_policy": {
            "type": "object",
            "properties": {
                "strict": {"type": "boolean"},
                "allow_soft_fail": {"type": "boolean"}
            },
            "required": ["strict"]
        }
    },
    "required": ["alpha_id", "alpha_context", "metrics", "cutoff_policy"]
}

