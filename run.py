from server import app, db
import config

if __name__ == '__main__':
    # Production mode - run without debug
    with app.app_context():
        db.create_all()
    print(f"Starting {config.APPNAME} in production mode...")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
