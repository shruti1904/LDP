from django.conf.urls import url

from . import views

app_name = 'LDA'
urlpatterns = [
	url(r'^$', views.index, name = 'index'),
	url(r'^graph/', views.graph, name = 'graph'),
	url(r'^toggle/', views.toggle, name = 'toggle'),
	url(r'^Login/', views.login, name = 'Login'),
	url(r'^SignUp/', views.signup, name = 'Sign Up'),
	url(r'^logout/', views.logout, name = 'Logout'),
	url(r'^Transformer/', views.getTransformer, name = 'Transformer'),
	url(r'^Building/', views.getBuilding, name = 'Building'),
	

]