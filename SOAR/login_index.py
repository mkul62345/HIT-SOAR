from startup import init_from_config
from flask import Flask , render_template, request, Response, redirect, send_file
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from db import *
import json
 
UPLOAD_FOLDER = "S:\\SOAR\\Uploads\\" #Change to local 
ALLOWED_EXTENSIONS = {'txt'}



app = Flask(__name__)
cfg_dict = init_from_config()
app.secret_key = "DROR" # Change this to a secure random key in production
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JWT_SECRET_KEY'] = '7$*&?>fhd3433@#4227'  # Change this to a secure random key in production
app.config['MYSQL_HOST'] = cfg_dict.get('HOST')
app.config['MYSQL_USER'] = cfg_dict.get('USER')
app.config['MYSQL_PASSWORD'] = cfg_dict.get('PASSWORD')
app.config['MYSQL_DB'] = cfg_dict.get('DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
jwt = JWTManager(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('login.html')   

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_password(username, password, app.config):
        #if True: #Change this once db is up
            access_token = create_access_token(identity=username)
            return redirect("/system_screen", code=307) #render_template('system_screen.html')
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
    
@app.route('/logger', methods=['GET','POST'])
def received_log():
    if request.method == 'GET':
        return Response(json.dumps(None), status=404, mimetype='application/json') 

    elif request.method == 'POST':
        #Insert log into db    
        hostname = json.loads(request.json["data"])["Event"]["System"]["Computer"] 
        if hostname != None and identify_host(hostname ,app.config):     
            log_into_db(request.json ,app.config)
        else:
            return Response(json.dumps(None), status=400, mimetype='application/json') 

        return Response(json.dumps(None), status=200, mimetype='application/json') 

    
@app.route('/block', methods=['GET','POST'])
def pinged():
    if request.method == 'GET':
        return Response(json.dumps(None), status=200, mimetype='application/json') 
    
    elif request.method == 'POST':
        arg = json.loads(request.form['agent-select'].replace("'",'"'))
        if block_agent(arg['uuid'] ,app.config):
            return redirect("/system_screen", code=307) 

        return Response(json.dumps(None), status=400, mimetype='application/json') 

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


@app.route('/system_screen', methods=['GET','POST'])
#@jwt_required()
def system_screen():
    if request.method == 'GET':
        return Response(json.dumps(None), status=404, mimetype='application/json')  
    if request.method == 'POST':
        result = fetch_agents(app.config)
        return render_template('system_screen.html', headings= ("UUID", "Active"), data = result, options = result)   



@app.route('/plot', methods=['GET','POST'])
#@jwt_required()
def plt():
    if request.method == 'GET':
        filename = 'S:\\HIT-SOAR\\SOAR\\Uploads\\jeff.jpeg' #Change to whatever is needed, placeholder method
        return send_file(filename, mimetype='image/gif')




if __name__ == '__main__':   
    app.run(debug=True, threaded=True)
    
  






