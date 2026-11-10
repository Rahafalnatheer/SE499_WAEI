from unittest.mock import MagicMock,patch
import unittest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from classes.text_extraction_service import TextExtractionService
from classes.contract import Contract
from classes.rules_manager import RulesManager
from classes.finding import Finding
import server_sprint_2


class TestSecondSprint(unittest.TestCase):
    def setUp(self):
            server_sprint_2.app.config["TESTING"] = True
            self.client = server_sprint_2.app.test_client()
    @patch("classes.text_extraction_service.PdfReader")
    def test_extract_txt_from_pdf(self, replaced_mock_obj):
        p1 = MagicMock()
        p1.extract_text.return_value = "This is fake page 1 content to ignore reading real file"
        p2 = MagicMock()
        p2.extract_text.return_value = "This is fake page 2 content to ignore reading real file"
        replaced_mock_obj.return_value.pages = [p1, p2]
        txt_service = TextExtractionService()
        result = txt_service.extract_text("replaced_fake_file.pdf")
        expected_content = "This is fake page 1 content to ignore reading real file\nThis is fake page 2 content to ignore reading real file\n"
        self.assertEqual(result, expected_content)


    @patch("classes.text_extraction_service.PdfReader")
    def test_extract_fact_from_contract(self, replaced_mock_txt):
        replaced_mock_txt.return_value.extract_text.return_value = (
            "Annual Leave: 20 days"
        )
        contract = Contract()
        result =contract.upload("contract.pdf")
        expected_value = {
            "probation": "six (6) months",
            "annual_leave": "twenty-one (21) days",
            "notice_period": "thirty (30) days",
            "working_hours": "forty-eight (48) hours per week",
            "contract_duration": "two (2) years"
        }
        self.assertEqual(result, expected_value)

    
    def test_extract_rules_info(self):
            text = """
                        RULE 1 - Annual Leave
                        Version: 1.0
                        Description: Employees must receive at least 20 days of annual leave.
                        Fact to extract: annual_leave_days
                        Condition: annual_leave_days >= 20
                    """
            ruleManager = RulesManager()
            result = ruleManager.extract_rules_info(text)
            rule = result[0]["rule"]
            rule_version = result[0]["ruleVersion"]
            self.assertEqual(rule.id, "1")
            self.assertEqual(rule.name, "Annual Leave")
            self.assertEqual(rule.description, "Employees must receive at least 20 days of annual leave.")
            self.assertEqual(rule_version.fact_name, "annual_leave_days")
            self.assertEqual(rule_version.condition, ">=")
            self.assertEqual(rule_version.fact_value, '20')

            

    @patch( "server_sprint_2.get_db_connection")
    def test_find_results(self, mock_conn):
        fact_name = "annual_leave_days"
        fact_value = "20"
        rule_cursor = MagicMock()
        rule_cursor.fetchall.return_value = [("20", ">=")]
        mock_conn.return_value.cursor.return_value = rule_cursor
        finding = Finding()
        result = finding.find_results(mock_conn.return_value,fact_name,fact_value)
        expected = (True, "annual_leave_days", 20.0)
        self.assertEqual(result, expected)

    @patch.object(server_sprint_2, "get_db_connection")
    def test_signup(self, mock_conn):
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
    
            response = self.client.post("/signup", data={
                "fullName": "Reema",
                "id": "112233",
                "mobile": "99887766",
                "email": "reema@gmail.com",
                "pass": "1234",
                "confirm_pass": "1234"
            })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["success"])
    @patch.object(server_sprint_2, "get_db_connection")
    def test_login(self, mock_conn):
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [(1,)]
            mock_conn.return_value.cursor.return_value = mock_cursor

    
            response = self.client.post("/login", data={
                "id": "112233",
                "pass": "1234"
            })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json["success"])

    @patch.object(server_sprint_2, "get_db_connection")
    def test_reset_password(self, mock_conn):
                mock_cursor = MagicMock()
                mock_conn.return_value.cursor.return_value = mock_cursor
                with self.client.session_transaction() as sess:
                    sess["otp"] = "123456"
                response = self.client.post("/reset-password", data={
                                "otp": "123456",
                                "pass": "112233",
                                "id": "1234",
                               
                            })
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json["success"])

if __name__ == "__main__":
    unittest.main()