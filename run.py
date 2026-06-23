from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # Ensure database tables exist
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
