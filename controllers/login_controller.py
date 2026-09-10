from views.login_view import show_login_form


def run_login():
    email, password = show_login_form()
    print(f"Email: {email}")
