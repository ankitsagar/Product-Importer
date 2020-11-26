from django.urls import path

from product.views import HomePage, ProductList

app_name = "products"

urlpatterns = [
    path('', HomePage.as_view(), name="homepage"),
    path('products/', ProductList.as_view(), name="product_list"),
]
