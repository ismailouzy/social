import graphene
from graphene_django import DjangoObjectType
from .models import Post


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = ("id", "content", "likes", "created_at")


class Query(graphene.ObjectType):
    posts = graphene.List(PostType)

    def resolve_posts(root, info):
        return Post.objects.all().order_by('-created_at')


class CreatePost(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)

    post = graphene.Field(PostType)

    def mutate(self, info, content):
        post = Post.objects.create(content=content)
        return CreatePost(post=post)


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
