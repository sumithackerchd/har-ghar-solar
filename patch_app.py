import re
import os

with open("app.py", "r") as f:
    content = f.read()

# Models to add
models_addition = """
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    meta_title = db.Column(db.String(255))
    meta_desc = db.Column(db.String(255))
    category = db.Column(db.String(100))
    tags = db.Column(db.String(255))
    author = db.Column(db.String(100), default="Admin")
    reading_time = db.Column(db.Integer, default=5)
    published_at = db.Column(db.String(50))
    updated_at = db.Column(db.String(50))
    featured_image = db.Column(db.String(300))
    schema_markup = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=True)

"""

# Find the end of models (before global search or error handlers)
model_marker = "# ==========================\n# VENDOR EXTENDED MODELS\n# =========================="
if model_marker in content:
    content = content.replace(model_marker, models_addition + model_marker)
else:
    print("Could not find model marker")

# Routes to add
routes_addition = """
# ==========================
# BLOG ROUTES
# ==========================
@app.route("/blog")
def blog_list():
    page = request.args.get('page', 1, type=int)
    blogs_query = Blog.query.filter_by(is_published=True).order_by(Blog.id.desc())
    blogs = blogs_query.paginate(page=page, per_page=12, error_out=False)
    
    # Sidebar data
    categories = db.session.query(Blog.category, db.func.count(Blog.id)).filter_by(is_published=True).group_by(Blog.category).all()
    popular = Blog.query.filter_by(is_published=True).order_by(db.func.random()).limit(5).all()
    
    return render_template("blog.html", blogs=blogs, categories=categories, popular=popular)

@app.route("/blog/<slug>")
def blog_detail(slug):
    blog = Blog.query.filter_by(slug=slug, is_published=True).first_or_404()
    related = Blog.query.filter(Blog.id != blog.id, Blog.category == blog.category, Blog.is_published == True).limit(3).all()
    return render_template("blog_detail.html", blog=blog, related=related)

@app.route("/blog/category/<category>")
def blog_category(category):
    page = request.args.get('page', 1, type=int)
    blogs_query = Blog.query.filter_by(category=category, is_published=True).order_by(Blog.id.desc())
    blogs = blogs_query.paginate(page=page, per_page=12, error_out=False)
    categories = db.session.query(Blog.category, db.func.count(Blog.id)).filter_by(is_published=True).group_by(Blog.category).all()
    popular = Blog.query.filter_by(is_published=True).order_by(db.func.random()).limit(5).all()
    return render_template("blog.html", blogs=blogs, categories=categories, popular=popular, current_category=category)

@app.route("/blog/tag/<tag>")
def blog_tag(tag):
    page = request.args.get('page', 1, type=int)
    blogs_query = Blog.query.filter(Blog.tags.like(f"%{tag}%"), Blog.is_published==True).order_by(Blog.id.desc())
    blogs = blogs_query.paginate(page=page, per_page=12, error_out=False)
    categories = db.session.query(Blog.category, db.func.count(Blog.id)).filter_by(is_published=True).group_by(Blog.category).all()
    popular = Blog.query.filter_by(is_published=True).order_by(db.func.random()).limit(5).all()
    return render_template("blog.html", blogs=blogs, categories=categories, popular=popular, current_tag=tag)

@app.route("/search")
@app.route("/blog/search")
def blog_search():
    q = request.args.get("q", "").strip()
    page = request.args.get('page', 1, type=int)
    if not q:
        return redirect(url_for('blog_list'))
    
    like_q = f"%{q}%"
    blogs_query = Blog.query.filter(db.or_(Blog.title.like(like_q), Blog.content.like(like_q), Blog.tags.like(like_q)), Blog.is_published==True).order_by(Blog.id.desc())
    blogs = blogs_query.paginate(page=page, per_page=12, error_out=False)
    categories = db.session.query(Blog.category, db.func.count(Blog.id)).filter_by(is_published=True).group_by(Blog.category).all()
    popular = Blog.query.filter_by(is_published=True).order_by(db.func.random()).limit(5).all()
    return render_template("blog.html", blogs=blogs, categories=categories, popular=popular, search_query=q)


# ==========================
# TRUST PAGES & SEO ROUTES
# ==========================
@app.route("/privacy-policy")
def privacy_policy():
    return render_template("trust/privacy.html")

@app.route("/cookie-policy")
def cookie_policy():
    return render_template("trust/cookie.html")

@app.route("/disclaimer")
def disclaimer():
    return render_template("trust/disclaimer.html")

@app.route("/terms")
def terms():
    return render_template("trust/terms.html")

@app.route("/editorial-policy")
def editorial_policy():
    return render_template("trust/editorial.html")

@app.route("/our-mission")
def our_mission():
    return render_template("trust/mission.html")

@app.route("/why-trust-us")
def why_trust_us():
    return render_template("trust/trust_us.html")

@app.route("/how-we-verify")
def how_we_verify():
    return render_template("trust/verify.html")

@app.route("/sitemap.xml")
def sitemap():
    import datetime
    blogs = Blog.query.filter_by(is_published=True).all()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n'
    
    # Static pages
    pages = ['/', '/about', '/services', '/contact', '/blog', '/privacy-policy', '/terms', '/disclaimer', '/cookie-policy', '/editorial-policy', '/our-mission', '/why-trust-us', '/how-we-verify']
    for p in pages:
        xml += '  <url>\\n'
        xml += f'    <loc>https://hargharsolar.duckdns.org{p}</loc>\\n'
        xml += f'    <lastmod>{today}</lastmod>\\n'
        xml += '    <changefreq>weekly</changefreq>\\n'
        xml += '    <priority>0.8</priority>\\n'
        xml += '  </url>\\n'
        
    # Blog posts
    for b in blogs:
        xml += '  <url>\\n'
        xml += f'    <loc>https://hargharsolar.duckdns.org/blog/{b.slug}</loc>\\n'
        date_str = b.updated_at[:10] if b.updated_at else today
        xml += f'    <lastmod>{date_str}</lastmod>\\n'
        xml += '    <changefreq>monthly</changefreq>\\n'
        xml += '    <priority>0.6</priority>\\n'
        xml += '  </url>\\n'
        
    xml += '</urlset>'
    
    from flask import Response
    return Response(xml, mimetype='application/xml')

@app.route("/rss.xml")
def rss_feed():
    import datetime
    from email.utils import formatdate
    blogs = Blog.query.filter_by(is_published=True).order_by(Blog.id.desc()).limit(20).all()
    
    xml = '<?xml version="1.0" encoding="UTF-8" ?>\\n'
    xml += '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\\n'
    xml += '<channel>\\n'
    xml += '  <title>Har Ghar Solar Blog</title>\\n'
    xml += '  <link>https://hargharsolar.duckdns.org/blog</link>\\n'
    xml += '  <description>Latest solar energy news, subsidies, and guides</description>\\n'
    xml += '  <language>en-in</language>\\n'
    xml += '  <atom:link href="https://hargharsolar.duckdns.org/rss.xml" rel="self" type="application/rss+xml" />\\n'
    
    for b in blogs:
        xml += '  <item>\\n'
        xml += f'    <title>{b.title}</title>\\n'
        xml += f'    <link>https://hargharsolar.duckdns.org/blog/{b.slug}</link>\\n'
        xml += f'    <description><![CDATA[{b.meta_desc}]]></description>\\n'
        xml += f'    <category>{b.category}</category>\\n'
        # Approximate pub date
        pub_date = formatdate(timeval=None, localtime=False, usegmt=True)
        xml += f'    <pubDate>{pub_date}</pubDate>\\n'
        xml += f'    <guid>https://hargharsolar.duckdns.org/blog/{b.slug}</guid>\\n'
        xml += '  </item>\\n'
        
    xml += '</channel>\\n</rss>'
    
    from flask import Response
    return Response(xml, mimetype='application/xml')


"""

# Find the end of routes
error_handlers_marker = "# ==========================\n# ERROR HANDLERS\n# =========================="
if error_handlers_marker in content:
    content = content.replace(error_handlers_marker, routes_addition + error_handlers_marker)
else:
    print("Could not find error handlers marker")

with open("app.py", "w") as f:
    f.write(content)

print("app.py patched.")
