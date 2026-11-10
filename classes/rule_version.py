class RuleVersion:
    def __init__(
        self,
        id=None,
        rule_id=None,
        fact_name=None,
        condition=None,
        fact_value=None
    ):
        self.id = id
        self.rule_id = rule_id
        self.fact_name = fact_name
        self.condition = condition
        self.fact_value = fact_value

    