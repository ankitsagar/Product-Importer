# Django imports
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView

# App imports
from .models import Product


class HomePage(TemplateView):
    template_name = "product/homepage.html"

    def get(self, request, **kwargs):
        if Product.objects.all().count():
            return reverse_lazy("product_list")
        else:
            return super().get(request, **kwargs)


class ProductList(ListView):
    model = Product
