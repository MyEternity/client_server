from core import JIMServer

c = JIMServer()
while True:
    client, client_address = c.socket.accept()
    try:
        msg = c.recv_msg(client)
        print(msg)
    except Exception as E:
        print(f'Recieved error data: {E}')
        client.close()
