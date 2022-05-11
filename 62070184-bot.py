import requests
import time

host = "10.0.15.112"
username = "admin"
password = "cisco"
student_id = "62070184"
loopback_name = f"Loopback{student_id}"

access_token = "N2M3NzA4NGItMjhhZC00MWIyLWFhODAtM2UzNzVjMzUyNmQ5MjUzYzIzNGYtOTQy_P0A1_9a8a306f-5965-407f-a4b3-63b85af39c54"
webex_endpoint = "https://webexapis.com/v1/messages"
webex_room_id = "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vZDZjYWMwMjAtOTA1ZS0xMWVjLWIxMzMtMDM5MDgwYWM5Yzdh"

def get_last_webex_message(room_id):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    res = requests.get(f"{webex_endpoint}?roomId={room_id}", headers=headers)
    return res.json().get("items", [{}])[0].get("text", "")

def send_webex_message(room_id, text):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "roomId": room_id,
        "text": text,
    }
    requests.post(f"{webex_endpoint}", headers=headers, json=data)

def get_interface_oper_status(interface_name):
    headers = {
        "Accept": "application/yang-data+json",
        "Content-type": "application/yang-data+json",
    }

    restconf_endpoint = f"https://{host}/restconf/data/ietf-interfaces:interfaces-state/interface={interface_name}/"
    res = requests.get(restconf_endpoint, auth=(username, password), headers=headers, verify=False)
    interface_info = res.json().get("ietf-interfaces:interface", {})
    return interface_info.get("oper-status")

def enable_interface(interface_name):
    headers = {
        "Accept": "application/yang-data+json",
        "Content-type": "application/yang-data+json",
    }

    config_data = {
        "ietf-interfaces:interface": {
            "name": interface_name,
            "type": "iana-if-type:softwareLoopback",
            "enabled": True
        }
    }

    restconf_endpoint = f"https://{host}/restconf/data/ietf-interfaces:interfaces/interface={interface_name}/"
    res = requests.put(restconf_endpoint, json=config_data, auth=(username, password), headers=headers, verify=False)

    if(res.status_code >= 200 and res.status_code <= 299):
        print("STATUS OK: {}".format(res.status_code))
    else:
        print('Error. Status Code: {} \nError message: {}'.format(res.status_code, res.json()))
    return res.status_code >= 200 and res.status_code <= 299

def loop():
    message = get_last_webex_message(webex_room_id)
    print(f"Received message: {message}")
    if message == student_id:
        interface_status = get_interface_oper_status(loopback_name)
        send_webex_message(webex_room_id, f"{loopback_name} - Operational status is {interface_status}")

        if interface_status == "down":
            enable_interface(loopback_name)
            interface_status = get_interface_oper_status(loopback_name)
            status_message = "up again" if interface_status == "up" else "still down"
            send_webex_message(webex_room_id, f"Enable {loopback_name} - Now the Operational status is {status_message}")

while 1:
    loop()
    time.sleep(1)
