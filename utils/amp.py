import requests

username = "totalfreedom"
password = ""
url = "http://play.totalfreedom.me:8080"

headers = {"Accept":"text/javascript"}
session_id = None

class Paths:
    LOGIN = url + "/API/Core/Login"
    LOGOUT = url + "/API/Core/Logout"
    GET_STATUS = url + "/API/Core/GetStatus"
    class power:
        START = url + "/API/Core/Start"
        RESTART = url + "/API/Core/Restart"
        STOP = url + "/API/Core/Stop"
        KILL = url + "/API/Core/Kill"
    PLAYER_LIST = url + "/API/Core/GetUserList"
    SEND_CONSOLE_COMMAND = url + "/API/Core/SendConsoleMessage"

class States:
    OFFLINE = 0
    PRE_START = 5
    STARTING = 10
    ONLINE = 20
    SHUTTING_DOWN = 30
    SLEEP_PREPARE = 45
    WAITING = 60
    INSTALLING = 70
    FAILED = 100
    SUSPENDED = 200
    MAINTENANCE = 250
    UNKNOWN = 999

class Power:
    START = "start"
    RESTART = "restart"
    STOP = "stop"
    KILL = "kill"

def get_session_id():
    # The API only accepts json in the form of a string for some odd reason
    data = str({"username":username,"password":password,"token":"","rememberMe":"false","SESSIONID":""})
    response = requests.post(Paths.LOGIN, headers=headers, data=data, timeout=5).json()
    global session_id
    session_id = response["sessionID"]

def logout():
    data = str({"SESSIONID": session_id})
    requests.post(Paths.LOGOUT, headers=headers, data=data)

def get_server_state():
    data = str({"SESSIONID":session_id})
    response = requests.post(Paths.GET_STATUS, headers=headers, data=data).json()
    state = response["State"]
    if state == States.OFFLINE:
        return "offline"
    elif state == States.PRE_START:
        return "pre-starting"
    elif state == States.STARTING:
        return "starting"
    elif state == States.ONLINE:
        return "online"
    elif state == States.SHUTTING_DOWN:
        return "shutting down"
    elif state == States.SLEEP_PREPARE:
        return "preparing for sleep-mode"
    elif state == States.INSTALLING:
        return "installing"
    elif state == States.FAILED:
        return "failed"
    elif state == States.SUSPENDED:
        return "suspended"
    elif state == States.MAINTENANCE:
        return "currently under maintenance"
    elif state == States.UNKNOWN:
        return "currently unknown"
    else:
        return str(state)

def control_power(action):
    path = None
    if action == Power.START:
        path = Paths.power.START
    elif action == Power.RESTART:
        path = Paths.power.RESTART
    elif action == Power.STOP:
        path = Paths.power.STOP
    elif action == Power.KILL:
        path = Paths.power.KILL
    data = str({"SESSIONID":session_id})
    requests.post(path, headers=headers, data=data)

def get_player_list():
    data = str({"SESSIONID":session_id})
    response = requests.post(Paths.PLAYER_LIST, headers=headers, data=data).json()
    players = []
    for p in response["result"].values():
        players.append(p)
    if len(players) == 0:
        return "```There are no players online```"
    else:
        return "```{}```".format(", ".join(players))

def send_console_command(command):
    data = str({"SESSIONID":session_id, "message":command})
    requests.post(Paths.SEND_CONSOLE_COMMAND, headers=headers, data=data).json()
