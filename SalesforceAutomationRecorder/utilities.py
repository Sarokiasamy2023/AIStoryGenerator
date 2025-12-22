from playwright.sync_api import sync_playwright
import random

OUT = "fields"  

"""
Return innermost text for a salesforce omniscript html element
"""

def navigate_to_form(page, url, username, password, form_name):
    # 1) Go to base URL (it will auto-redirect to login)
    page.goto(url, wait_until="networkidle")

    # 2) Login page – adjust selectors after you inspect with dev tools
    print(" On log-in page...")
    page.wait_for_load_state("networkidle")
    page.locator('input[placeholder="Username"]').fill(username)
    page.locator('input[placeholder="Password"]').fill(password)
    page.locator('button:has-text("Log in")').click(force=True)
    print(" Logged in...")

    # 3) Banner agreement page – toggle “I Agree” then click Next
    # Use role/text selectors because Salesforce often changes IDs
    page.wait_for_load_state("networkidle")
    page.locator("input[type='checkbox']").click(force=True)
    page.locator("button:has-text('Next')").click(force=True)
    print(" Agreed to banner agreement...")
    
    
    # 3.1) Click finish
    page.wait_for_load_state("networkidle")
    page.locator("button:has-text('Finish')").click(force=True)
    print(" Now entering homepage...")

    
    # 4) Home page -> click “HSD PERFORMANCE REPORTS”
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(10_000)
    page.locator("span:has-text('HSD Performance Reports')").click(force=True)
    print(" Clicked HSD Performance Reports...")


    # 5) Click specific report row “HSD-01078”
    page.wait_for_load_state("networkidle", timeout=100000)
    page.locator(f"a[title='{form_name}']").click(force=True)
    print(f" Clicked on form {form_name}")
    
    # 6) Click Edit on the report
    page.wait_for_load_state("networkidle")
    page.locator("a:has-text('Edit')").click(force=True)
    print(" Clicked 'Edit Form'...")
    
    # 7) Go into the actual form – click “Next” on intro/steps pages
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("button span.btnLabel:has-text('Next')", timeout=100000).click(force=True)
    print(" Loading into the form...")
    
    # get all input textarea and select elements from div.cCenterPanel[tabindex='-1']
    page.wait_for_selector("div.cCenterPanel fieldset", timeout=100000)
    print(" WE ARE IN THE FORM...")
    return page

def get_innermost_text(locator, ret=""):
    count = locator.count()

    for i in range(count):
        curr = locator.nth(i)
        tag_name = curr.evaluate("curr => curr.tagName").lower()
        inner_text = curr.inner_text()
        children = curr.locator(":scope > *")
        if inner_text and children.count() == 0:
            inner_text = inner_text.split("\n")
            for line in inner_text:
                ret += line + "\n"
        else:
            ret += get_innermost_text(children, ret)
        return ret

"""
Write the innermost text for a salesforce omniscript html element
"""
def write_innermost_text(locator, depth=0, filename="output.html"):
    count = locator.count()

    for i in range(count):
        curr = locator.nth(i)
        inner_text = curr.evaluate("""
        el => {
            let text = "";
            for (const node of el.childNodes) {
                if (node.nodeType === Node.TEXT_NODE) {
                    text += node.textContent;
                }
            }
            return text;
            }"""
        )
    children = curr.locator(":scope > *")
    if inner_text and children.count() == 0:
        inner_text = inner_text.split("\n")
        with open(filename, "a", encoding="utf8") as f:
            for line in inner_text:
                f.write(" "*(depth+1) + line + "\n")
            f.close()
    else:
        write_innermost_text(children, depth, filename)

"""
Write the entire HTML of an HTML element until its furthest depth
"""
def html_dump(locator, depth=0, filename="html_dump.html"):
    count = locator.count()

    for i in range(count):
        curr = locator.nth(i)

        # write opening tag
        tag_name = curr.evaluate("curr => curr.tagName").lower()
        tag = " " * (depth * 2) + "<" + tag_name
        attrs = curr.evaluate("""
            curr => {
                const attrs = curr.attributes
                const ret = {}
                for(const attr of attrs){
                    ret[attr.name] = attr.value
                }
                return ret
            }
        """)
        for name, value in attrs.items():
            tag += " " + name
            tag += "=\'" + value + "\'" if value else ""
        tag += ">\n"
        with open(filename, "a", encoding="utf8") as f:
            f.write(tag)
            f.close()
        
        # write inner text
        # write inner text (only direct text nodes)
        inner_text = curr.evaluate("""
            el => {
                let text = "";
                for (const node of el.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        text += node.textContent;
                    }
                }
                return text;
            }
        """)
        if inner_text:
            inner_text = inner_text.split("\n")
            with open(filename, "a", encoding="utf8") as f:
                for line in inner_text:
                    f.write(" " * ((depth + 1) * 2) + line + "\n")


        # write inner html with DFS
        children = curr.locator(":scope > *")
        html_dump(children, depth + 1, filename)
        closing_tag = " " * (depth * 2) + "</" + tag_name + ">\n"

        # write closing tag
        with open(filename, "a", encoding="utf8") as f:
            f.write(closing_tag)
            f.close()

"""
Default values for a field schema
"""
def default_schema():
    return {
            "key": "",
            "label": "",
            "required": False,
            "type": None,
            "pattern": None,
            "minlength": None,
            "maxlength": None,
            "options": []
            }

"""
Generate random number between min_len and max_len if present
"""
def rand_length(min_len, max_len):
    min_len = max(0, int(min_len) if min_len is not None else 0)
    max_len = int(max_len) if max_len is not None else max(min_len + 5, 10)
    if max_len <= min_len:
        max_len = min_len + 5
    return int(min_len + (max_len - min_len) * (random.random()**1.5))


def slightly_modify(s):
    if not s:
        return s

    chars = list(s)

    # Remove 0–2 characters
    for _ in range(random.randint(0, 2)):
        if chars:
            idx = random.randint(0, len(chars) - 1)
            chars.pop(idx)

    # Duplicate 0–2 characters
    for _ in range(random.randint(0, 2)):
        if chars:
            idx = random.randint(0, len(chars) - 1)
            chars.insert(idx, chars[idx])

    # Uppercase 1–3 characters
    for _ in range(random.randint(1, 3)):
        if chars:
            idx = random.randint(0, len(chars) - 1)
            chars[idx] = chars[idx].upper()

    # Swap adjacent characters
    if random.random() < 0.3 and len(chars) > 2:
        idx = random.randint(0, len(chars) - 2)
        chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]

    return "".join(chars)
