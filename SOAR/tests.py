import requests

def ping_server():
    try:
        url = "http://localhost:5000/block"
        response = requests.get(url=url)
        if response.status_code == 200:
            print("Server up")
            return 1
        raise Exception("Server down")
    
    except Exception as e:
        print("Server down")
        return 0
    
def check_auth():
    try:
        url = "http://localhost:5000/system_screen"
        response = requests.get(url=url)
        if response.status_code == 401:
            print("Auth up")
            return 1
        raise Exception("Auth down")
    
    except Exception as e:
        print("Auth down")
        return 0
    
def ping_db():
    try:
        url = "http://localhost:5000/dbstatus"
        response = requests.get(url=url)
        if response.status_code == 200:
            print("DB up")
            return 1
        raise Exception("DB down")
    
    except Exception as e:
        print("DB down")
        return 0

def run_tests():
    sum = 0
    print("Starting system testing: \n")
    sum += ping_server()
    sum += check_auth()
    sum += ping_db()
    if sum == 3:
        print("All systems ready!")
        return 1
    return 0



run_tests()
input("Press any key to exit")
