# ––– DJANGO IMPORTS
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.views.generic import (
    ListView,
    TemplateView,
)


# ––– THIRD-PARTY IMPORTS
from admin_auto_filters.views import AutocompleteJsonView
from django_filters.views import FilterView


# ––– APPLICATION IMPORTS
from apps.common import filters, models, services


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
# GENERIC / BASE VIEWS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class GenericListView(LoginRequiredMixin, ListView):
    """
    Must override for each view:
    - model

    Override as needed for each view:
    - template_name
    - filter_display
    - filter_by_field
    - filter_by_field_choices
    - filter_by_field_valid_choices
    - exclude_by_field
    - exclude_by_value
    - order_field
    """

    model = models.Placeholder
    template_name = "generics/generic_list.html"
    filter_display = True
    filter_by_field = "category"
    filter_by_field_choices = model.CHOICES
    filter_by_field_valid_choices = []
    exclude_by_field = None
    exclude_by_value = ""
    bulk_create_available = False

    # display session options
    order_by_field = "name"

    def get_context_data(self, **kwargs):
        context = super(GenericListView, self).get_context_data(**kwargs)

        # get naming and url options for list
        context["options"] = get_template_context_options(
            self.model, self.bulk_create_available
        )

        # get filtering, ordering and page size options for list
        filter_by_value, order_by_field, page_size = get_list_display_session_options(
            self.request, self.model, order_by_field=self.order_by_field
        )

        # get queryset
        if filter_by_value != "ALL":
            filter = self.filter_by_field
            qs = self.model.objects.filter(**{filter: filter_by_value})
        else:
            qs = self.model.objects.order_by(order_by_field)
        exclude = self.exclude_by_field
        if exclude:
            qs = qs.exclude(**{exclude: self.exclude_by_value})

        # populate labels and values for filter dropdown
        context["filter_display"] = self.filter_display
        if self.filter_display:
            context["filter_options"] = get_list_filter_options(
                filter_by_value,
                self.filter_by_field,
                self.filter_by_field_choices,
                self.filter_by_field_valid_choices,
            )
        else:
            context["filter_options"] = {"value": "ALL"}

        # pagination
        paginator = Paginator(
            qs,
            page_size,
            orphans=round(page_size / 3, 0),
        )
        page = self.request.GET.get("page", 1)
        try:
            data = paginator.get_page(page)
        except PageNotAnInteger:
            data = paginator.get_page(1)
        except EmptyPage:
            data = paginator.get_page(paginator.num_pages)
        context["data"] = data

        return context


class GenericFilteredListView(LoginRequiredMixin, FilterView):
    """
    Must override for each view:
    - model

    Override as needed for each view:
    - template_name
    - exclude_by_field
    - exclude_by_value
    - order_field
    - filterset_class
    """

    model = models.Placeholder
    template_name = "generic/generic_list_with_filter.html"

    page_size = 10
    exclude_by_field = None
    exclude_by_value = ""
    advanced_search_available = True
    add_available = True
    edit_available = True
    bulk_create_available = False
    edit_via_xlsx = False

    # django-filter for searching
    # filterset_class = None

    # display session options
    order_by_field = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get naming and url options for list
        context["options"] = services.get_template_context_options(
            self.model,
            self.add_available,
            self.edit_available,
            self.bulk_create_available,
            self.edit_via_xlsx,
        )

        # apply filter
        context["filterset"] = self.filterset
        context["filter_applied"] = any(
            field in self.request.GET for field in set(self.filterset.get_fields())
        )

        # pagination
        paginator = Paginator(
            self.filterset.qs,
            self.page_size,
            orphans=round(self.page_size / 3, 0),
        )
        page = self.request.GET.get("page", 1)
        try:
            data = paginator.get_page(page)
        except PageNotAnInteger:
            data = paginator.get_page(1)
        except EmptyPage:
            data = paginator.get_page(paginator.num_pages)
        context["data"] = data

        return context


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