# Post Model

# class Post(BaseModel):
#     id: Optional[str]
#     title: str
#     author: str
#     content: Text
#     created_at: datetime = datetime.now()
#     published_at: Optional[datetime]
#     published: bool = False


# posts = []

# @app.get('/posts')
# def get_posts():
#     return posts


# @app.post('/posts')
# def save_post(post: Post):

#     post.id = str(uuid())
#     posts.append(post.dict())
#     return posts[-1]  # -1 devuelve el último item


# @app.get('/posts/{post_id}')
# def get_post(post_id: str):
#     for post in posts:
#         if post["id"] == post_id:
#             return post
#     raise HTTPException(status_code=404, detail="Post not found")


# @app.delete("/posts/{post_id}")
# def delete_post(post_id: str):
#     for index, post in enumerate(posts):
#         if post["id"] == post_id:
#             posts.pop(index)
#             return {"message": "Post has been deleted successfully"}
#     raise HTTPException(status_code=404, detail="Post not found")


# @app.put('/posts/{post_id}')
# def update_post(post_id: str, updatedPost: Post):
#     for index, post in enumerate(posts):
#         if post["id"] == post_id:
#             posts[index]["title"] = updatedPost.title
#             posts[index]["content"] = updatedPost.content
#             posts[index]["author"] = updatedPost.author
#             return {"message": "Post has been updated successfully"}
#     raise HTTPException(status_code=404, detail="Post not found")
