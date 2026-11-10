from .legal_source import LegalSource
from .text_extraction_service import TextExtractionService
from .rules_manager import RulesManager


#rulemanager connect to rule and ruleversion then collect the rules and save object rules.
#RuleClauses use rulemanager to get the rules and save in in database
class RuleClauses:
    
    def save_from_legal_source(self,conn):
        legalSource = LegalSource()
        textExtractionService = TextExtractionService()
        source = legalSource.get_source(conn)
        text = textExtractionService.extract_text(source)
        ruleanager = RulesManager()
        rules = ruleanager.extract_rules_info(text)
        for r in rules:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO rule (id,name, description) VALUES (%s,%s, %s)",
                (r["rule"].id,r["rule"].name, r["rule"].description)
            )
            conn.commit()
            cursor.execute(
                        "INSERT INTO rule_version (rule_id, fact_name,fact_condition,fact_value) VALUES (%s,%s, %s,%s)",
                        (r["ruleVersion"].rule_id,r["ruleVersion"].fact_name, r["ruleVersion"].condition,r['ruleVersion'].fact_value)
                    )
        conn.commit()
        cursor.close()
        conn.close()
