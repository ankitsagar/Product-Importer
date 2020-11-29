# Django imports
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView
from django.views.generic.base import View


# App imports
from .models import Product
from .utils import CustomPaginator


class HomePage(TemplateView):
    template_name = "product/homepage.html"

    def get(self, request, **kwargs):
        # If products are there then redirect to list page otherwise ask user
        # to upload products
        if Product.objects.all().count():
            return HttpResponseRedirect(reverse_lazy("products:product_list"))
        else:
            return super().get(request, **kwargs)


class BulkActions(View):
    """ To bulk delete or make inactive/active products. """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        bulk_action = self.request.POST.get('bulk-action')
        # ids of products
        bulk_action_items = self.request.POST.getlist('item_ids[]', [])
        select_across = self.request.POST.get('select_across')

        if select_across:
            products = Product.objects.all()
        else:
            products = Product.objects.filter(id__in=bulk_action_items)

        if bulk_action == "delete":
            self.bulk_delete(products)
        elif bulk_action == "activate":
            self.bulk_change_state(products, True)
        elif bulk_action == "deactivate":
            self.bulk_change_state(products, False)
        return self.redirectresponse_success_url()

    def bulk_delete(self, products):
        products.delete()
        return self.redirectresponse_success_url()

    def bulk_change_state(self, products, is_active):
        products.update(is_active=is_active)
        return self.redirectresponse_success_url()

    def redirectresponse_success_url(self):
        if self.request.GET:
            queryparameter = "?" + self.request.GET.urlencode()
        else:
            queryparameter = ""
        return HttpResponseRedirect(self.success_url + queryparameter)


class ProductList(BulkActions, ListView):
    model = Product
    paginate_by = 20
    paginator_class = CustomPaginator
    success_url = reverse_lazy("products:product_list")

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.order_by("name")
        query = self.request.GET.get("q")
        filter_by = self.request.GET.get("filter_by", "").lower()
        if query:
            # Get all product that has query in name or sku
            qs = qs.filter(
                Q(name__icontains=query) | Q(sku__icontains=query)
            )
        if filter_by == "inactive":
            qs = qs.filter(is_active=False)
        elif filter_by == "active":
            qs = qs.filter(is_active=True)
        return qs
