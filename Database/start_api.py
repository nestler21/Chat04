import connexion

app = connexion.FlaskApp(__name__, specification_dir='openapi/')
app.add_api('openapi.yaml')
app.run(port=8080)