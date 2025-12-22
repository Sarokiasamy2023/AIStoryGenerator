import utilities
from playwright.sync_api import TimeoutError
import os
import json

class SchemaExtractor:
    def __init__(self, page, url, username, password, form_name):
        os.makedirs("outputs", exist_ok=True)
        self._url = url
        self._page = page
        self._username = username
        self._password = password
        self._form_name = form_name
        self._page_schema = []
        self._page_num = -1
        self._schema = {}
        self._keys = set([])
    
    def navigate_to_form(self):
        # 1) Go to base URL (it will auto-redirect to login)
        self._page.goto(self._url, wait_until="networkidle")

        # 2) Login page – adjust selectors after you inspect with dev tools
        print(" On log-in page...")
        self._page.wait_for_load_state("networkidle")
        self._page.locator('input[placeholder="Username"]').fill(self._username)
        self._page.locator('input[placeholder="Password"]').fill(self._password)
        self._page.locator('button:has-text("Log in")').click(force=True)
        print(" Logged in...")

        # 3) Banner agreement page – toggle “I Agree” then click Next
        # Use role/text selectors because Salesforce often changes IDs
        self._page.wait_for_load_state("networkidle")
        self._page.locator("input[type='checkbox']").click(force=True)
        self._page.locator("button:has-text('Next')").click(force=True)
        print(" Agreed to banner agreement...")
        
        
        # 3.1) Click finish
        self._page.wait_for_load_state("networkidle")
        self._page.locator("button:has-text('Finish')").click(force=True)
        print(" Now entering homepage...")

        
        # 4) Home page -> click “HSD PERFORMANCE REPORTS”
        self._page.wait_for_load_state("networkidle")
        self._page.locator("span:has-text('HSD Performance Reports')").click(force=True)
        print(" Clicked HSD Performance Reports...")


        # 5) Click specific report row “HSD-01078”
        self._page.wait_for_load_state("networkidle", timeout=100000)
        self._page.locator(f"a[title='{self._form_name}']").click(force=True)
        print(f" Clicked on form {self._form_name}")
        
        # 6) Click Edit on the report
        self._page.wait_for_load_state("networkidle")
        self._page.locator("a:has-text('Edit')").click(force=True)
        print(" Clicked 'Edit Form'...")
        
        # 7) Go into the actual form – click “Next” on intro/steps pages
        self._page.wait_for_load_state("networkidle")
        self._page.wait_for_selector("button span.btnLabel:has-text('Next')", timeout=100000).click(force=True)
        print(" Loading into the form...")

        
        # get all input textarea and select elements from div.cCenterPanel[tabindex='-1']
        self._page.wait_for_selector("div.cCenterPanel fieldset", timeout=100000)
        print(" WE ARE IN THE FORM...")
    
    def extract_schema(self):
        try:
            self._page.wait_for_selector("button span.btnLabel:has-text('Next')", timeout=5_000)
            self._page_schema = []
            self._page_num += 1
            self._take_screenshot()
            root = self._page.locator("fieldset > slot")
            print(f" Writing schema for page {self._page_num+1}...")
            for i in range(root.count()):
                self._page_schema.append(utilities.default_schema())
                self._insert_field_schema(root.nth(i), index=i)
                percent_done = int(float((i+1)/root.count())*100)
                print(f"  {percent_done}% done...")
            init = {}
            for schema in self._page_schema:
                if len(schema['key']) > 0:
                    init[schema['key']] = {
                        "label": schema['label'].strip(' \n'),
                        "required": schema['required'],
                        "type": schema['type'],
                        "pattern": schema['pattern'],
                        "minlength": schema['minlength'],
                        "maxlength": schema['maxlength'],
                        "options": schema['options']
                    }
                    if init[schema['key']]['type'] not in ('select', 'multiselect'):
                        init[schema['key']]['minlength'] = '1' if init[schema['key']]['required'] else '0'
                    self._keys.add(schema['key'])
            self._schema[self._page_num + 1] = init
            #next page
            self._page.wait_for_selector("button span.btnLabel:has-text('Next')").click(force=True)
            self._page.wait_for_timeout(5_000)
            self.extract_schema()
        except TimeoutError:
            self._page.close()
            print("DONE EXTRACTING SCHEMA FROM ALL PAGES")

    def output_schema(self):
        if len(self._schema) > 0:
            # if schema.json exists overwrite it with new schema
            with open(f"outputs/{utilities.OUT}.json", "w") as f:
                json.dump(self._schema, f, indent=4)
            print(f" Schema saved to outputs/{utilities.OUT}.json")
    
    def get_field_count(self):
        return len(self._keys)
    
    def get_field_keys(self):
        return self._keys
    
    def get_pages_count(self):
        return self._page_num + 1
    
    def _insert_field_schema(self, locator, on_label_parent=False, on_input_parent=False, index=0):
        count = locator.count()

        for i in range(count):
            curr = locator.nth(i)

            tag_name = curr.evaluate("curr => curr.tagName").lower()
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
            if not('aria-readonly' in attrs.keys() and attrs['aria-readonly'] == 'true'):
                # If our parent isn't in a label block, we check if we are right now
                if not on_label_parent:
                    on_label_curr = tag_name == "runtime_omnistudio_omniscript-omniscript-text-block"
                else:
                    on_label_curr = on_label_parent
                # If our parent isn't in an input block and we aren't on a label block, 
                # we check if we are entering an input block
                no_type = not self._page_schema[index]["type"]
                on_input_curr = "runtime_omnistudio_omniscript-omniscript-" in tag_name
                if no_type and not on_label_curr and not on_input_parent and on_input_curr:
                    self._page_schema[index]["type"] = tag_name.split("runtime_omnistudio_omniscript-omniscript-")[1]
                else:
                    on_input_curr = on_input_parent
                    
                # We are not in a label or an input block
                # looking for either text-block tag or looking for input tag
                if not on_label_curr and not on_input_curr:
                    children = curr.locator(":scope > *")
                    self._insert_field_schema(children, on_label_curr, on_input_curr, index)
                # We are in a text-block
                # looking for text
                elif on_label_curr:
                    if inner_text:
                        inner_text = inner_text.split("\n")
                        for line in inner_text:
                            if line == "*" and len(inner_text) == 1:
                                self._page_schema[index]["required"] = True
                            else:
                                label = self._page_schema[index]["label"]
                                label += " " + line
                                self._page_schema[index]["label"] = label
                    children = curr.locator(":scope > *")
                    self._insert_field_schema(children, on_label_curr, on_input_curr, index)
                # We are in an input block
                # looking for metdata from input/textarea/ul tag and their nested elements
                elif on_input_curr:
                    itype = self._page_schema[index]["type"]
                    if 'data-omni-key' in attrs.keys() and not self._page_schema[index]["key"]:
                        self._page_schema[index]["key"] = attrs['data-omni-key']
                    if tag_name == "input" or tag_name == "textarea":
                        if itype == "multiselect" and attrs['type'] == "checkbox" and attrs['name'] == self._page_schema[index]['key']:
                            options = self._page_schema[index]["options"]
                            options.append(attrs['value'])
                            self._page_schema[index]["options"] = options
                        else:
                            self._page_schema[index]["required"] = "required" in attrs.keys() if self._page_schema[index]["required" ] == False else self._page_schema[index]["required"]
                            self._page_schema[index]['pattern'] = attrs['pattern'] if 'pattern' in attrs.keys() else self._page_schema[index]['pattern']
                            self._page_schema[index]['minlength'] = attrs['minlength'] if 'minlength' in attrs.keys() else self._page_schema[index]['minlength']
                            self._page_schema[index]['maxlength'] = attrs['maxlength'] if 'maxlength' in attrs.keys() else self._page_schema[index]['maxlength']
                    elif tag_name == "li" and itype == "select":
                        init = utilities.get_innermost_text(curr).strip()
                        options = self._page_schema[index]['options']
                        options.append(init)
                        self._page_schema[index]['options'] = options
                    elif tag_name == "legend" and itype == "multiselect":
                        self._page_schema[index]["label"] = utilities.get_innermost_text(curr)
                        self._page_schema[index]['required'] = True
                    
                    children = curr.locator(":scope > *")
                    self._insert_field_schema(children, on_label_curr, on_input_curr, index)

    def _take_screenshot(self):
        self._page.screenshot(path=f"outputs/{utilities.OUT}{self._page_num + 1}.png", full_page=True)
        s = f"Saved screenshot for page {self._page_num+1} as outputs/{utilities.OUT}{self._page_num + 1}.png"
        if self._page_num == 0:
            print(f" {s}")
        else:
            print(f"\n {s}")