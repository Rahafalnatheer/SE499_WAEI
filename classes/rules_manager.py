import re
from .rule import Rule
from .rule_version import RuleVersion
class RulesManager:

    def extract_rules_info(self,text):
        rules_data = []
        rules_matches = re.finditer(r"RULE\s+(\d+)\s*[-—](.+)",text)
        for i,m in enumerate(list(rules_matches)):
            rule_id = m.group(1)
            rule_name = m.group(2).strip()
            st = m.start()
            if i < len(list(rules_matches))-1:
                end = rules_matches[i+1].start()
            else:
                end = len(text)
            inner_text = text[st:end].strip()
            version_match = re.search(r"Version\s*:(.+)",inner_text)
            rule_version = version_match.group(1).strip()
            desc_match = re.search(r"Description\s*:(.+)",inner_text)
            rule_desc = desc_match.group(1).strip()
            fact_name_match = re.search(r"Fact\s+to\s+extract\s*:\s*(.+)",inner_text)
            rule_fact_name = fact_name_match.group(1).strip()
            fact_condition_match = re.search(r"Condition\s*:\s*" + rule_fact_name +"\s*(>=|<=|>|<|==|=)\s*(.+)",inner_text)
            fact_condition = fact_condition_match.group(1).strip()
            fact_value = fact_condition_match.group(2).strip()
            rule = Rule(rule_id,rule_name,rule_desc)
            ruleVersion = RuleVersion(rule_id=rule_id,fact_name=rule_fact_name,condition=fact_condition,fact_value=fact_value)

            rules_data.append({
                "rule":rule,
                "ruleVersion":ruleVersion
            })
        return rules_data
