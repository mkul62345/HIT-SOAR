from startup import init_from_config
from flask import Flask , render_template, request, Response, redirect, send_file, jsonify, url_for, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from db import *
import json
import datetime
 

ALLOWED_EXTENSIONS = {'txt', 'csv', 'jpeg'}

app = Flask(__name__)
cfg_dict = init_from_config()
app.config['SECRET_KEY'] = cfg_dict.get('SECRET_KEY')   # Change this to a secure random key in production
app.config['UPLOAD_FOLDER'] = cfg_dict.get('UPLOAD_FOLDER')
app.config['JWT_SECRET_KEY'] = cfg_dict.get('JWT_SECRET_KEY')  # Change this to a secure random key in production
app.config['MYSQL_HOST'] = cfg_dict.get('HOST')
app.config['MYSQL_USER'] = cfg_dict.get('USER')
app.config['MYSQL_PASSWORD'] = cfg_dict.get('PASSWORD')
app.config['MYSQL_DB'] = cfg_dict.get('DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=600)
jwt = JWTManager(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('login.html')   

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_password(username, password, app.config):
            access_token = create_access_token(identity=username)
            response = make_response(redirect("/system_screen"))
            response.set_cookie('access_token', access_token)
            return response 
        return render_template('login.html') #Redirect nowhere, render error message

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    elif request.method == 'POST':
        username = request.form['username'] 
        email    = request.form['email']

        if request.form['user_type'] == 'user':          
            password = request.form['password']
            if register_new_user(username, email, "Normal", password, app.config):
                return render_template('login.html')
            return render_template('register.html') #Redirect nowhere, render error message
        
        #elif request.form['user_type'] == 'XXXX':
            # Logic for other user type

@app.route('/change_password', methods=['GET','POST'])
def change_password_():
    if request.method == 'GET':
        return render_template('change_password.html')

    elif request.method == 'POST':
        username     = request.form['username']
        password_old = request.form['currentPassword']
        password_new = request.form['newPassword']
        if validate_password(username, password_old, app.config):
            if change_password(username, password_new, password_old, app.config):
                return render_template('login.html') 
        return render_template('change_password.html') #Redirect nowhere, render error message
    
@app.route('/logger', methods=['POST'])
def received_log():
    if request.method == 'POST':
        #Insert log into db    
        hostname = json.loads(request.json["data"])["Event"]["System"]["Computer"] 
        if hostname != None and identify_host(hostname ,app.config):     
            log_into_db(request.json ,app.config)
        else:
            return Response(json.dumps(None), status=400, mimetype='application/json') 

        return Response(json.dumps(None), status=200, mimetype='application/json') 

@app.route('/block', methods=['GET','POST'])
def block_command():
    if request.method == 'GET':
        return Response(json.dumps(None), status=200, mimetype='application/json')   #Effectively just ping
    
    elif request.method == 'POST':
        if validate_cookie( request.cookies.get('access_token') ,app.config):
            arg = json.loads(request.form['agent-select'].replace("'",'"'))
            if block_agent(arg['uuid'] ,app.config):
                return redirect("/system_screen") 
            return Response(json.dumps(None), status=400, mimetype='application/json') 
        return Response(json.dumps(None), status=401, mimetype='application/json')

@app.route('/system_screen', methods=['GET'])
def system_screen():
    if request.method == 'GET':
        try:
            if validate_cookie( request.cookies.get('access_token') ,app.config):
                result = fetch_agents(app.config)
                return render_template('system_screen.html', headings= ("UUID", "Active"), data = result, options = result) 

        except Exception as e:
            print(f"Error: {e}")
            return Response(json.dumps(None), status=401, mimetype='application/json') 
       
    return Response(json.dumps(None), status=404, mimetype='application/json') 
    
@app.route('/dbstatus', methods=['GET'])
def pingdb():
    if request.method == 'GET':
        if ping_db(app.config):
            return Response(json.dumps(None), status=200, mimetype='application/json')  
      
    return Response(json.dumps(None), status=404, mimetype='application/json') 

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


@app.route('/plot', methods=['GET'])
def plt():
    if request.method == 'GET':
        filename = 'S:\\HIT-SOAR\\SOAR\\Uploads\\jeff.jpeg' #Change to whatever is needed, placeholder method
        return send_file(filename, mimetype='image/gif')




if __name__ == '__main__':   
    app.run(debug=True, threaded=True)
    
  






