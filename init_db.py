from app import app, db, User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we need to create a test user
        if User.query.filter_by(username='test').first() is None:
            test_user = User(
                username='test',
                password_hash=generate_password_hash('test123')
            )
            db.session.add(test_user)
            db.session.commit()
            print("Created test user (username: test, password: test123)")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 
