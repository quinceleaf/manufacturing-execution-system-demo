# ––– DJANGO IMPORTS
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import (
    TemplateView,
)


# ––– PYTHON UTILITY IMPORTS


# ––– THIRD-PARTY IMPORTS


# ––– APPLICATION IMPORTS


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# INDEX
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


# class IndexView(LoginRequiredMixin, TemplateView):
class IndexView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# SESSION / UI
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def ui_toggle_sidebar_pin(request):
    if request.method == "GET":
        current_setting = request.session.get("pin_sidebar", None)
        print(f"current_setting: {current_setting}")
        if current_setting is None or current_setting == False:
            request.session["pin_sidebar"] = True
            message = "Setting [pin_sidebar] set to True"
        else:
            request.session["pin_sidebar"] = False
            message = "Setting [pin_sidebar] set to False"
        data = {"message": message, "is_valid": True}
    else:
        message = "Request not GET"
        data = {
            "message": message,
            "is_valid": False,
        }
    return JsonResponse(data)