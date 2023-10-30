from .views import app
from .models import graph

# graph.run("CREATE CONSTRAINT FOR (n:User) REQUIRE n.username IS UNIQUE")
# graph.run("CREATE CONSTRAINT FOR (n:Post) REQUIRE n.id IS UNIQUE")
# graph.run("CREATE CONSTRAINT FOR (n:Tag) REQUIRE n.name IS UNIQUE")
# graph.run("CREATE INDEX FOR (p:Post) ON (p.formatted_date)")
