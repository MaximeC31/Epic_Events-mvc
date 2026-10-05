import sentry_sdk
from sqlalchemy.exc import SQLAlchemyError
from monitoring import initialize_sentry
from views.setup_view import show_setup_error
from controllers.main_controller import run

if __name__ == "__main__":

    try:
        initialize_sentry()

    except (RuntimeError, ValueError, SQLAlchemyError) as error:
        sentry_sdk.capture_exception(error)
        show_setup_error("Impossible de démarrer l'application. Vérifiez la configuration Sentry.")
        raise SystemExit(1) from None

    run()
