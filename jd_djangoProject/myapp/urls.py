from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.loginout, name='logout'),

    path('index', views.index, name='index'),

    path('ecommerce_products', views.ecommerce_products, name='ecommerce_products'),
    path('details', views.products_details, name='details'),
    path('ecommerce_comment_list', views.ecommerce_comment_list, name='ecommerce_comment_list'),

    path('widgets/', views.widgets, name='widgets'),
    path('chart', views.chart, name='chart'),
    path('comment_chart', views.comment_chart, name='comment_chart'),

    path('predict', views.predict, name='predict'),
    path('brand_analysis/', views.brand_analysis, name='brand_analysis'),  # 新增这一行
]
