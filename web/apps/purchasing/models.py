from django.db import models


from apps.common import models as core_models


class Settings(core_models.AbstractBaseModel):
    def __str__(self):
        return f"Settings for Purchasing app"