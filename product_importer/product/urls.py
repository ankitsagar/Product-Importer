from django.urls import path

from .views import HomePage, ProductList, ProductImport

app_name = "products"

urlpatterns = [
    path('', HomePage.as_view(), name="homepage"),
    path('products/', ProductList.as_view(), name="product_list"),
    path('import-products/', ProductImport.as_view(), name="product_import"),
]
