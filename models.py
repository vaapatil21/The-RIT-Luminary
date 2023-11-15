from py2neo import Graph, Node, Relationship, NodeMatcher
from passlib.hash import bcrypt
from datetime import datetime
import uuid


graph = Graph("bolt://localhost:7687", auth=("vaishnavi", "vaishnavi"))

class User:
     def __init__(self,username):
         self.username = username

     def find(self):
         query = f"MATCH (user:User {{username: '{self.username}'}}) RETURN user"
         result = graph.run(query).data()
         return result[0]["user"] if result else None

     def register(self,password):
        if not self.find():
            user = Node("User",username = self.username ,password = bcrypt.encrypt(password))
            #user = Node("User", username=self.username, passowrd=password)
            graph.create(user)
            return True
        return False

     def verify_password(self,password):
         user = self.find()
         if not user :
             return False
         return bcrypt.verify(password,user['password'])


     def add_post(self, title, tags, text):

         user = self.find()
         timestamp = int(datetime.now().timestamp())
         formatted_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

         post = Node(
             "Post",
             id=str(uuid.uuid4()),
             title=title,
             text=text,
             timestamp=timestamp,
             formatted_date=formatted_date
             # timestamp=int(datetime.now().timestamp()),
             # formatted_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

         # timestamp=int(datetime.now().timestamp()),
             # formatted_date=datetime.fromtimestamp(datetime).strftime("%Y-%m-%d")

         )

         rel = Relationship(user, "PUBLISHED", post)
         graph.create(rel)

         tags = [x.strip() for x in tags.lower().split(",")]
         tags = set(tags)

         for tag in tags:
             # Try to find an existing Tag node with the given name
             query = f"MATCH (tag:Tag) WHERE tag.name = '{tag}' RETURN tag"
             result = graph.run(query).data()
             if result:
                 # Use the existing Tag node
                 t = result[0]['tag']
                 rel = Relationship(t, "TAGGED", post)
                 graph.create(rel)
             else:
                 # Create a new Tag node if it doesn't exist
                 t = Node("Tag", name=tag)
                 graph.create(t)
                 rel = Relationship(t, "TAGGED", post)
                 graph.create(rel)


     def like_post(self, post_id):
         user = self.find()

         matcher = NodeMatcher(graph)
         post = matcher.match("Post", id=post_id).first()

         rel = Relationship(user, "LIKES", post)
         graph.merge(rel)



     def recent_posts_user(self, n):
         query = """
         MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
         WHERE user.username = $username
         RETURN post, COLLECT(tag.name) AS tags
         ORDER BY post.timestamp DESC LIMIT $n
         """
         return graph.run(query, username=self.username, n=n)

     def similar_users(self, n):
         query = """
         MATCH (user1:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
               (user2:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
         WHERE user1.username = $username AND user1 <> user2
         WITH user2, COLLECT(DISTINCT tag.name) AS tags, COUNT(DISTINCT tag.name) AS tag_count
         ORDER BY tag_count DESC LIMIT $n
         RETURN user2.username AS similar_user, tags
         """
         return graph.run(query, username=self.username, n=n)

     def commonality_of_user(self, user):

         query1 = """
         MATCH (user1:User)-[:PUBLISHED]->(post:Post)<-[:LIKES]-(user2:User)
         WHERE user1.username = $username1 AND user2.username = $username2
         RETURN COUNT(post) AS likes
         """

         likes = graph.run(query1, username1=self.username, username2=user.username).data()[0]["likes"]
         likes = 0 if not likes else likes
         print(likes)

         query2 = """
         MATCH (user1:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
               (user2:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
         WHERE user1.username = $username1 AND user2.username = $username2 
         RETURN COLLECT(DISTINCT tag.name) AS tags 
         """

         tags = graph.run(query2, username1=self.username, username2=user.username).data()[0]["tags"]
         print(tags)

         return {"likes": likes, "tags": tags}

     def find_post(self, post_id):
         query = f"""
         MATCH (user:User)-[:PUBLISHED]->(post:Post)
         WHERE user.username = $username AND post.id = $post_id
         RETURN post
         """
         result = graph.run(query, username=self.username, post_id=post_id).data()
         return result[0]["post"] if result else None

     def delete_post(self, post_id):
         found_post = self.find_post(post_id)
         if found_post:
             cypher_query = f"""
             MATCH (author:User)-[relationship:PUBLISHED]->(target_post:Post)
             WHERE author.username = $current_user AND target_post.id = $post_id
             DETACH DELETE target_post
             """
             graph.run(cypher_query, current_user=self.username, post_id=post_id)


def search_by_tags(tags):
    query = """
    MATCH (post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE tag.name IN $tags
    RETURN DISTINCT post.title AS title, post.tags AS tags, post.text AS text
    """
    posts = graph.run(query, tags=tags).data()
    return posts



def recent_post(n):
    timestamp = int(datetime.now().timestamp())
    today = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

    query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE post.formatted_date = $today
        RETURN user.username AS username, post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp DESC LIMIT $n
        """

    print(today)
    # today = datetime.now().strftime("%F")
    return graph.run(query, today=today, n=n)

