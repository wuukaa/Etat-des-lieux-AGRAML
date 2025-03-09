from website import create_app
import socket


local_hostname = socket.gethostname()
ip_addresses = socket.gethostbyname_ex(local_hostname)[2]
filtered_ips = [ip for ip in ip_addresses if not ip.startswith("127.")]
first_ip = filtered_ips[:1]
ip_locale = first_ip[0]

app = create_app()

if __name__ == '__main__':
    app.run(debug = True, host=ip_locale, port='80')
