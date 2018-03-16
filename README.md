# Pager

Pager is a lightweight wrapper around pycurl. It was designed to be used in a pinch (for pretty specific use-cases) and in no way should be considered a serious replacement for pycurl, but rather as a quick prototyping tool.

```python
import pager

wiki = Pager('https://en.wikipedia.org/wiki/Main_Page')
wiki.get('/')
print(wiki.status_code.human, wiki.last_location)
# 200 OK https://en.wikipedia.org/wiki/Main_Page/

page = Pager()
content = page.post('http://www.google.com') # content contains the page source
print(page.status_code, page.last_location)
# 200 http://www.google.com

page.post('http://www.bing.com')
page.get('http://www.yahoo.com')

# sending POST data
poster = Pager('http://www.somewebsite.com')
poster.post('/login.html', postdata='username=Zeus&password=thunderbolt')
# poster now contains the login.html page source
```
