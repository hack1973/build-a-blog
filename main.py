import os
import webapp2
import jinja2

from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    #last_modified =dbDateTimeProperty(auto_now = True)

class MainPage(Handler):
    def get(self, title="", body="", error="", blog_id=""):


        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 5")
        self.render("frontpage.html", title = title, body = body, error = error, blogs=blogs)

class NewPost(Handler):
    def render_newpost(self, title="", body="", error=""):
        self.render("newpost.html", title = title, body = body, error = error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = Blog(title = title, body = body)
            b.put()
            blog_id = str(b.key().id())
            self.redirect("/blog"+"/"+blog_id)

        else:
            error = "We need both a Title and a Body to the Blog Post"
            self.render_newpost(title, body, error)

class ViewPostHandler(Handler):
    def get(self, blog_id = "", title = "", body = "", error = ""):

        post = Blog.get_by_id(int(blog_id))

        if post:
            self.render("permalink.html", title = post.title , body = post.body, blog_id = blog_id, error = error)

        else:
            error = "This is not a valid ID, please try again"
            self.render("permalink.html", title = title, body = body, blog_id = blog_id, error = error)

app = webapp2.WSGIApplication([
    ('/blog/?', MainPage),
    ('/blog/newpost', NewPost),
    ('/blog/([0-9]+)', ViewPostHandler)
    ], debug=True)
