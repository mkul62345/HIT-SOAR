import pymysql.cursors
import random
import string
import csv
from argon2 import PasswordHasher, exceptions

UPLOADS_PATH = "S:\\SOAR\\Uploads\\" # Change according to need
SECRET_KEY = '@@##sfasfd321'  # Replace with a strong and unique secret key
TOKEN_EXPIRATION_SECONDS = 3600  # Set the expiration time for the token (e.g., 1 hour)

def connect_to_db(config):
    host = config['MYSQL_HOST']
    user = config['MYSQL_USER']
    password = config['MYSQL_PASSWORD']
    dbname = config['MYSQL_DB']

    # Connect to the database
    db_connection = pymysql.connect(host=host,
                                    user=user,
                                    password=password,
                                    database=dbname,
                                    port=3306,
                                    cursorclass=pymysql.cursors.DictCursor)

    return db_connection

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def validate_password(username, pWord, db_args):
    # Connect to the database
    connection = connect_to_db(db_args)
    try:
        ph = PasswordHasher()
        with connection.cursor() as cursor:           
            # Check if the username and password match a user in the database
            sql = "SELECT password FROM user WHERE username=%s"
            cursor.execute(sql, (username , ))
            pass_hash = cursor.fetchone()
            
            #On success return 1
            if ph.verify(pass_hash['password'], pWord):
                return 1
                

    except (pymysql.Error, exceptions.VerifyMismatchErroras) as e:
        print(f"Error: {e}")
        return 0

    finally:
        if connection:
            connection.close()

def compare_pass_history(username, pWord, ph, connection): #Checks password against current and 2 previous.
    try:
        with connection.cursor() as cursor:           
            # Get current and 2 passwords back and compare the new one to all 3. 
            sqlSelect = "SELECT password FROM user WHERE username=%s"
            cursor.execute(sqlSelect, (username , ))
            pass1 = cursor.fetchone()
            
            sqlUpdate = "SELECT passwordsecond FROM userpass WHERE uname=%s"
            cursor.execute(sqlUpdate, (username, ))
            pass2 = cursor.fetchone()

            sqlUpdate = "SELECT passwordthird FROM userpass WHERE uname=%s"
            cursor.execute(sqlUpdate, (username, ))
            pass3 = cursor.fetchone()
            
            #If we fail validating against all 3, so it means its a new one
            allowedToProceed = False;
            try:
                ph.verify(pass1['password'], pWord)
                return 0
            except exceptions.VerifyMismatchError:
                try:
                    ph.verify(pass2['passwordsecond'], pWord)
                    return 0
                except exceptions.VerifyMismatchError:
                    try:
                        ph.verify(pass3['passwordthird'], pWord)
                        return 0
                    except exceptions.VerifyMismatchError:
                        return 1

    except pymysql.Error as e:
        raise e

def change_password(username, pWord, oldpHash, db_args): # Always call after authentication
    # Connect to the database
    connection = connect_to_db(db_args)
    try:
        ph = PasswordHasher()
        if compare_pass_history(username, pWord, ph, connection):
            with connection.cursor() as cursor:           
                # Check if the username and password match a user in the database
                pHash = ph.hash(pWord)
            
                sqlSelect = "SELECT passwordsecond, passwordthird FROM userpass WHERE uname=%s"
                cursor.execute(sqlSelect, (username , ))
                passwordSecond, passwordThird = cursor.fetchone()
                
                #We discard the 3rd, put the 2nd there.
                passwordThird = passwordSecond
                sqlUpdate = "UPDATE userpass SET passwordthird =%s WHERE uname =%s"
                cursor.execute(sqlUpdate, (ph.hash(passwordThird), username, ))

                #Put current one (pre change) into 2nd.
                passwordSecond = oldpHash
                sqlUpdate = "UPDATE userpass SET passwordsecond =%s WHERE uname =%s"
                cursor.execute(sqlUpdate, (ph.hash(passwordSecond), username, ))
                
                #Update current password with the new password
                sql = "UPDATE user SET password =%s WHERE username =%s"
                if ph.verify(pHash, pWord):
                    cursor.execute(sql, (pHash, username, ))
                    connection.commit()
                    return 1 #"commited update"

    except (pymysql.Error, exceptions.VerifyMismatchErroras) as e:
        print(f"Error: {e}")
        return 0

    finally:
        if connection:
            connection.close()

def register_new_user(username, email, role, pWord, db_args):
    connection = connect_to_db(db_args)
    try:       
        with connection.cursor() as cursor:
            ph = PasswordHasher()
            passHash = ph.hash(pWord)
            sqlInsert = "INSERT INTO user (username, email, role, password) VALUES (%s, %s, %s, %s)"
            values = (username, email, role, passHash)
            cursor.execute(sqlInsert, values)

            sqlCreatePassRecord = "INSERT INTO userpass (uname, passwordsecond, passwordthird) VALUES (%s, %s, %s)"
            dummyHash = ph.hash("XXX") 
            values = (username, dummyHash, dummyHash)
            cursor.execute(sqlCreatePassRecord, values)
        # Commit the changes to the database
        connection.commit()
        return 1 #"User registered successfully!"
        
    except pymysql.Error as e:
        print(f"Error: {e}")
        return 0

    finally:
        if connection:
            connection.close()

def fetch_agents(db_args):
    # Connect to the database
    connection = connect_to_db(db_args)
    try:
        with connection.cursor() as cursor:           
            # Check if the username and password match a user in the database
            sql = "SELECT * FROM agent"
            cursor.execute(sql)
            result = cursor.fetchall()
            
            #On success return 1
            return result
                
    except (pymysql.Error) as e:
        print(f"Error: {e}")
        return None

    finally:
        if connection:
            connection.close()

def log_into_db(data, db_args):
    connection = connect_to_db(db_args)
    try:       
        with connection.cursor() as cursor:
            sqlInsert = "INSERT INTO logs (createdat, logtext) VALUES (%s, %s)"
            values = (data['timestamp'], data['data'])

            cursor.execute(sqlInsert, values)

        # Commit the changes to the database
        connection.commit()
        return 1 #"User registered successfully!"
        
    except pymysql.Error as e:
        print(f"Error: {e}")
        return 0

    finally:
        if connection:
            connection.close()

def identify_host(data, db_args):
    connection = connect_to_db(db_args)
    try:       
        with connection.cursor() as cursor:
            sqlInsert = "SELECT active FROM agent WHERE uuid=%s"
            cursor.execute(sqlInsert, (data , ))
            status = cursor.fetchone()
            if status["active"]:
                return 1

            return 0
        
    except pymysql.Error as e:
        print(f"Error: {e}")
        return 0

    finally:
        if connection:
            connection.close()

def export_logs_csv(db_args):
    # Connect to the database
    connection = connect_to_db(db_args)
    try:
        with connection.cursor() as cursor:           
            # Check if the username and password match a user in the database
            sql = "SELECT * FROM logs"
            cursor.execute(sql)
            results = cursor.fetchall()

            #Getting Field Header names
            column_names = [i[0] for i in cursor.description]
            path = UPLOADS_PATH  + "exported.csv" 
            with open(path, "w") as write_to: 
                result_csv = csv.writer(write_to) #use lineterminator = '\n' for windows 
                result_csv.writerow(column_names)
                for result in results:
                    result_csv.writerow(result.values())

            #On success return 1
            return path            

    except (pymysql.Error) as e:
        print(f"Error: {e}")
        return ""

    finally:
        if connection:
            connection.close()


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////







