# ––– DJANGO IMPORTS
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
)


# ––– PYTHON UTILITY IMPORTS


# ––– THIRD-PARTY IMPORTS


# ––– APPLICATION IMPORTS


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# INDEX
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())
