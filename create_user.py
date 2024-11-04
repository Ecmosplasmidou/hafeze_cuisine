from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        print("Error: Username or email already exists.")
    else:
        user = User(username=username, email=email)
        user.set_password(password)
        print(f"Password hash: {user.password_hash}")
        db.session.add(user)
        db.session.commit()
        print("User created successfully!")

        # Test de vérification du mot de passe
        test_password = input("Re-enter password to test verification: ")
        if user.check_password(test_password):
            print("Password verification succeeded!")
        else:
            print("Password verification failed!")