from django.apps import AppConfig


# pylint: disable=unused-import
# pylint: disable=import-outside-toplevel
class PropertiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "properties"

    def ready(self):
        import properties.signals
