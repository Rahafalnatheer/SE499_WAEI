
import json
from flask import jsonify

from llama_cpp import Llama
from huggingface_hub import hf_hub_download

from .text_extraction_service import TextExtractionService


class Contract:

    MODEL_REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"
    MODEL_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"

    def __init__(
        self,
        id=None,
        user_id=None,
        title=None,
        path=None,
        fact_name=None,
        fact_value=None,
        model_path=None
    ):

        self.id = id
        self.user_id = user_id
        self.title = title
        self.path = path
        self.fact_name = fact_name
        self.fact_value = fact_value
        self.text_extraction_service = TextExtractionService()

        if model_path is None:
            model_path = hf_hub_download(
                repo_id=self.MODEL_REPO,
                filename=self.MODEL_FILE
            )


        self.model = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_batch=256,
            n_threads=4,
            n_gpu_layers=-1,
            verbose=False
        )

    def get_my_contract(self,conn):
            cursor = conn.cursor()
            cursor.execute("SELECT contract.id,title,path,created_at,final_result FROM contract,finding where finding.contract_id=contract.id and user_id=%s",(self.user_id,))
            contract = cursor.fetchall()
            if contract:
                    return jsonify({
                                    "contract":contract,
                                    "success": True,
                                    "message": ""
                                }), 200
            else:
                      return jsonify({
                            "success": False,
                            "message":""
                             }), 400 

    def get_contract_by_id(self,conn,id):
                cursor = conn.cursor()
                cursor.execute("SELECT finding FROM finding where finding.contract_id=%s",(id,))
                row = cursor.fetchone()
                cursor.close()

                if not row:
                    return None, 404

                finding = row[0]

                if isinstance(finding, str):
                    finding = json.loads(finding)

                return finding, 200
                      
    def delete_contract(self,conn,contract_id,user_id):
        cursor = conn.cursor()
        try:
                cursor.execute(
                                                          """
                                                          DELETE FROM contract_clause
                                                          WHERE contract_id = %s
                                                          """,
                                                          (contract_id,)
                                                      )
                                                      
                                              
                                    
                                    
                                    
                conn.commit()
                cursor.execute(
                                      """
                                      DELETE FROM finding
                                      WHERE contract_id = %s
                                      """,
                                      (contract_id,)
                                  )
                                  
                          
                conn.commit()
                            
                cursor.execute(
                      """
                      DELETE FROM contract
                      WHERE id = %s AND user_id = %s
                      """,
                      (contract_id, user_id)
                  )
                  
          
                conn.commit()
                 
                return jsonify({
                      "success": True,
                      "message": "Contract deleted successfully"
                  }), 200
          
        except Exception as error:
                print(error)
          
                return jsonify({
                      "success": False,
                      "message": "Unable to delete contract"
                  }), 500
          









    def upload_contract(self, path):
        contract = self.text_extraction_service.extract_text(path)
        if contract == "" or not contract:
            return None
        # return {'Contract Title': "Contract 1",
        #         'Probation Period': 'ninety (90) days starting from the first working day',
        #         'Annual Leave': 'twenty-one (21) days of paid annual leave for each year of service, increasing to thirty (30) days after five (5) consecutive years of service',
        #         'Working Hours': 'eight (8) hours per day and forty-eight (48) hours per week, distributed over six (6) working days',
        #         'Overtime': "any hours exceeding the applicable statutory working-hour limits shall be treated as overtime, with additional payment of fifty percent (50%) of the employee's basic hourly wage for each overtime hour",
        #         'Notice Period': 'sixty (60) days when notice is given by the employer for an employee paid monthly, thirty (30) days when notice is given by the employee',
        #         'Contract Duration': 'two (2) years, commencing on 1 January 2027 and ending on 31 December 2028',
        #         'End-of-Service Payment': "half a month's wage for each of the first five (5) years of service, one month's wage for each subsequent year of service",
        #         'Non-Compete Terms': "for a period of twelve (12) months following termination of employment, the employee shall not engage in activities that directly compete with the employer's software development business within Riyadh, Saudi Arabia",
        #         'Salary and Payment Terms': "SAR 7,000 basic salary, SAR 2,000 housing allowance, SAR 1,000 transportation allowance, total monthly salary SAR 10,000, paid monthly through bank transfer to the employee's registered bank account, payment made on the twenty-seventh (27th) day of each calendar month"
        #         }
        prompt = f"""
                You are an information extraction system for Saudi Arabian employment contracts.

                Extract the nine specified concepts from the contract.

                Rules:
                1. Extract only information explicitly stated in the contract.
                2. Never infer missing information or use external legal knowledge.
                3. Return null for unavailable fields.
                4. Preserve original values, units, and meaning.
                5. Include exact supporting contract text in evidence.
                6. Do not evaluate legal compliance.
                7. Return only valid JSON matching the supplied schema.

                CONTRACT TITLE EXTRACTION:

                - Extract the main title or heading appearing at the beginning
                of the contract document.
                - Do not use the employer name or employee name as the title.
                - Preserve the original title exactly as written.
                - If no identifiable document title exists, return null.
                - Never return placeholder text such as "Contract title or No title".

                Extract:
                1. Contract title
                2. Probation period
                3. Annual leave
                4. Working hours
                5. Overtime
                6. Notice period
                7. Contract duration
                8. End-of-service payment
                9. Non-compete terms
                10. Salary and payment terms

                [JSON schema]

                Contract:
                {contract}
                """


        messages = [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]


        response = self.model.create_chat_completion(
                    messages=messages,
                    temperature=0.0,
                    max_tokens=600,
                    response_format={
                        "type": "json_object"
                    }
                )

        result = response["choices"][0]["message"]["content"]

        try:

                    result = json.loads(result)

        except json.JSONDecodeError as e:

                    print(e)

        return result







# ###NO NEEDED
#     def upload(self, path):
#         contract = self.text_extraction_service.extract_text(path)
#         if contract == "" or not contract:
#             return None
#         return { "probation": "six (6) months",
#                     "annual_leave": "twenty-one (21) days",
#                     "notice_period": "thirty (30) days",
#                     "working_hours": "forty-eight (48) hours per week",
#                     "contract_duration": "two (2) years"}

  
#         prompt = f"""
# You are a legal contract information extraction system.

# Read the following employment contract and extract all facts
# explicitly available in the document.

# Extract information including:

# 1. probation
# 2. annual_leave
# 3. notice_period
# 4. working_hours
# 5. contract_duration

# Also identify any other relevant employment contract facts.

# Return ONLY valid JSON.

# Use this structure:

# {{
#     "probation": null,
#     "annual_leave": null,
#     "notice_period": null,
#     "working_hours": null,
#     "contract_duration": null
# }}

# Rules:

# - Extract only facts explicitly stated in the contract.
# - Do not invent or assume information.
# - If a fact is absent, return null.
# - Preserve numerical values and their units.
# - Additional explicitly stated facts may be included.
# - Use strings for extracted values.
# - Use null for missing information.

# Contract:

# {contract}
# """

#         messages = [
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ]


#         response = self.model.create_chat_completion(
#             messages=messages,
#             temperature=0.0,
#             max_tokens=600,
#             response_format={
#                 "type": "json_object"
#             }
#         )

#         result = response["choices"][0]["message"]["content"]

#         try:

#             result = json.loads(result)

#         except json.JSONDecodeError as e:

#             print(e)

#         return result