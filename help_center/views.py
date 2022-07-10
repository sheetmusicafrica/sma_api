from rest_framework import viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, generics, views, status

from .models import *
from .serializer import PostSerializer

from musicStore.views import SitePagination



class ManagePost(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = SitePagination
    http_method_names = ['get']


    def get_queryset(self):
        return Post.objects.all().order_by('category')

    def list(self,request):
        posts = []

        query = self.request.query_params.get('query', None)

        all_category = Category.objects.all().order_by("-preference")
        
        for category in all_category:
            category_data = {}
            category_post = Post.objects.filter(category=category)

            if query is not None:
                category_post = category_post.filter(title__icontains=query)

            category_data['category'] = category.name
            category_data['data'] = PostSerializer(category_post, many=True).data

            if len(category_data['data']) != 0:
                posts.append(category_data)

        return Response(posts)



    def perform_create(self, serializer):
        return Response({})

    def destroy(self, serializer,pk=None):
        return Response({})

    def update(self, request, pk=None):
        return Response({})


class Postfeedback(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        form = request.POST
        post = Post.objects.get(pk=int(form['postId']))

        print(form)
        if form['positive'] == 'true':
            post.positive_count += 1
        else:
            post.negative_count += 1
        
        post.save()

        return Response({
            'post':post.id,
            'positive_count':post.positive_count,
            'negative_count':post.negative_count
        })
        

