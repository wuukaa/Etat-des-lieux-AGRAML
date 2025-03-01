from website import create_app
# import netifaces as ni
# ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
# print(ip)

app = create_app()

if __name__ == '__main__':
    app.run(debug = True, host='10.10.43.182', port='80')
