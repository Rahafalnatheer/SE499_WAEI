import operator
import json
import os
from llama_cpp import Llama,LlamaRAMCache
from huggingface_hub import hf_hub_download




class Finding:
    MODEL_REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"
    MODEL_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"
    def __init__(
        self,
        id=None,
        rule_version_id=None,
        contract_id=None,
        extracted_value=None,
        result=None,
        model_path=None

    ):
        self.id = id
        self.rule_version_id = rule_version_id
        self.contract_id = contract_id
        self.extracted_value = extracted_value
        self.result = result
        if model_path is None:
                    model_path = hf_hub_download(
                        repo_id=self.MODEL_REPO,
                        filename=self.MODEL_FILE
                    )

        self.model = Llama(
                    model_path=model_path,
                    n_ctx=8192,
                    n_batch=256,
                    n_threads=4,
                    n_gpu_layers=-1,
                    verbose=False
                )
        
        self.model.set_cache(
                    LlamaRAMCache(capacity_bytes=2 * 1024 * 1024 * 1024)
                )

    # def get_fact_by_contract_id(self,conn,contract_id,fact_names,fact_values):
    #     cursor = conn.cursor()
    #     i=0
    #     for f_name in fact_names:
    #         cursor.execute("SELECT fact_name,fact_value,fact_condition FROM rule_version where fact_name LIKE %s",(f"{f_name}%",))
    #         fact = cursor.fetchall()
    #         if fact:
    #             fact = fact[0]
    #             fact_name = fact[0]
    #             fact_value = fact_values[i]
    #             print("%%%%%%",fact_value)
    #             cursor.close()
    #             conn.close()
    #             return fact_name,fact_value
            
    #         i+=1
            
    #     return None,None

    def review_contract(self,contract_data, rules):
#         return {'contract_title': 'EMPLOYMENT CONTRACT – CONTRACT 2',
#  'clauses': [{'status': 'satisfied',
#    'clause_name': 'probation_period',
#    'clause_data': 'ninety (90) days starting from the first working day'},
#   {'status': 'need_review',
#    'clause_name': 'annual_leave',
#    'clause_data': 'twenty-one (21) days of paid annual leave for each year of service, increasing to thirty (30) days after five (5) consecutive years of service'},
#   {'status': 'need_review',
#    'clause_name': 'working_hours',
#    'clause_data': 'eight (8) hours per day and forty-eight (48) hours per week, distributed over six (6) working days'},
#   {'status': 'need_review',
#    'clause_name': 'overtime',
#    'clause_data': "any hours exceeding the applicable statutory working-hour limits shall be treated as overtime, with additional payment of fifty percent (50%) of the employee's basic hourly wage for each overtime hour"},
#   {'status': 'need_review',
#    'clause_name': 'notice_period',
#    'clause_data': 'sixty (60) days when notice is given by the employer for an employee paid monthly, thirty (30) days when notice is given by the employee'},
#   {'status': 'need_review',
#    'clause_name': 'contract_duration',
#    'clause_data': 'two (2) years, commencing on 1 January 2027 and ending on 31 December 2028'},
#   {'status': 'need_review',
#    'clause_name': 'end_of_service_payment',
#    'clause_data': "end-of-service benefits in accordance with Saudi Labor Law, calculated based on half a month's wage for each of the first five (5) years of service and one month's wage for each subsequent year of service"},
#   {'status': 'need_review',
#    'clause_name': 'non_compete_terms',
#    'clause_data': "for a period of twelve (12) months following termination of employment, the employee shall not engage in activities that directly compete with the employer's software development business within Riyadh, Saudi Arabia"},
#   {'status': 'need_review',
#    'clause_name': 'salary_and_payment_terms',
#    'clause_data': "monthly compensation of SAR 10,000, paid through bank transfer to the employee's registered bank account on the twenty-seventh (27th) day of each calendar month"}]}

        rules_json = json.dumps(
            rules,
            ensure_ascii=False,
            separators=(",", ":")
        )

        contract_json = json.dumps(
            contract_data,
            ensure_ascii=False,
            separators=(",", ":")
        )

        prompt = f"""
    You are a Saudi Labor Law compliance reviewer.

    Your task is to evaluate the extracted employment contract
    information against the supplied labor law rules.

    ==============================
    EXTRACTED CONTRACT DATA
    ==============================

    {contract_json}

    ==============================
    SUPPLIED LABOR LAW RULES
    ==============================

    {rules_json}

    ==============================
    CLAUSES TO EVALUATE
    ==============================

    Evaluate exactly these nine categories:

    1. probation_period
    2. annual_leave
    3. working_hours
    4. overtime
    5. notice_period
    6. contract_duration
    7. end_of_service_payment
    8. non_compete_terms
    9. salary_and_payment_terms

    ==============================
    RULE-TO-CLAUSE MATCHING
    ==============================

    Use the following matching guidance:

    1. probation_period:
    No directly applicable rule is supplied.

    2. annual_leave:
    No directly applicable rule is supplied.

    3. working_hours:
    Match with the rule concerning hours exceeding standard
    weekly working hours (Overtime Hours, Rule 8).

    4. overtime:
    Match with the following rules:
    - Rule 7: Overtime Pay.
    - Rule 8: Overtime Hours.
    - Rule 9: Holiday Overtime.

    5. notice_period:
    No directly applicable rule is supplied.

    6. contract_duration:
    No directly applicable rule is supplied.

    7. end_of_service_payment:
    No directly applicable rule is supplied.

    8. non_compete_terms:
    No directly applicable rule is supplied.

    9. salary_and_payment_terms:
    No directly applicable rule is supplied.

    These mappings identify relevant rules only.
    Always examine the complete original rule definitions
    before making a compliance decision.

    Do not match unrelated rules to a clause.

    ==============================
    COMPLIANCE EVALUATION
    ==============================

    For every clause:

    1. Identify its extracted contract value.
    2. Identify all applicable supplied rules.
    3. Compare the contract value with the requirements
    of every applicable rule.
    4. Consider numerical values, conditions, exceptions,
    limitations, and applicability.
    5. Evaluate all applicable rules before assigning a status.

    If multiple rules apply to one clause, all applicable
    requirements must be satisfied to assign satisfied.

    Do not introduce legal requirements from external knowledge.

    ==============================
    STATUS DEFINITIONS
    ==============================

    satisfied:
    The contract clause exists and satisfies all applicable
    supplied labor law rules.

    need_review:
    The contract clause exists but violates, partially satisfies,
    or cannot be verified against applicable supplied rules.

    Also use need_review when no directly applicable rule
    is supplied for an existing clause.

    failed:
    The extracted contract value is null or absent.

    ==============================
    IMPORTANT INSTRUCTIONS
    ==============================

    - Perform the complete matching and compliance evaluation.
    - Do not extract contract information again.
    - Use the extracted contract values directly.
    - Do not invent or modify contract values.
    - Never mark an existing extracted clause as failed.
    - Never mark a missing clause as satisfied or need_review.
    - Do not assume compliance without checking applicable rules.
    - If no applicable rule exists, use need_review.
    - Preserve the exact extracted clause values.
    - CONTRACT TITLE:

    Copy the exact value of "Contract Title" from the extracted
    contract data.

    If the value is null or absent, return exactly "No title".

    Never return the placeholder "Contract title or No title".
    Never invent a contract title.
    - Return exactly nine clause objects.
    - Follow the specified clause order.

    ==============================
    OUTPUT FORMAT
    ==============================

    {{
        "contract_title": "Contract title or No title",
        "clauses": [
            {{
                "status": "satisfied",
                "clause_name": "probation_period",
                "clause_data": "Extracted contract value"
            }},
            {{
                "status": "need_review",
                "clause_name": "annual_leave",
                "clause_data": "Extracted contract value"
            }},
            {{
                "status": "need_review",
                "clause_name": "working_hours",
                "clause_data": "Extracted contract value"
            }},
            {{
                "status": "need_review",
                "clause_name": "overtime",
                "clause_data": "Extracted contract value"
            }},
            {{
                "status": "need_review",
                "clause_name": "notice_period",
                "clause_data": "Extracted contract value"
            }},
            {{
                "status": "need_review",
                "clause_name": "contract_duration",
                "clause_data": "Extracted contract value"
            }},
            {{
                "status": "need_review",
                "clause_name": "end_of_service_payment",
                "clause_data": "Extracted contract value"
            }},
            {{
                "status": "need_review",
                "clause_name": "non_compete_terms",
                "clause_data": "Extracted contract value"
            }},
            {{
                "status": "need_review",
                "clause_name": "salary_and_payment_terms",
                "clause_data": "Extracted contract value"
            }}
        ]
    }}
    SPECIAL EVALUATION REQUIREMENTS:

    WORKING HOURS:
    Evaluate the extracted Working Hours clause against Rule 8.
    Check whether the stated working hours and the rule's conditions
    are consistent.

    OVERTIME:
    Evaluate the extracted Overtime clause against all three:
    - Rule 7: Overtime Pay.
    - Rule 8: Overtime Hours.
    - Rule 9: Holiday Overtime.

    Check each requirement independently.
    A general statement about overtime payment does not automatically
    satisfy requirements concerning holiday overtime or compensatory leave.

    Do not assign need_review automatically.
    Assign satisfied if all applicable requirements are met.
    Assign need_review if any applicable requirement is violated,
    incomplete, or cannot be verified.

    The statuses in this example illustrate the output structure.
    Determine the actual statuses from the supplied contract data
    and labor law rules.

    Return ONLY valid JSON.
    """

        response = self.model.create_chat_completion(
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=3500,
            response_format={"type": "json_object"}
        )

        result = response["choices"][0]["message"]["content"]

        try:
            return json.loads(result)

        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
            print("Raw response:", result)
            print("\n========== JSON ERROR ==========")
            print("Error:", e)
            print("Line:", e.lineno)
            print("Column:", e.colno)
            print("Character:", e.pos)

            lines = result.splitlines()

            start = max(0, e.lineno - 4)
            end = min(len(lines), e.lineno + 3)

            print("\n========== ERROR CONTEXT ==========")

            for i in range(start, end):
                print(f"{i + 1}: {lines[i]}")

            print("\n========== RESPONSE END ==========")
            print(repr(result[-500:]))

            print("\n========== FINISH REASON ==========")
            print(response["choices"][0].get("finish_reason"))
            return None

        
    def find_results(self,conn,contract_id,contract_content,legal_source_):
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT id, title, source, link
                FROM legal_source
                WHERE enabled = 1
                LIMIT 1
            """)

            legal_source = cursor.fetchone()
            print(legal_source)
            if not legal_source:
                return {
                    "success": False,
                    "error": "No legal source is currently enabled. Please enable a legal source first."
                }

            legal_source_path = legal_source["link"]

            filename = os.path.basename(legal_source_path)

            legal_source_path = os.path.join(
                "rules_as_code",
                filename
            )

            if not os.path.isfile(legal_source_path):
                return {
                    "success": False,
                    "error": "The enabled legal source file was not found."
                }
        except json.JSONDecodeError as e:
            print("Invalid legal source JSON:", e)
            return {
                "success": False,
                "error": "The enabled legal source contains invalid JSON."
            }

        except Exception as e:
            print("find_results error:", e)
            return {
                "success": False,
                "error": str(e)
            }

        with open(legal_source_path, "r", encoding="utf-8") as file:
            rules = json.load(file)

        with open(legal_source_path, "r", encoding="utf-8") as file:
            rules = json.load(file)
        contract_rules = [
            rule for rule in rules
            if rule.get("contract_reviewable") is True
        ]
        finding = self.review_contract(contract_content,contract_rules)
        if finding:
                cursor = conn.cursor()
                finding_json = json.dumps(
                    finding,
                    ensure_ascii=False
                )
                print("########",finding)
                cursor.execute(
                        "INSERT INTO finding (contract_id,finding,final_result) VALUES (%s,%s,%s)",
                                (contract_id,finding_json,"")
                    )
                conn.commit()
                finding_id = cursor.lastrowid
                cursor.close()
                conn.close()
                return finding,finding_id
        return None,None
