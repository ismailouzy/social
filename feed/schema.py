import graphene
from graphene_django import DjangoObjectType
from django.db.models import Count, Q
from django.contrib.auth.models import User
from .models import Post, Comment, Interaction
import graphql_jwt


# ------------------ Types ------------------
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("id", "text", "user", "created_at")


class PostType(DjangoObjectType):
    like_count = graphene.Int()
    share_count = graphene.Int()

    class Meta:
        model = Post
        fields = ("id", "content", "created_at", "comments", "like_count", "share_count")

    def resolve_like_count(root, info):
        return root.interactions.filter(type="like").count()

    def resolve_share_count(root, info):
        return root.interactions.filter(type="share").count()


# ------------------ Queries ------------------
class Query(graphene.ObjectType):
    posts = graphene.List(PostType)

    def resolve_posts(root, info):
        return Post.objects.annotate(
            like_count=Count("interactions", filter=Q(interactions__type="like")),
            share_count=Count("interactions", filter=Q(interactions__type="share"))
        ).all()


# ------------------ Mutations ------------------
class CreatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        content = graphene.String(required=True)

    def mutate(self, info, content):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required!")
        post = Post.objects.create(content=content)
        return CreatePost(post=post)


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


class LikePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required!")
        post = Post.objects.get(id=post_id)

        interaction, created = Interaction.objects.get_or_create(
            post=post, user=user, type=Interaction.LIKE
        )
        if not created:
            interaction.delete()  # toggle unlike

        return LikePost(post=post)


class SharePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required!")
        post = Post.objects.get(id=post_id)

        Interaction.objects.get_or_create(post=post, user=user, type=Interaction.SHARE)
        return SharePost(post=post)


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    create_comment = CreateComment.Field()
    like_post = LikePost.Field()
    share_post = SharePost.Field()

    # Authentication Mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
