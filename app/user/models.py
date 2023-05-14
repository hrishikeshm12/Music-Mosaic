from flask import jsonify, request, session, redirect, flash
from passlib.hash import pbkdf2_sha256
from app import db,user_inter
import uuid

class User:

  def start_session(self, user):
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    return jsonify(user), 200

  def signup(self):
    print(request.form)

    # Create the user object
    user = {
      "_id": uuid.uuid4().hex,
      "fname": request.form.get('fname'),
      "lname": request.form.get('lname'),
      "username": request.form.get('username'),
      "email": request.form.get('email'),
      "password": request.form.get('password')
    }

    # Encrypt the password
    #user['password'] = pbkdf2_sha256.encrypt(user['password'])

    # Check for existing email address
    if db.users.find_one({ "username": user['username'] }):
      return jsonify({ "error": "Username address already in use" }), 400

    if db.users.insert_one(user):
      result=user_inter.insert_one({"user_id": user["_id"], "liked": [], "saved": []})
      if result.acknowledged:
        print("Record added successfully to user interaction also.")
      return self.start_session(user)

    return jsonify({ "error": "Signup failed" }), 400
  



  def signout(self):
    session.clear()
    return redirect('/')
  
  def login(self):

    user = db.users.find_one({
      "username": request.form.get('username')
    })

    if user and (request.form.get('password'), user['password']):
      return self.start_session(user)
    
    return jsonify({ "error": "Invalid login credentials" }), 401

    