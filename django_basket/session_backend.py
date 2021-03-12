from django.contrib.sessions.backends.db import SessionStore as DbSessionStore
from django.contrib.auth import get_user_model
from .models import get_basket_model
from .contrib import selectors


User = get_user_model()
BasketModel = get_basket_model()

OLD_SESSION = "_old_session"


class SessionStore(DbSessionStore):

    def get_marker(self):
        return self.get(OLD_SESSION, None)

    def set_marker(self, old_session: str):
        """Set old session key marker to session"""
        self[OLD_SESSION] = old_session

    def delete_marker(self):
        del self[OLD_SESSION]

    def cycle_key(self):
        """Actualize cart by session rewriting"""
        # Get session key before cycle process
        old_session_key = self.session_key
        super().cycle_key()
        self.save()
        # Get basket with old session key
        basket = selectors.get_basket(session_id=old_session_key)
        # If exists anonymous user basket will set old session marker in session collection
        if basket and not basket.user:
            self.set_marker(old_session_key)
