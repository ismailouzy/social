import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
import graphql_jwt
from .models import Post, Comment


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("id", "text", "created_at", "user", "post")


class CreateComment(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        post_id = graphene.Int(required=True)
        text = graphene.String(required=True)

    def mutate(self, info, post_id, text):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required!")
        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(post=post, user=user, text=text)
        return CreateComment(comment=comment)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class PostType(DjangoObjectType):
    like_count = graphene.Int()

    class Meta:
        model = Post
        fields = ("id", "content", "created_at", "comments", "like_count")

    def resolve_like_count(self, info):
        return self.like_count


class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=False)

    def mutate(self, info, username, password, email=None):
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return RegisterUser(user=user)


class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    me = graphene.Field(UserType)

    def resolve_posts(root, info):
        return Post.objects.all().order_by('-created_at')

    def resolve_me(root, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")
        return user


class CreatePost(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)

    post = graphene.Field(PostType)

    def mutate(self, info, content):
        if info.context.user.is_anonymous:
            raise Exception("Authentication required!")
        post = Post.objects.create(content=content)
        return CreatePost(post=post)


class LikePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required!")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise Exception("Post not found")


        if user in post.likes.all():

            post.likes.remove(user)
        else:
            post.likes.add(user)

        return LikePost(post=post)


class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    create_post = CreatePost.Field()
    create_comment = CreateComment.Field()
    like_post = LikePost.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
