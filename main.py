from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug = True, port='443', ssl_context='adhoc', host='10.10.10.143')