# 🔐 CSRF Scanner (Demo Tool)

## 📌 Overview

This project is a ** CSRF scanner** designed to automatically detect potential Cross-Site Request Forgery vulnerabilities in web applications.

The tool combines:

* Automated crawling
* Request interception (via Playwright)
* Heuristic-based detection
* Basic vulnerability classification
* AI-detecting pattern

⚠️ **Important:**
This is a **demo  tool**, built for learning and experimentation purposes. It is **NOT production-ready** and may produce false positives or miss complex cases.

---

## 🚀 Features

### ✅ Automated Crawling

* Recursively crawls target domain
* Indentifying noise patterns
* Filters static resources (JS, CSS, images, etc.)
* Identifies potential state-changing endpoints

### ✅ Request Capture

* Uses Playwright to simulate real user login
* Intercepts authenticated requests (POST)
* Extracts:

  * Headers
  * Cookies
  * Request body

### ✅ CSRF Detection Techniques

* Origin header manipulation
* Content-Type bypass testing
* Token presence detection
* Cross-account token reuse (optional)

### ✅ Heuristic Analysis

* Identifies risky endpoints based on:

  * URL patterns (`delete`, `update`, `change`, etc.)
  * HTML elements (forms, buttons, onclick events)
* Groups similar DOM structures using pattern matching

### ✅ Basic Severity Classification

* CRITICAL / HIGH / MEDIUM / LOW (heuristic-based)

---

## ⚙️ Installation

### Requirements

* Python 3.9+
* Playwright
* Requests
* BeautifulSoup
* ollama (model mistral
* llama (in link : https://github.com/tashfeenahmed/freellmapi?fbclid=IwY2xjawRiSlFleHRuA2FlbQIxMABicmlkETFia3ZRbVlnUVM5RG9Ec2c3c3J0YwZhcHBfaWQQMjIyMDM5MTc4ODIwMDg5MgABHpHMO4pkIiUTCtKT9EAXvw3qmD7EdQy6KxhTkRMbqevqTKHbbG0csYZG8-5U_aem_kvUkBVJblS5obiyEowWsqA#using-the-api)

### Setup

```bash
pip install requests beautifulsoup4 playwright
playwright install
```

---

## 🧪 Usage

```bash
python csrf.py -domain http://target.com -cre
```

### Parameters

* `-domain` → Target URL
* `-cre` → Enable login mode (required for authenticated testing)

### Example flow

1. Enter credentials
2. Tool logs in using Playwright
3. Captures authenticated request
4. Starts crawling & testing
5. Outputs potential CSRF issues

---

## 🔍 Detection Logic (Simplified)

The tool attempts to identify CSRF vulnerabilities by:

1. Replaying captured requests with:

   * Modified `Origin` headers
   * Different `Content-Type`

2. Comparing responses:

   * Status code
   * Response body similarity
   * Behavioral differences

3. Checking:

   * Presence of CSRF tokens
   * Cookie security flags (SameSite, Secure, HttpOnly)

---

## ⚠️ Limitations

This tool is intentionally simplified. Known limitations include:
* ❌ Complex installation
* ❌ No reliable state-change verification (heuristic only)
* ❌ May produce false positives
* ❌ Limited handling of modern frameworks (SPA, GraphQL, etc.)
* ❌ Heavy reliance on pattern matching and heuristics
* ❌ Partial CSRF coverage (does not fully simulate browser behavior)

---

## 🧠 Design Philosophy

This project focuses on:

* Understanding **how CSRF works in practice**
* Building a **custom scanning workflow**
* Exploring **automation in web security testing**

It is NOT meant to replace tools like:

* Burp Suite
* OWASP ZAP

---


---

## 🔒 Disclaimer

This tool is provided for **educational purposes only**.

* Do NOT use it on systems without permission
* The author is not responsible for misuse

---

## 📈 Future Improvements

* Better state-change detection
* Reduce false positives
* Add support for SPA / API-based apps
* Improve request correlation
* Implement scoring system
* Simplize installation and set-up

---

---
## 👨‍💻 Author
# THXY
Cybersecurity Student | Python Learner
---



---

## ⭐ Notes

This is a **demo version** of a CSRF scanner.

The goal is to demonstrate:

* Security understanding
* Automation capability
* Tool-building mindset

Not to provide a fully accurate vulnerability scanner.
