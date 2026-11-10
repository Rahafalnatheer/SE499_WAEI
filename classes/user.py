from flask import jsonify
from werkzeug.security import  check_password_hash


class User:
    def __init__(self,fullname,id_number, phone,email,password,otp=None):
        self.fullname=fullname
        self.id_number = id_number
        self.phone=phone
        self.email=email
        self.password=password
        self.otp=otp


    def signup(self,conn):
        cursor = conn.cursor()   
        cursor.execute(
                    "INSERT INTO users (fullname,id_number, phone,email,password) VALUES (%s,%s, %s,%s,%s)",
                                (self.fullname,self.id_number,self.phone,self.email,self.password)
                    )
        conn.commit()
        return jsonify({
                        "success": True,
                        "message": "تم إنشاء الحساب بنجاح"
                    }), 200

    def login(self,conn):
        if self.id_number=="1200000000" and self.password == "admin_123":
               return jsonify({
                                               "id":-1,
                                               "success": True,
                                               "message": ""
                                           }), 200
        cursor = conn.cursor()
        cursor.execute("SELECT id,password FROM users where id_number=%s",(self.id_number,))
        user = cursor.fetchall()
        if user:
            password = user[0][1]
            print(user,password)
            if check_password_hash(password,self.password):
                id = user[0][0]
                return jsonify({
                                "id":id,
                                "success": True,
                                "message": ""
                            }), 200
            else:
                  return jsonify({
                        "success": False,
                        "message":""
                         }), 400 
                  
        else:
            return jsonify({
                                        "success": False,
                                        "message":""
                                    }), 400 
    def reset_password(self,conn):
                    cursor = conn.cursor()   
                    cursor.execute(
                        "UPDATE  users set password=%s where id_number=%s",
                                                        (self.password,self.id_number)
                                            )
                    conn.commit()
                    return jsonify({
                                                "success": True,
                                                "message": "تم بنجاح"
                                            }), 200

    def get_user_by_id(self,id,conn):
            cursor = conn.cursor()
            cursor.execute("SELECT id,id_number,fullname,phone,email FROM users where id=%s",(id,))
            user = cursor.fetchall()
            if user:
                    return jsonify({
                                    "id":user[0][0],
                                    "id_number":user[0][1],
                                    "fullname":user[0][2],
                                    "phone":user[0][3],
                                    "email":user[0][4],
                                }), 200
            return jsonify({
                            "success": False,
                            "message":""
                             }), 400 

    def edit_profile(self,conn,id):
                        cursor = conn.cursor()   
                        cursor.execute(
                            "UPDATE  users set fullname=%s,phone=%s,email=%s where id=%s",
                                                            (self.fullname,self.phone,self.email,id)
                                                )
                        conn.commit()
                        return jsonify({
                                                    "success": True,
                                                    "message": "تم بنجاح"
                                                }), 200

    def list_users(self,conn):
            cursor = conn.cursor()
            cursor.execute("SELECT id,fullname,id_number, phone,email FROM users")
            rows = cursor.fetchall()
            return rows

    def delete_user(self,conn,user_id):
        cursor = conn.cursor()
           
        try:
                   cursor.execute(
                       "DELETE FROM users WHERE id = %s",
                       (user_id,)
                   )
           
                   if cursor.rowcount == 0:
                       conn.rollback()
                       return jsonify({
                           "success": False,
                           "error": "User not found"
                       }), 404
           
                   conn.commit()
           
                   return jsonify({
                       "success": True,
                       "message": "User deleted successfully"
                   }), 200
           
        except Exception as error:
                   conn.rollback()
                   print("Delete user error:", error)
           
                   return jsonify({
                       "success": False,
                       "error": "Unable to delete user. The account may have linked records."
                   }), 409
                      
           