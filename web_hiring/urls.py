from django.urls import path, include
from web_hiring import views

app_name = 'web_hiring'

urlpatterns = [
    path('search/', views.SearchResultsView.as_view(), name='post_search'),
    path('',views.PostListView.as_view(),name='post_list'),
    path('about/',views.AboutView.as_view(),name='about'),
    path('post/<int:pk>/',views.PostDetailView.as_view(),name='post_detail'),
    path('post/new/',views.CreatePostView.as_view(),name='post_new'),
    path('post/<int:pk>/edit/',views.PostUpdateView.as_view(),name='post_edit'),
    path('post/<int:pk>/remove/',views.PostDeleteView.as_view(),name='post_delete'),
    path('drafts/',views.DraftListView.as_view(),name='draft_list'),
    path('published/',views.PublihedListView.as_view(),name='published_list'),
    path('post/<int:pk>/publish/',views.post_publish,name='post_publish'),
]
