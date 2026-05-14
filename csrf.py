import sys
import argparse
from collections import deque
from bs4 import BeautifulSoup
import urllib
from urllib.error import HTTPError,URLError
import requests
from urllib.parse import urlparse, urljoin, urldefrag, parse_qs, urlencode
import re
import time
import gzip
import json
from http.cookies import SimpleCookie
from playwright.sync_api import sync_playwright
from difflib import SequenceMatcher
from urllib.parse import unquote
sys.setrecursionlimit(10000)
from openai import OpenAI
import random

client = OpenAI(
    base_url="http://localhost:3001/v1",
    api_key="freellmapi-3f85121b3474dd22455e2214807bc30eea09bb72c86ab0e1",
)
n=-1
k=0
thinh = []
crawlled_url = []
crawlled_url_prefix=[]
p =[]
pattern = []
batch = []
urlneedtocheck = []
state_changing = []
session = requests.Session()
cookieth = []
parsed_cookies = []
cookie_name=[]
score = {}
ht =-1
vitrigach = []
vitricham = []
csrf_token_exist = False
captured ={}
captured_response = {}
target_request    = None
testcsrf_token = None
user_field = None
authorization_header = None
authcookie=None
pass_field = None
testcookies_dict = {}
login_data = {}
Email = re.compile(r'(username|user|user_name|email|email_address|mail|login|login_id|loginid|account|account_name|member|member_id|userid|user_id|customer|customer_id)', re.I)
Password = re.compile(r'(password|pass|passwd|pwd|passcode|secret|user_password|login_password)', re.I)
checkcookiename = re.compile(r'(session|sessid|sid|auth|token|jwt|connect\.sid|phpsessid|jsessionid|asp\.net_sessionid|authentication|cookie)', re.I)
user_selector = "input[type='email'], input[name*='email'], input[id*='email']"
pass_selector = "input[type='password'], input[name*='pass'], input[id*='pass']"
ONCLICK = ["show(", "hide(", "toggle(", "fadein(", "fadeout(","slideup(", "slidedown(","addclass(", "removeclass(", "toggleclass(","css(", "html(", "text(", "append(", "prepend(","focus(", "blur(", "scrollto(", "scrollintoview(","openmodal(", "closemodal(", "showmodal(","console.log", "alert(","history.back", "history.forward"]
csrf = re.compile(r'(csrf|csrf_token|_csrf|_token|authenticity_token|__requestverificationtoken|verification_token|request_token)', re.I)
action = [
    "action=", "act=", "do=", "cmd=","exec=", "operation=","delete=", "remove=", "update=","add=", "create=", "edit=","confirm=", "reset=", "change=","mode=delete", "type=delete","method=delete", "op=delete","status=active", "status=inactive","enable=", "disable=",]
risky = [
    "delete", "remove", "destroy", "drop", "erase", "wipe","update", "edit", "modify", "patch", "save","create", "add", "insert", "new", "register","logout", "signout", "logoff","login-as", "impersonate","revoke", "invalidate","change-password", "reset-password","change-pass", "reset-pass","set-password", "update-password","change", "set", "apply","confirm", "verify", "approve","reject", "deny", "activate", "deactivate","enable", "disable","update-profile", "edit-profile","change-email", "update-email","change-username","upload", "import", "export","submit", "send","checkout", "purchase", "buy","order", "cancel-order","refund","subscribe", "unsubscribe","add-to-cart", "remove-from-cart","clear-cart","delete-account", "remove-user","ban", "unban","block", "unblock","delete/", "remove/", "update/","create/", "add/",
]
anchor = [
    "learn more","read more","click here","more info","more information","find out more","see more","discover more","view more","explore more","read details","details","learn more about","continue reading","go to","open","here","link","this link","more","view details","see details","check it out","learn","explore"
]
origin_list=["null","http://127.0.0.1"]
content_type=["application/x-www-form-urlencoded",  "multipart/form-data", "text/plain"]
results1 = {}
results2 = {}
results3 = {}
def find_similar_groups(html_list, percent=0.85):
    groups = {}
    used = set()
    k = 1
    for i in range(len(html_list)):
        if i in used:
            continue
        current_group = [html_list[i]]
        used.add(i)
        for j in range(i + 1, len(html_list)):
            if j in used:
                continue

            ratio = SequenceMatcher(
                None,
                str(html_list[i]),
                str(html_list[j])
            ).ratio()
            if ratio >= percent:
                used.add(j)
                current_group.append(html_list[j])
        if len(current_group) >= 2:
            groups[k] = current_group
            k += 1
    return groups


def extract_form_text(form):
    parts = []

    parts.append(form.get_text(separator=" "))

    for inp in form.find_all("input"):
        parts.append(inp.get("name", ""))
        parts.append(inp.get("placeholder", ""))
        parts.append(inp.get("value", ""))

    for btn in form.find_all("button"):
        parts.append(btn.get_text())

    full_text = " ".join(parts).lower()

    keywords = (
        "search", "query", "q=", "page=", "p=", "sort",
        "filter", "view", "lang=", "locale=",
        "category", "tag", "utm_", "ref="
    )

    if form.get("method", "").lower() == "get" and any(k in full_text for k in keywords):
        return False  

    return True  



def onclick(code, domainname):
    code_lower = code.lower()

    urls = re.findall(r'https?://[^"\']+', code_lower)

    for url in urls:
        netloc = urlparse(url).netloc

        if domainname not in netloc:
            return "external"

    return "internal"

def domtree(tag):
    if getattr(tag, "name", None) is None:
        return ""
    result = f"<{tag.name}>"
    for x in tag.children:
        result += domtree(x)
    return result
def isurl(url):
        if "http" in url or "https" in url:
                return True
def head(x):
    n =-1
    for k in x:
        n +=1
        if k == ":":
            header = x[:n]
            return header
def value(x):
    n =-1
    for k in x:
        n +=1
        if k == ":":
            value = x[n+2:]
            return value

def samesite(url, base):
    return urlparse(url).hostname == urlparse(base).hostname    

def is_valid_url(url):
    if url is None:   
        return False
    bad_chars = ["'", '"', "<", ">", "{", "}"]

    for c in bad_chars:
        if c in url:
            return False
    if url.startswith(("javascript:", "mailto:", "tel:", "data:")):
        return False
    if any(ext in url for ext in (".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg",".ico", ".webp", ".woff", ".woff2", ".ttf", ".eot",".mp4", ".mp3", ".wav", ".pdf", ".doc", ".docx", ".ashx", ".xls", ".xlsx", ".ppt", ".zip", ".rar")):
        return False
    return True        

def remove_trailing_slash(url):
    if not url:
        return url
    if url.endswith('/'):
        url = url[:-1]
    return url

def match_pattern(url, patterns):
    u = urlparse(url).path.strip('/').split('/')
    for pattern in patterns:
        p = pattern.strip('/').split('/')
        if len(u) != len(p):
            continue
        matched = True
        for i in range(len(u)):
            if p[i] in ["{var}", "{id}", "{slug}"]:
                continue
            if u[i] != p[i]:
                matched = False
                break
        if matched:
            return True
    return False  

def get_prefix(url):
    path = urlparse(url).path.strip('/').split('/')
    return "/".join(path[:2])

def urlcounter(batch):
    container = {}
    for url in batch:
        k = get_prefix(url)
        container[k] = container.get(k, 0) + 1
    return container
print("Please put your header in a double quotes without <> (ex: -f  \"h1\") ")

parser = argparse.ArgumentParser(description="")
parser.add_argument("-domain", type=str, help="URL to crawl (ex: http://localhost:8000)")
parser.add_argument("-cre", action="store_true", help="Login with username/password")
args = parser.parse_args()
com = args.domain

if args.cre:
    username = input("Please provide your username: ")
    password = input("Please provide your password: ")
    loginurl = input("Please provide your website's login url (ex: https://www.thxy.com/login): ")
    cre2 = input("Do you want to test Shared Session Bug (y/n): ")
    if cre2 == "y":
        username2 = input("Please provide another username: ")
        password2 = input("Please provide another password: ")
    elif cre2 == "n":
        pass
    else:
        print("Please just type y or n")
        sys.exit()


try:
    res = session.get(loginurl, timeout=10)
except requests.exceptions.RequestException as e:
    print("Network error:", e)
bs = BeautifulSoup(res.text, "html.parser")
inputs = bs.find_all("input")
for inp in inputs:
    val = inp.get("id") or inp.get("name")
    if inp.get("id"):
        ht = 1
    if inp.get("name"):
        ht=0

    if Email.search(val):
        user_field = val

    if Password.search(val):
        pass_field = val

'''
zzz=com.split("www.")[1]
domainname=zzz.split(".",1)[0]
'''
zzz="localhost:5000"
domainname = "localhost:5000"
print(domainname)
def handle_route(route):
    global target_request
    req = route.request

    if req.method == "POST" and domainname in req.url:
        if req.post_data is not None:
            decoded = unquote(req.post_data)
            if username in decoded and password in decoded:
                captured["method"]  = req.method
                captured["url"]     = req.url
                captured["headers"] = dict(req.headers)
                captured["body"]    = req.post_data
                target_request      = req

    route.continue_()

def handle_response(res):
    global target_request
    global res_status
    if target_request and res.request == target_request:
        captured_response["status"]  = res.status
        captured_response["headers"] = dict(res.headers)
        try:
            captured_response["body"] = res.text()
        except Exception:
            captured_response["body"] = "(unreadable)"
        print("\n=== STARTING ===")
        res_status =res.status


def get_cookies(x, username, password):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.route("**/*", handle_route)
        page.on("response", handle_response)  

        page.goto(x)
        page.wait_for_load_state("networkidle")
        if ht == 1:
            page.fill(f"#{user_field}", username)

            page.fill(f"#{pass_field}", password)
        if ht == 0:
            page.fill(f"[name='{user_field}']",username)
            page.fill(f"[name='{pass_field}']",password)
        page.click("button[type='submit'], input[type='submit']")  
        page.wait_for_load_state("networkidle")

        
        cookies = context.cookies()
        browser.close()
            
        return cookies




cookies = get_cookies(loginurl, username, password)
cookies_dict = {c["name"]: c["value"] for c in cookies}

 





cap_url = captured.get("url")
cap_headers = dict(captured.get("headers", {}))
for x, y in cap_headers.items():
    if x == "origin":
        parsed_url = urlparse(y)
        if parsed_url.scheme == "https":
            urlll=y.split("https")[1]
            urlll="http"+urlll
            origin_list.append(urlll)
        if parsed_url.scheme == "http":
            urlll=y.split("http")[1]
            urlll="https"+urlll
            origin_list.append(urlll)
        evil_full=parsed_url.scheme+"://"+"evil."+zzz
        evil_full2=parsed_url.scheme+"://"+"localhost."+zzz
        origin_list.append(evil_full)
        origin_list.append(evil_full2)


if "Authorization" in cap_headers:
    print("Authorization headers --> Low csrf potential")
    authorization_header = True
cap_headers.pop("cookie", None)
cap_headers.pop("content-length", None)
cap_body = captured.get("body")
session = requests.Session()
for c in cookies:
    session.cookies.set(
        c["name"],
        c["value"],
        domain=c.get("domain"),
        path=c.get("path")
    )
response = session.post(
    cap_url,
    headers=cap_headers,
    data=cap_body,
    allow_redirects=False,   
)

response_test = {}
response_test["status"] = response.status_code
response_test["headers"] = response.headers

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
    "Accept-Language": "en-US,en;q=0.9",
}
queue = deque([com])
visited = set()

print("[*] Crawlling website")
for round_num in range(3):
    round_num += 1
    results={}
    
    newqueue = deque([])
    same = {}

    while queue:
        x = queue.popleft()

        if x in visited:
            continue
        visited.add(x)

        if match_pattern(x, pattern) == False:
            batch.append(x)
        else:
            continue

        if len(batch) >= 20:
            cont = urlcounter(batch)
            for prefix, count in cont.items():
                if count > 12:
                    for ks in batch:
                        if prefix in ks:
                            urlneedtocheck.append(ks)
                    response_ollama = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "mistral",
                            "prompt": f"""
                                You are a URL pattern detection engine.

                                Task:
                                Extract ONLY dynamic URL patterns.

                                STRICT RULES:
                                - DO NOT include static base paths (e.g. /resources/COVID19/)
                                - ONLY return patterns that contain variables: {{id}}, {{slug}}, {{var}}
                                - NO explanations
                                - NO extra text
                                - NO markdown
                                - NO backticks
                                - ONE pattern per line

                                Valid output example:
                                /a/b/{{id}}
                                /a/b/{{slug}}

                                Now analyze:

                                {urlneedtocheck}
                            """,
                            "stream": False
                        }
                    )
                    raw = response_ollama.json()["response"]
                    new_lines = [line.strip() for line in raw.strip().split('\n') if line.strip()]
                    response_ollama.close()
                    pattern.extend(new_lines)
            batch = []

        try:
            time.sleep(0.3)
            
            resp = session.get(x, headers=headers, timeout=10, allow_redirects=True)
            
            html = resp.text
                
            bs = BeautifulSoup(html, "html.parser")
            parsed_url = urlparse(com)
            com1 = parsed_url.scheme +"://"+ parsed_url.netloc
            repeated = []
            for tag in bs.find_all(True):
                name = tag.name
                if x not in results:
                    results[x] = []
                

                if name in ["input", "textarea", "select"]:
                    if tag.get("type") != "hidden" and tag.get("type") != None:
                        repeated.append(tag)
                        results[x].append({
                            "type": "input",
                            "input_type": tag.get("type"),
                            "name": tag.get("name"),
                            "full_tag":str(tag)
                        })
                if name == "a":
                    text = " ".join(tag.get_text().split())
                    
                    
                    href = tag.get("href")

                    if not href:
                        continue
                    if any(ext in href for ext in (".ashx", ".pdf", ".doc", ".docx", ".xls",".xlsx", ".ppt", ".zip", ".rar", ".mp4", ".mp3", ".png", ".jpg", ".gif", ".svg")):
                        continue
                    if href.startswith(("~/","")):
                        continue
                    if len(href)>120:
                        continue
                    if any(k in text for k in anchor ):
                        continue
                    href2=href.lower()
                    if href2.startswith(("https://","http://","www"))   and not href2.startswith(com1):
                        continue
                    if href2 == "javascript:void(0)" and text == None:
                        continue

                    if any(p in href2 for p in [ "search", "query", "q=","page=", "p=","sort", "filter", "view","lang=", "locale=","category", "tag","utm_", "ref="]):
                        continue
                    if  href2.startswith("#") or href2  in ["javascript:history.back()","javascript:history.forward()","/", "javascript:history.back();","javascript:history.forward();"] or  href2.startswith(("mailto:","tel:","sms:","callto:")) :
                        continue
                    if (any(k in href2 for k in action) or any(k in href2 for k in risky)):
                        repeated.append(tag)

                        results[x].append({
                            "type": "a",
                            "href": href,
                            "text": text,
                            "full_tag":str(tag)
                            })
                if name == "button":
                    text = " ".join(tag.get_text().split())
                    if any(k in text for k in anchor ):
                        continue
                    if not text and not tag.has_attr("onclick") and tag.get("type") != "submit":
                        continue
                    if text.lower() in ["x", "×", "close"]:
                        continue
                    repeated.append(tag)

                    results[x].append({
                        "type": "button",
                        "text": text,
                        "full_tag" : str(tag)
                    })
                if tag.has_attr("onclick"):
                    code = tag.get("onclick")
                    if not code:
                        continue
                    code_lower = code.lower()
                    if any(k in code_lower for k in ONCLICK):
                        continue
                    if onclick(code, com1) == "external":
                        continue
                    repeated.append(tag)

                    results[x].append({
                        "type": "onclick",
                        "code": tag.get("onclick"),
                        "full_tag": str(tag)
                    })
                if bs.find("form"):
                    form = bs.find("form")
                    if extract_form_text(form):
                        results[x].append({
                        "type": "form",
                        "action": tag.get("action"),
                        "method": tag.get("method", "get").lower(),
                        })


                
            if round_num == 1:
                results1 = results
            if round_num ==2:
                results2 = results
            if round_num ==3:
                results3 = results

        except Exception as e:
            print(f"  [Error] {e}: {x}")
            continue


        fp = domtree(bs)
        same[fp] = same.get(fp, 0) + 1
        if same[fp] > 4:
            continue
        for a in bs.find_all("a"):
            href = a.get("href")
            if not href:
                continue
            urll = urljoin(com, href)
            urll = remove_trailing_slash(urldefrag(urll).url)
            if not is_valid_url(urll):
                continue
            if samesite(urll, com) and urll not in visited and isurl(urll):
                newqueue.append(urll)

        for img in bs.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            urll = urljoin(com, src)
            urll = remove_trailing_slash(urldefrag(urll).url)
            if not is_valid_url(urll):
                continue
            if samesite(urll, com) and urll not in visited and isurl(urll):
                newqueue.append(urll)

        for script in bs.find_all("script"):
            source = script.get("src")
            if not source:
                continue
            urll = urljoin(com, source)
            urll = remove_trailing_slash(urldefrag(urll).url)
            if not is_valid_url(urll):
                continue
            if samesite(urll, com) and urll not in visited and isurl(urll):
                newqueue.append(urll)

        for link in bs.find_all("link"):
            href2 = link.get("href")
            if not href2:
                continue
            urll = urljoin(com, href2)
            urll = remove_trailing_slash(urldefrag(urll).url)
            if not is_valid_url(urll):
                continue
            if samesite(urll, com) and urll not in visited and isurl(urll):
                newqueue.append(urll)

        for form in bs.find_all("form"):
            action = form.get("action")
            if not action:
                continue
            urll = urljoin(com, action)
            urll = remove_trailing_slash(urldefrag(urll).url)
            if not is_valid_url(urll):
                continue
            if samesite(urll, com) and urll not in visited and isurl(urll):
                newqueue.append(urll)

        for iframe in bs.find_all("iframe"):
            src3 = iframe.get("src")
            if not src3:
                continue
            urll = urljoin(com, src3)
            urll = remove_trailing_slash(urldefrag(urll).url)
            if not is_valid_url(urll):
                continue
            if samesite(urll, com) and urll not in visited and isurl(urll):
                newqueue.append(urll)

    queue = newqueue
print("[*] Crawlling website finished")
crawlled_url = list(visited)

parsed_url = urlparse(com)
com2 = parsed_url.scheme +"://"+ parsed_url.netloc

crawlled_url_lower=[]

for x in crawlled_url:
    x2= x.lower()
    crawlled_url_lower.append(x2)

def filter_results(results):
    for k, items in results.items():
        new_items = []

        for z in items:
            if "href" in z:
                val = z["href"]
                full_url = urljoin(com2, val).lower().rstrip("/")
                if full_url in crawlled_url_lower:
                    continue
                else:
                    if val in crawlled_url_lower:
                        continue

                
            new_items.append(z)

        results[k] = new_items

    return results
results1=filter_results(results1)
results2=filter_results(results2)
results3=filter_results(results3)

def next_filter_results(results):
    already = set()
    for k, items in results.items():
        new_items = []

        for z in items:
            key = tuple(sorted(z.items()))  # convert dict sang hashable

            if key in already:
                continue

            already.add(key)
            new_items.append(z)

        results[k] = new_items

    return results
results1=next_filter_results(results1)
results2=next_filter_results(results2)
results3=next_filter_results(results3)

def next_next_filter_results(results):
    new_results={}
    for k, items in results.items():
        if items != []:
            new_results[k] = items
    return new_results
results1=next_next_filter_results(results1)
results2=next_next_filter_results(results2)
results3=next_next_filter_results(results3)

results = {}

for d in [results1, results2, results3]:
    for key, value in d.items():
        if key not in results:
            results[key] = value
        else:
            results[key].extend(value)
results=next_next_filter_results(results)
print(results)

in_form = {}
formed = []
for url, items in results.items():
    resp = session.get(url, headers=headers, timeout=10)
    bs = BeautifulSoup(resp.text, "html.parser")
    seen_forms = set()
    for tag in bs.find_all(True):
        name = tag.name
        form = tag.find_parent("form")

        if not form:
            continue
        action = form.get("action") 
        method = form.get("method", "get").lower()
        form_key = f"{url} | {action} | {method}"

        temp = None
        if name in ["input", "textarea", "select"]:

            if tag.get("type") not in ["hidden", None]:

                temp = {
                    "type": name,
                    "input_type": tag.get("type"),
                    "name": tag.get("name")
                }

        elif name == "button":

            text = " ".join(tag.get_text().split())

            temp = {
                "type": "button",
                "text": text
            }

        elif name == "a":

            href = tag.get("href")

            if href:

                text = " ".join(tag.get_text().split())

                temp = {
                    "type": "a",
                    "href": href,
                    "text": text
                }

        elif tag.has_attr("onclick"): 
            code = tag.get("onclick") 
            if code: 
                temp = {"type": "onclick", "code": code}
        if temp and temp in items:

            in_form.setdefault(form_key, []).append(temp)

            formed.append(temp)


        if method == "get" and form_key not in seen_forms:

            seen_forms.add(form_key)

            print(f"[!] Form {form_key} is vulnerable")

not_in_form = {}

for url, items in results.items():

    remaining = []

    for item in items:

        if item.get("type") == "form":
            continue
        if item not in formed:
            if item not in remaining:
                remaining.append(item)
    if remaining:
        not_in_form[url] = remaining

not_in_form = next_filter_results(not_in_form)
not_in_form = next_next_filter_results(not_in_form)

print("formed:", formed)
print("not_in_form:", not_in_form)
print("in_form:", in_form)
not_in_form_list=[]
tags=[]
for z in not_in_form.values():
    for y in z:
        for x,k in y.items():
            if x == "full_tag":
                not_in_form_list.append(k)

similar = find_similar_groups(not_in_form_list)
list_tag_for_AI = []


for group in similar.values():
    list_tag_for_AI.append(group[:3])

AI_pattern=[]

for x in list_tag_for_AI:
    resp = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[
            {
                "role": "user",
                "content": f"""data:\n{json.dumps(x)}"
                Analyze the following HTML tags and generate a generalized structural template.

               Analyze the following HTML tags and generate ONE generalized template.

                Requirements:
                - Preserve the exact HTML structure
                - Replace EVERY dynamic value with ONLY {{dynamic}}
                - Do NOT create custom variable names
                - Do NOT use {{id}}, {{product_id}}, {{text}}, etc.
                - ONLY use {{dynamic}}
                - Keep static parts unchanged
                - Do NOT use regex
                - Return only the final template
                - No explanations
                - No extra text
   
            """    
            
            }
        ]
    )
    AI_pattern.append(resp.choices[0].message.content)

def AI_pattern_match(AI_list, html):
    for template in AI_list:
        pattern = re.escape(template)
        pattern = pattern.replace(
            re.escape("{dynamic}"),
            r"(.+?)"
        )
        if re.fullmatch(pattern, html):
            return True
    return False
seen_pattern=set()
not_in_form_vip={}
for s,z in not_in_form.items():
    for y in z:
        for x,k in y.items():
            if x == "full_tag":
                if AI_pattern_match(AI_pattern,k)==False:
                    not_in_form_vip.setdefault(s, []).append(y)
                if AI_pattern_match(AI_pattern,k):
                    for pattern in AI_pattern:
                        regex = re.escape(pattern)
                        regex = regex.replace(
                            r"\{dynamic\}",
                            r"(.+?)"
                        )
                        if re.fullmatch(regex, k):
                            if pattern not in seen_pattern:
                                not_in_form_vip.setdefault(s, []).append(y)
                                seen_pattern.add(pattern)

                            break
cookies_for_play = []
fake_data = {
    "name": "Nguyen Van A",
    "fullname": "Nguyen Van A",
    "username": "admin123",
    "email": "test@example.com",
    "password": "Password123!",
    "phone": "0901234567",
    "address": "123 Nguyen Van Linh, Da Nang",
    "city": "Da Nang",
    "country": "Vietnam",
    "zipcode": "550000",
    "postal": "550000",
    "company": "Test Company",
    "search": "test",
    "keyword": "test",
    "message": "hello",
    "comment": "test comment",
    "url": "https://example.com",
    "website": "https://example.com",
    "age": "25",
    "quantity": "1",
    "price": "100",
    "amount": "1000"
}
def tag_to_selector(full_tag):
    soup = BeautifulSoup(full_tag, "html.parser")
    tag = soup.find()
    if not tag:
        return None

    if tag.get("onclick"):
        onclick = tag["onclick"].replace('"', '\\"')
        return f'[onclick="{onclick}"]'

    if tag.get("name"):
        return f'[name="{tag["name"]}"]'

    if tag.get_text(strip=True):
        text = tag.get_text(strip=True)
        return f'{tag.name}:has-text("{text}")'

    if tag.get("class"):
        classes = ".".join(tag["class"])
        return f'{tag.name}.{classes}'

    return tag.name
for c in cookies:

    cookies_for_play.append({
        "name": c["name"],
        "value": c["value"],
        "domain": c.get("domain"),
        "path": c.get("path", "/")
    })
for x, y in not_in_form_vip.items():
    with sync_playwright() as ht:
        browser = ht.firefox.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies_for_play)
        page = context.new_page()
        page.goto(x)

        for item in y:
            selector = tag_to_selector(item["full_tag"])
            if not selector:
                continue
            if item["type"] in ["input", "textarea"]:
                text_source = (item.get("text") or item.get("name") or item.get("full_tag")).lower()
                dataa = None
                for key, value in fake_data.items():
                    if key in text_source:
                        dataa = value
                        break
                if dataa:
                    try:
                        page.locator(selector).fill(dataa)
                    except:
                        pass
            elif item["type"] == "select":
                sel = page.locator(selector)
                options = sel.locator("option")
                values=[]
                for i in range(options.count()):
                    value = options.nth(i).get_attribute("value") 
                    if value not in ["", None]: 
                        values.append(value) 
                if values:
                    try:
                        with page.expect_request(lambda req: req.resource_type in ["xhr", "fetch"], timeout=2000) as req_info:
                            sel.select_option(random.choice(values))
                        req = req_info.value
                        if req.method.lower() == "get":
                            print(f"{req.url} is valid")
                    except TimeoutError:
                        pass
            elif item["type"] == "button":
                try:
                    with page.expect_request(lambda req: req.resource_type in ["xhr", "fetch"],timeout=2000) as req_info:
                        page.locator(selector).click()
                    req = req_info.value
                    if req.method.lower() == "get":
                        print(f"{req.url} is valid")
                except TimeoutError:
                    pass

for kk in cookies:
    name = kk.get("name", "")

    if csrf.search(name):
        csrf_token_name = kk.get("name")
        csrf_token_value = kk.get("value")
        csrf_token_exist = True
        break


for zz in cookies:
    cookiename=zz["name"]
    if cookiename not in cookie_name:
        cookie_name.append(cookiename)
        if bool(checkcookiename.search(cookiename)) :
            score[cookiename] = score.get(cookiename, 0) + 4
        cookievalue = zz["value"]
        if zz["value"] == '':
            score[cookiename] = score.get(cookiename, 0) - 10
        if len(zz["value"]) >=100:
            score[cookiename] = score.get(cookiename, 0) + 7
        if zz["secure"] == True:
            score[cookiename] = score.get(cookiename, 0) + 3
        if zz["sameSite"] == "Lax":
            score[cookiename] = score.get(cookiename, 0) + 3
        if zz["sameSite"] == "Strict":
            score[cookiename] = score.get(cookiename, 0) + 2
ln = 0


if authorization_header and csrf_token_exist:
    resp = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[
            {
                "role": "user",
                "content": f"""data:\n{json.dumps(cookie_name)}"
                Task:
                - Identify which name represents an authentication cookie (auth cookie).
                - If none of them is an authentication cookie, return: None

                Rules:
                -Output must not be this {json.dumps(csrf_token_name)}
                - Return ONLY the exact name of the cookie.
                - Do NOT explain.
                - Do NOT add any extra text.
                - Output must be a single value only.
            """    
            
            }
        ]
    )
    authcookie=(resp.choices[0].message.content)
if authorization_header and csrf_token_exist == False:
    resp = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[
            {
                "role": "user",
                "content": f"""data:\n{json.dumps(cookie_name)}"
                Task:
                - Identify which name represents an authentication cookie (auth cookie).
                - If none of them is an authentication cookie, return: None

                Rules:
                - Return ONLY the exact name of the cookie.
                - Do NOT explain.
                - Do NOT add any extra text.
                - Output must be a single value only.
            """    
            
            }
        ]
    )
    authcookie=(resp.choices[0].message.content)
    
for x,y in score.items():
    if x==authcookie and y <=7:
        authcookie== None
if authcookie==None and authorization_header:
    print("This web can not be exploited by this tool because this web use Authorization headers")
    print("  _____ ")
    print(" /     \\")
    print("|  - -  |")
    print("|   ^   |")
    print("|  ___  |")
    print(" \\_____/")
    print("Sorry about this weakness!!!")

    sys.exit()
if authorization_header ==None:
    for x,y in score.items():
        if y > ln and x != csrf_token_name:
            ln = y
            authcookie =x
cap_headers_origin = cap_headers.copy()
for k in origin_list:
    
    cap_headers_origin["origin"]=k
    response2 = session.post(
    cap_url,
    headers=cap_headers_origin,
    data=cap_body,
    allow_redirects=False,   
    )
    response2_test = {}
    response2_test["status"] = response2.status_code
    response2_test["headers"] = response2.headers
    for x, y in response2_test.items():
            if x == "status":
                if y != response.status_code:
                    break
            if x == "headers":
                for m, n in y.items():
                    if m.lower() == "set-cookie":
                        if authcookie in n:
                            print(f"    [!] Origin bypass with {k}")
cap_headers_content = cap_headers.copy()
resp_aca = requests.post(
    com,
    headers={"Origin": "https://evil.com"},
    data="a=1"
)
test_origin = "https://evil.com"
if resp.headers.get("Access-Control-Allow-Origin") != None and resp.headers.get("Access-Control-Allow-Credentials") != None:
    acao = resp.headers.get("Access-Control-Allow-Origin")
    acac = resp.headers.get("Access-Control-Allow-Credentials")

    if acao == "*" and acac == "true":
        print( "    [!] CRITICAL (wildcard + credentials)")

    if acao == test_origin and acac == "true":
        print( "    [!] CRITICAL (reflection)")


if cap_headers_content["content-type"]=="application/json":

    for z in content_type:
        
        
        cap_headers_content["content-type"] = z
        response4 = session.post(
            cap_url,
            headers=cap_headers_content,
            data=cap_body,
            allow_redirects=False,   
        )
        response4_test = {}
        response4_test["status"] = response4.status_code
        response4_test["headers"] = response4.headers
        for x, y in response4_test.items():
                if x == "status":
                    if y != response.status_code:
                        break
                if x == "headers":
                    for m, n in y.items():
                        if m.lower() == "set-cookie":
                            if authcookie in n:
                                print(f"Content bypass with {z}")

for zz in cookies:
    if zz["name"] == authcookie:
                print(f"\n[+] Found auth cookie: {authcookie}")

                secure = zz.get("secure", False)
                httponly = zz.get("httponly", False)
                samesite = zz.get("sameSite", None)
                domain = zz.get("domain", "")
                path = zz.get("path", "")

                issues = []

                if not secure:
                    print("  [-] Missing Secure → Risk of MITM cookie theft")
                else:
                    print("  [+] Secure enabled")

                if not httponly:
                    print("  [-] Missing HttpOnly → Risk of XSS stealing cookie")
                else:
                    print("  [+] HttpOnly enabled")

                if not samesite:
                    print("  [-] Missing SameSite → CSRF risk")
                else:
                    if samesite == "None":
                        print("  [!] SameSite=None → Allows CSRF risk")
                    elif samesite == "Lax":
                        print("  [~] SameSite=Lax → Partial CSRF protection")
                if domain.startswith("."):
                    print(f"  [!] Broad domain scope ({domain}) → Subdomain risk")
                else:
                    print(f"  [+] Restricted domain ({domain})")

                if path != "/":
                    print(f"  [~] Restricted path: {path}")
                else:
                    print("  [+] Path=/")

if csrf_token_exist:
    csrf_token=csrf_token_name+"="+csrf_token_value


if csrf_token_exist == True:
    if cre2 == "y":
        cookies2 = get_cookies(loginurl, username2, password2)
        
        csrf_token_value2 = None
        for kk in cookies2:
            name = kk.get("name", "")
            if csrf.search(name):
                csrf_token_value2 = kk.get("value")

        cookies_dict2 = {c["name"]: c["value"] for c in cookies2}
        cookies_dict2[csrf_token_name] = csrf_token_value  # token user1

        cap_url2 = captured.get("url")
        cap_headers2 = dict(captured.get("headers", {}))
        cap_headers2.pop("cookie", None)
        cap_headers2.pop("content-length", None)
        cap_body2 = captured.get("body")
        
        data_dict = parse_qs(cap_body2)
        data_dict[csrf_token_name] = [csrf_token_value]
        cap_body2_fixed = urlencode(data_dict, doseq=True)

        session2 = requests.Session()
        response3 = session2.post(
            cap_url2,
            headers=cap_headers2,
            cookies=cookies_dict2,
            data=cap_body2_fixed,
            allow_redirects=False,
        )
        response3_test = {}
        response3_test["status"] = response3.status_code
        response3_test["headers"] = response3.headers
        print(response3_test)

        for x, y in response3_test.items():
            if x == "status":
                if y != response.status_code:
                    break
            if x == "headers":
                for m, n in y.items():
                    if m.lower() == "set-cookie":
                        if authcookie in n:
                            print(" CSRF token  cross-account ")
                        else:
                            print(" token is rejected")
