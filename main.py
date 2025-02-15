from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug = True, host='10.10.43.182')