from flask import Flask,render_template,request,jsonify,session
from flask_mail import Mail, Message
import mysql.connector
import os
from classes.user import User
from classes.contract import Contract
from classes.finding import Finding
from classes.rules_clauses import RuleClauses
import secrets
from werkzeug.security import generate_password_hash
import re
import datetime
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "waeisupport@gmail.com"
app.config["MAIL_PASSWORD"] = "sfcamvcpmdcahltm"
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]
app.secret_key = "12345678"
mail = Mail(app)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="waei"
    )




@app.route("/send-otp", methods=["POST"])
def send_otp():
    
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "Email is required"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users where email=%s",(email,))
    user = cursor.fetchall()
    cursor.close()
    conn.close()
    if user:
        user_id = user[0][0]
        otp = f"{secrets.randbelow(1000000):06d}"
        session["otp"] = otp
        session["otp_user_id"] = user_id
        session["otp_created_at"] = datetime.datetime.utcnow().timestamp()
        try:
            msg = Message(
                subject="Password Reset OTP",
                recipients=[email],
                body=f"""
                        Hello,

                        Your password reset OTP is: {otp}

                        Please enter it into form with new password.
                        """
                )

            mail.send(msg)
            return jsonify({"message": "OTP sent successfully"}),200

        except Exception as e:
            print(e)
            return jsonify({"error": "Unable to send OTP. Please try again."}), 500


@app.route("/reset-password",methods=["POST"])
def reset_password():
      otp = request.form.get("otp", "").strip()
      new_password = request.form.get("pass", "")
      new_password = generate_password_hash(new_password)
      id_number = request.form.get("id", "").strip()
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute("SELECT id FROM users where id_number=%s",(id_number,))
      user = cursor.fetchall()
      cursor.close()
      conn.close()
      if user:
        user_id = user[0][0]
        if "otp" in session and session["otp"] == otp and session["otp_user_id"] == user_id:
                            otp_created_at = session["otp_created_at"]
                            if otp_created_at and datetime.datetime.utcnow().timestamp() - otp_created_at <= 600:
                                conn = get_db_connection()
                                user=User(id_number=id_number,password=new_password,fullname=None,phone=None,email=None,otp=otp)
                                session.pop("otp", None)
                                session.pop("otp_user_id", None)
                                session.pop("otp_created_at", None)
                                return user.reset_password(conn)
                            return jsonify({
                                                                "success": False,
                                                                "message": "تم بنجاح"
                                                            }), 200
            
        return jsonify({
                                                "success": False,
                                                "message": "خطأ "
                                            }), 400
      return jsonify({
                                                      "success": False,
                                                      "message": "خطأ "
                                                  }), 400
      
     

@app.route("/")
def home():
    return render_template("preview.html")


@app.route("/save_rules_clauses")
def save_rules_clauses():
    ruleClauses = RuleClauses()
    conn = get_db_connection()
    ruleClauses.save_from_legal_source(conn)
    return render_template("preview.html")





@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method=="POST":
        fullName = request.form.get("fullName")
        id = request.form.get("id")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        password = request.form.get("pass")
        confirm_pass = request.form.get("confirm_pass")
        if password == confirm_pass:
            hashed_password = generate_password_hash(password)
            conn = get_db_connection()
            user = User(fullname=fullName,id_number=id,phone=mobile,email=email,password=hashed_password)
            return user.signup(conn)
        
        else:
            return jsonify({
                            "success": False,
                            "message":"خطأ في التسجيل: لم يتم تأكيد كلمة المرور."
                        }), 400

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=="POST":
            id = request.form.get("id")
            password = request.form.get("pass")

            conn = get_db_connection()

            user=User(id_number=id,password=password,fullname=None,phone=None,email=None)
            response, status_code = user.login(conn)
            returned_data = response.get_json()
            if "id" in returned_data:
                session["user_id"] = returned_data["id"]
                print(session["user_id"])
            return response, status_code


@app.route("/get_profile", methods=["GET"])
def get_profile():
    if "user_id" not in session:
       return jsonify({"error": "Unauthorized"}), 401
    if session["user_id"] == -1:
           return jsonify({
                                               "id":-1,
                                               "id_number":"1200000000",
                                               "fullname":"Admin",
                                               "phone":"0000000000",
                                               "email":"admin@gmail.com",
                                           }), 200
    conn = get_db_connection()
    userObj = User(id_number=None,password=None,fullname=None,phone=None,email=None)
    userData,code = userObj.get_user_by_id(session["user_id"],conn)
    return userData,code


@app.route("/edit_profile", methods=["POST"])
def edit_profile():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Unauthorized"
        }), 401

    data = request.get_json(silent=True) or {}

    full_name = (data.get("fullName") or "").strip()
    email = (data.get("email") or "").strip()
    mobile = (data.get("mobile") or "").strip()
    conn = get_db_connection()
    user = User(fullname=full_name,id_number=None,phone=mobile,email=email,password=None)
    return user.edit_profile(conn,session["user_id"])


@app.route("/main_page",methods=["POST","GET"])
def main_page():
    if "user_id" not in session:
                     return jsonify({"error": "Unauthorized"}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select final_result,count(*) from finding,contract,users where " \
                    "contract.id = finding.contract_id and users.id=contract.user_id and users.id=%s " \
                     "group by final_result",(session["user_id"],))

    statistic = cursor.fetchall()
    cursor.close()
    conn.close()
    print(statistic)
    if not statistic:
          return jsonify({
                                               "success": False,
                                               "message": ""
                                           }), 400
          

    
    return jsonify({
                    "success": True,
                    "missed": statistic[0][1],
                    "need review": statistic[1][1],
                    "satisfied": statistic[2][1]

                }), 200

    

@app.route("/upload-contract",methods=["POST","GET"])
def upload_contract():
    if "user_id" not in session:
                     return jsonify({"error": "Unauthorized"}), 401
    if request.method=="POST":
        contract = request.files["contract_file"]
        os.makedirs("contract", exist_ok=True)
        contract_path = os.path.join("contract", contract.filename)
        contract.save(contract_path)

        if contract:

            contract_obj = Contract()
            result = contract_obj.upload_contract(contract_path)
            if not result:
                 return jsonify({
                                     "success": False,
                                     "message": ""
                                 }), 400
            user_id=session["user_id"]
            title = list(result.keys())[0]
            title=result[title]
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                                            "INSERT INTO CONTRACT (user_id,title, path) VALUES (%s,%s, %s)",
                                            (user_id,title, contract_path)
                                        )
            conn.commit()
            contract_id = cursor.lastrowid
            fact_names = []
            fact_values = []
            for res in result:
                if result[res] and res != "Contract Title":
                    fact_names.append(res)
                    fact_values.append(result[res])
                    cursor.execute(
                        "INSERT INTO CONTRACT_CLAUSE (contract_id,fact_name, fact_value) VALUES (%s,%s, %s)",
                                                        (contract_id,res,result[res])
                                                    )
                    conn.commit()
            cursor.close()
            conn.close()
            conn = get_db_connection()
            finding_obj = Finding()
            finding,finding_id = finding_obj.find_results(conn,contract_id,result,"./labor_rules.json") 
            if not finding:
                 return jsonify({
                                                      "success": False,
                                                      "message": ""
                                }), 400
            satisfied = 0
            need_review = 0
            missing = 0

            clauses_names = []
            clauses_data = []
            statuses = []
            
            for k in finding:
                 if k == "clauses":
                      for clause in finding["clauses"]:
                           clauses_names.append(clause["clause_name"])
                           clauses_data.append(clause["clause_data"])
                           statuses.append(clause["status"])
                           if clause["status"] == "satisfied":
                                satisfied +=1
                           if clause["status"] == "need_review":
                                need_review+=1
                           if clause["status"] == "failed":
                                missing+=1
            final_result = ""
            print("3333333",finding)
            if missing>0:
                 final_result = "Missed"
            elif need_review>0:
                 final_result = "Need Review"
            elif satisfied == len(finding["clauses"]):
                 final_result = "Satisfied"

            else:
                 final_result = "Unknown"

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "Update finding set final_result=%s where id=%s",
                                 (final_result,finding_id)
                )
            conn.commit()


            return jsonify({
                "success": True,
                "message": "",
                "clauses_names": clauses_names,
                "clauses_data": clauses_data,
                "statuses": statuses,
                "final_result":final_result
            }), 200


@app.route("/get_my_contracts",methods=["GET"])
def get_my_contracts():
            if "user_id" not in session:
                    return jsonify({
                        "success": False,
                        "error": "Unauthorized"
                    }), 401
            user_id = session["user_id"]
            conn = get_db_connection()
            contract=Contract(user_id = user_id)
            response, status_code = contract.get_my_contract(conn)
            returned_data = response.get_json()
            if "id" in returned_data:
                session["user_id"] = returned_data["id"]
                print(session["user_id"])
            return response, status_code


@app.route("/get_contract_by_id",methods=["GET","POST"])
def get_contract_by_id():
            if "user_id" not in session:
                    return jsonify({
                        "success": False,
                        "error": "Unauthorized"
                    }), 401
            contract_id = request.args.get("contract_id")
            print(contract_id)
            user_id = session["user_id"]
            conn = get_db_connection()
            contract=Contract(user_id = user_id)
            finding, status_code = contract.get_contract_by_id(conn,contract_id)
            print(finding,"############")
            if not finding or status_code != 200:
                    return jsonify({
                                           "success": False,
                                           "error": "Error"
                                       }), 400
            satisfied = 0
            need_review = 0
            missing = 0
            clauses_names = []
            clauses_data = []
            statuses = []
            for k in finding:
                if k == "clauses":
                    for clause in finding["clauses"]:
                                       clauses_names.append(clause["clause_name"])
                                       clauses_data.append(clause["clause_data"])
                                       statuses.append(clause["status"])
                                       if clause["status"] == "satisfied":
                                            satisfied +=1
                                       if clause["status"] == "need_review":
                                            need_review+=1
                                       if clause["status"] == "failed":
                                            missing+=1
            final_result = ""
            if missing>0:
                             final_result = "Missed"
            elif need_review>0:
                             final_result = "Need Review"
            elif satisfied == len(finding["clauses"]):
                             final_result = "Satisfied"
            
            else:
                             final_result = "Unknown"
            
                        
            return jsonify({
                            "success": True,
                            "message": "",
                            "clauses_names": clauses_names,
                            "clauses_data": clauses_data,
                            "statuses": statuses,
                            "final_result":final_result
                        }), status_code


@app.route("/delete_contract", methods=["POST"])
def delete_contract():
    if "user_id" not in session:
                    return jsonify({
                        "success": False,
                        "error": "Unauthorized"
                    }), 401
    data = request.get_json(silent=True) or {}

    contract_id = data.get("contract_id")
    user_id = session.get("user_id")

    

    if not contract_id:
        return jsonify({
            "success": False,
            "message": "Contract ID is required"
        }), 400

    conn = get_db_connection()
    contract=Contract(user_id = user_id)
    return contract.delete_contract(conn,contract_id,user_id)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()

    response = jsonify({
        "success": True,
        "message": "Logged out successfully"
    })

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    return response,200


@app.route("/list_user",methods=["POST","GET"])
def list_user():
    if "user_id"  not in session:
                        return jsonify({
                                                                            "success": False,
                                                                            "error": "Unauthorized"
                                                                        }), 401
    if session["user_id"]!=-1:
                                return jsonify({
                                    "success": False,
                                    "error": "Unauthorized"
                                }), 401
                        
     

     
    
      
    conn = get_db_connection()
    user = User(fullname=None,id_number=None,phone=None,email=None,password=None)
    rows = user.list_users(conn)
    print(rows)
    users = [
            {
                "id": row[0],
                "fullname": row[1],
                "id_number": row[2],
                "phone": row[3],
                "email": row[4]
            }
            for row in rows
        ]

    return jsonify({"success": True, "users": users}), 200

@app.route("/delete_user", methods=["POST"])
def delete_user():

    if session.get("user_id") is None:
        return jsonify({"success": False, "error": "Login required"}), 401

    if session.get("user_id") != -1:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    print(data)
    try:
        user_id = int(data.get("user_id"))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Invalid user ID"
        }), 400

    if user_id == -1:
        return jsonify({
            "success": False,
            "error": "Admin account cannot be deleted"
        }), 400

    conn = get_db_connection()
    user = User(fullname=None,id_number=None,phone=None,email=None,password=None)
    res,code = user.delete_user(conn,user_id)
    return res,code
    



@app.route("/list_legal_source",methods=["POST","GET"])
def list_legal_source():
    if "user_id"  not in session:
                        return jsonify({
                                                                            "success": False,
                                                                            "error": "Unauthorized"
                                                                        }), 401
    if session["user_id"]!=-1:
                                return jsonify({
                                    "success": False,
                                    "error": "Unauthorized"
                                }), 401
                        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,title,source, create_at,enabled FROM legal_source")
    rows = cursor.fetchall()

    encoded_rules_data = [
            {
                "id": row[0],
                "title": row[1],
                "source": row[2],
                "create_at": row[3],
                "enabled": row[4]
            }
            for row in rows
        ]

    return jsonify({"success": True, "encoded_rules_data": encoded_rules_data}), 200
      
@app.route("/add_legal_source", methods=["POST"])
def add_legal_source():

    if "user_id" not in session or session["user_id"] != -1:
        return jsonify({
            "success": False,
            "error": "Unauthorized"
        }), 401

    conn = None
    cursor = None
    saved_path = None

    try:
        title = request.form.get("title", "").strip()
        source = request.form.get("source", "").strip()
        uploaded_file = request.files.get("file")

        if not title or not source or not uploaded_file:
            return jsonify({
                "success": False,
                "message": "Title, source, and file are required."
            }), 400

        if uploaded_file.filename == "":
            return jsonify({
                "success": False,
                "message": "Please select a file."
            }), 400

        allowed_extensions = {"json"}

        original_filename = secure_filename(uploaded_file.filename)

        if (
            "." not in original_filename or
            original_filename.rsplit(".", 1)[1].lower() not in allowed_extensions
        ):
            return jsonify({
                "success": False,
                "message": "Only PDF and DOCX files are allowed."
            }), 400

        # if uploaded_file.content_length and uploaded_file.content_length > 20 * 1024 * 1024:
        #     return jsonify({
        #         "success": False,
        #         "message": "File size cannot exceed 20 MB."
        #     }), 400

        upload_folder = os.path.join(
            app.root_path,
            "rules_as_code"
        )

        os.makedirs(upload_folder, exist_ok=True)

        extension = original_filename.rsplit(".", 1)[1].lower()

        new_filename = f"{uuid.uuid4().hex}.{extension}"

        saved_path = os.path.join(
            upload_folder,
            new_filename
        )

        uploaded_file.save(saved_path)

        file_link = f"/rules_as_code/{new_filename}"

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO legal_source
                (title, source, link, create_at, enabled)
            VALUES
                (%s, %s, %s, NOW(), 0)
        """, (
            title,
            source,
            file_link
        ))

        conn.commit()

        inserted_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "Legal source added successfully.",
            "id": inserted_id
        }), 201

    except Exception as ex:
       
        return jsonify({
            "success": False,
            "message": "Failed to add legal source."
        }), 500



@app.route("/toggle_legal_source", methods=["POST"])
def toggle_legal_source():
    if session.get("user_id") != -1:
        return jsonify({
            "success": False,
            "error": "Unauthorized"
        }), 403

    data = request.get_json(silent=True) or {}

    source_id = data.get("id")
    enabled = data.get("enabled")

    if source_id is None or enabled not in (True, False, 0, 1):
        return jsonify({
            "success": False,
            "error": "Invalid source ID or status"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()

        if bool(enabled):
            cursor.execute("""
                UPDATE legal_source
                SET enabled = 0
            """)

            cursor.execute("""
                UPDATE legal_source
                SET enabled = 1
                WHERE id = %s
            """, (source_id,))

            if cursor.rowcount == 0:
                return jsonify({
                    "success": False,
                    "error": "Legal source not found"
                }), 404

        else:
            cursor.execute("""
                UPDATE legal_source
                SET enabled = 0
                WHERE id = %s
            """, (source_id,))

            if cursor.rowcount == 0:
                return jsonify({
                    "success": False,
                    "error": "Legal source not found"
                }), 404

        conn.commit()

        cursor.execute("""
            SELECT id, title, source, link, create_at, enabled
            FROM legal_source
            ORDER BY id DESC
        """)

        sources = cursor.fetchall()

        return jsonify({
            "success": True,
            "encoded_rules_data": sources
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": "Unable to update legal sources"
        }), 500

    finally:
        cursor.close()
        conn.close()



@app.route("/delete_legal_source", methods=["POST"])
def delete_legal_source():
    if session.get("user_id") != -1:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}

    try:
        source_id = int(data.get("id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid source ID"}), 400

    if source_id <= 0:
        return jsonify({"success": False, "error": "Invalid source ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    file_link = None

    try:
        conn.start_transaction()

        cursor.execute("""
            SELECT id, link
            FROM legal_source
            WHERE id = %s
            FOR UPDATE
        """, (source_id,))

        record = cursor.fetchone()

        if not record:
            conn.rollback()
            return jsonify({
                "success": False,
                "error": "Legal source not found"
            }), 404

        file_link = record["link"]

        cursor.execute("""
            DELETE FROM legal_source
            WHERE id = %s
        """, (source_id,))

        conn.commit()

        if file_link:
            import os
            from urllib.parse import urlparse

            filename = os.path.basename(
                urlparse(file_link).path
            )

            file_path = os.path.join(
                "rules_as_code",
                filename
            )

            if filename and os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print("File cleanup error:", e)

        return jsonify({
            "success": True,
            "message": "Legal source deleted successfully"
        })

    except Exception as e:
        print("Delete legal source error:", e)

        return jsonify({
            "success": False,
            "error": "Unable to delete legal source"
        }), 500

    finally:
        cursor.close()
        conn.close()
if __name__ == "__main__":
    app.run(debug=True)





#check match and contrsact and test several things
#admin