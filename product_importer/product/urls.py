from django.urls import path

from .views import HomePage, ProductList

app_name = "products"

urlpatterns = [
    path('', HomePage.as_view(), name="homepage"),
    path('products/', ProductList.as_view(), name="product_list"),
]
