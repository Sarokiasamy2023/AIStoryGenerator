import utilities
from playwright.async_api import TimeoutError
import os
import json
import re
import csv
from DataGenerator import DataGenerator


class DatasetGenerator:
    def __init__(self, test_steps, positive_cases, negative_cases, page, form_name, overwrite_csv: bool = False):
        os.makedirs("outputs", exist_ok=True)

        if overwrite_csv and os.path.exists("outputs/data.csv"):
            os.remove("outputs/data.csv")

        self._test_steps_file_name = test_steps
        self._pos = positive_cases
        self._neg = negative_cases
        self._page = page
        self._form_name = form_name

        self._curr_page_schema = []
        self._schema = self._load_existing_schema()
        self._curr_page_num = (max(self._schema.keys()) - 1) if len(self._schema) > 0 else -1

        self._existing_field_count = self.get_field_count() if len(self._schema) > 0 else 0

        self._test_labels = self._read_test_steps()
        self._expected_number_fields = self._existing_field_count + len(self._test_labels)
        self._data_generator = DataGenerator()

    async def extract_schema_output_csv(self):
        labels = []
        try:
            # For the current page:
            # Scan all fields in the fieldset tag and extract schema for the fields only in the test steps
            await self._page.wait_for_selector("div.cCenterPanel fieldset", timeout=5_000)
            self._curr_page_schema = []
            self._curr_page_num += 1
            await self._take_screenshot()
            root = self._page.locator("fieldset > slot")
            print(f" Writing schema for page {self._curr_page_num+1}...")
            curr_index = 0
            page_field_count = await root.count()
            for nth_child in range(page_field_count):
                self._curr_page_schema.append(utilities.default_schema())
                await self._is_test_field(root.nth(nth_child), index=curr_index)
                if self._curr_page_schema[curr_index] is None:
                    self._curr_page_schema.pop(-1)
                else:
                    if len(self._test_labels) > 0:
                        self._test_labels.pop(-1)
                    print(f"  EXTRACTING SCHEMA FOR A TEST FIELD...")
                    await self._insert_field_schema(root.nth(nth_child), index=curr_index)
                    curr_index += 1
                percent_done = int(float((nth_child+1)/page_field_count)*100) if page_field_count > 0 else 100
                print(f"    {percent_done}% done...")
            init = {}
            for schema in self._curr_page_schema:
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
                    labels.append(init[schema['key']]['label'])
            
            # Merge into schema without overwriting existing content.
            # If extraction yields no fields, do NOT write an empty page dict that could
            # wipe previously extracted fields.
            if len(init) > 0:
                page_key = self._curr_page_num + 1
                if page_key in self._schema and isinstance(self._schema.get(page_key), dict):
                    for k, v in init.items():
                        if k not in self._schema[page_key]:
                            self._schema[page_key][k] = v
                else:
                    self._schema[page_key] = init

            if len(labels) > 0:
                print(f" OUTPUTTING CSV FOR PAGE {self._curr_page_num + 1}...")
                self._output_csv(labels)

            self._output_schema()
            return labels
        except TimeoutError:
            self._output_schema()
            return labels

    def get_field_count(self):
        ret = 0
        if not isinstance(self._schema, dict):
            return ret
        for _, page_schema in self._schema.items():
            if isinstance(page_schema, dict):
                ret += len(page_schema)
        return ret
    
    def get_pages_count(self):
        return len(self._schema)
    

    # ---- Private/helper functions ----
    def _load_existing_schema(self):
        path = f"outputs/{utilities.OUT}.json"
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r") as f:
                existing = json.load(f)
            normalized = {}
            if isinstance(existing, dict):
                for k, v in existing.items():
                    try:
                        normalized[int(k)] = v
                    except Exception:
                        # Ignore non-numeric keys
                        continue
            return normalized
        except Exception:
            return {}

    def _output_schema(self):
        if len(self._schema) > 0:
            # if schema.json exists overwrite it with new schema
            with open(f"outputs/{utilities.OUT}.json", "w") as f:
                json.dump(self._schema, f, indent=4)
            if self._expected_number_fields != self.get_field_count():
                print(f"  DID NOT EXTRACT ALL PROPER TEST FIELDS.\n  PLEASE LOOK AT outputs/{utilities.OUT}.json.\n  EXPECTED {self._expected_number_fields} fields, but got {self.get_field_count()}.")
            else:
                print(f"  EXTRACTED {self.get_field_count()} out of {self.get_field_count()} TEST FIELDS PROPERLY!")
    
    def _read_test_steps(self):
        in_form = False
        ret = []
        try:
            with open(self._test_steps_file_name, "r") as f:
                while True:
                    line = f.readline()

                    if not line:
                        break
                    if not in_form:
                        if not self._form_name:
                            in_form = True
                        else:
                            in_form = self._form_name in line
                    else:
                        regex = r"\"\%(.+)\%\""
                        pattern = re.compile(regex)
                        match = re.search(pattern, line)
                        if match:
                            ret.append(match.group(1))
                f.close()
        except Exception as e:
            print(f"   {e}")
        finally:
            return ret[::-1]

    async def _take_screenshot(self):
        await self._page.screenshot(path=f"outputs/{utilities.OUT}{self._curr_page_num + 1}.png", full_page=True)
        s = f"Saved screenshot for page {self._curr_page_num+1} as outputs/{utilities.OUT}{self._curr_page_num + 1}.png"
        if self._curr_page_num == 0:
            print(f" {s}")
        else:
            print(f"\n {s}")

    async def _get_innermost_text(self, locator, ret=""):
        count = await locator.count()

        for i in range(count):
            curr = locator.nth(i)
            inner_text = await curr.inner_text()
            children = curr.locator(":scope > *")
            children_count = await children.count()
            if inner_text and children_count == 0:
                inner_text = inner_text.split("\n")
                for line in inner_text:
                    ret += line + "\n"
            else:
                ret = await self._get_innermost_text(children, ret)
        return ret

    def _output_csv(self, labels):
        page_schema = self._schema[self._curr_page_num + 1]
        if not os.path.exists("outputs/data.csv"):
            output_csv = []
            csv_columns = ["Scenario Type", "Data Used"] + labels
            output_csv.append(csv_columns)
            for _ in range(self._pos):
                row = []
                for col_name in csv_columns:
                    if col_name == "Scenario Type":
                        row.append("\'Positive\'")
                    elif col_name == "Data Used":
                        row.append("\'False\'")
                    else:
                        for key in page_schema.keys():
                            if page_schema[key]['label'] == col_name:
                                schema = page_schema[key]
                                break
                        data = self._data_generator.generate_correct(schema)
                        row.append(f"\'{data}\'")
                output_csv.append(row)
            
            for _ in range(self._neg):
                row = []
                for col_name in csv_columns:
                    if col_name == "Scenario Type":
                        row.append("\'Negative\'")
                    elif col_name == "Data Used":
                        row.append("\'False\'")
                    else:
                        for key in page_schema.keys():
                            if page_schema[key]['label'] == col_name:
                                schema = page_schema[key]
                                break
                        data = self._data_generator.generate_incorrect(schema)
                        row.append(f"\'{data}\'")
                output_csv.append(row)
            with open('outputs/data.csv', mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(output_csv)
        else:   
            # New column headers

            # New values to add for each row (excluding header)
            # These must match the number of data rows in the CSV
            init_rows = []

            
            for _ in range(self._pos):
                row = []
                for col_name in labels:
                    for key in page_schema.keys():
                        if page_schema[key]['label'] == col_name:
                            schema = page_schema[key]
                            break
                    data = self._data_generator.generate_correct(schema)
                    row.append(f"\'{data}\'")
                init_rows.append(row)
            
            for _ in range(self._neg):
                row = []
                for col_name in labels:
                    for key in page_schema.keys():
                        if page_schema[key]['label'] == col_name:
                            schema = page_schema[key]
                            break
                    data = self._data_generator.generate_incorrect(schema)
                    row.append(f"\'{data}\'")
                init_rows.append(row)

            with open("outputs/data.csv", mode='r') as file:
                reader = list(csv.reader(file))

            # Add new column headers to the first row
            reader[0].extend(labels)


            # Add new values to each data row
            for i in range(1, len(reader)):
                reader[i].extend(init_rows[i - 1])

            # Write the updated data back to the same file
            with open("outputs/data.csv", mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(reader)


    async def _is_test_field(self, locator, on_label_parent=False, on_input_parent=False, index=0):
        count = await locator.count()

        for i in range(count):
            if self._curr_page_schema[index]:
                curr = locator.nth(i)

                tag_name = (await curr.evaluate("curr => curr.tagName")).lower()
                attrs = await curr.evaluate("""
                    curr => {
                        const attrs = curr.attributes
                        const ret = {}
                        for(const attr of attrs){
                            ret[attr.name] = attr.value
                        }
                        return ret
                    }
                """)
                inner_text = await curr.evaluate("""
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
                    no_type = self._curr_page_schema[index]["type"] is None
                    on_input_curr = "runtime_omnistudio_omniscript-omniscript-" in tag_name
                    if no_type and not on_label_curr and not on_input_parent and on_input_curr:
                        self._curr_page_schema[index]["type"] = tag_name.split("runtime_omnistudio_omniscript-omniscript-")[1]
                    else:
                        on_input_curr = on_input_parent
                        
                    # We are not in a label or an input block
                    # looking for either text-block tag or looking for input tag
                    if not on_label_curr and not on_input_curr:
                        children = curr.locator(":scope > *")
                        await self._is_test_field(children, on_label_curr, on_input_curr, index)
                    # We are in a text-block
                    # looking for text
                    elif on_label_curr:
                        if inner_text:
                            inner_text = inner_text.split("\n")
                            for line in inner_text:
                                if line == "*" and len(inner_text) == 1:
                                    self._curr_page_schema[index]["required"] = True
                                else:
                                    label = self._curr_page_schema[index]["label"]
                                    label += " " + line
                                    self._curr_page_schema[index]["label"] = label
                        children = curr.locator(":scope > *")
                        await self._is_test_field(children, on_label_curr, on_input_curr, index)
                    # We are in an input block
                    # looking for metdata from input/textarea/ul tag and their nested elements
                    elif on_input_curr:
                        itype = self._curr_page_schema[index]["type"]

                        if 'data-omni-key' in attrs.keys() and not self._curr_page_schema[index]["key"]:
                            self._curr_page_schema[index]["key"] = attrs['data-omni-key']
                                            
                        if itype == "multiselect":
                            if tag_name == "legend":
                                self._curr_page_schema[index]["label"] = await self._get_innermost_text(curr)
                                self._curr_page_schema[index]['required'] = True
                            else:
                                children = curr.locator(":scope > *")
                                await self._is_test_field(children, on_label_curr, on_input_curr, index)

            if self._curr_page_schema[index]:
                curr_label = self._curr_page_schema[index]['label']
                if not curr_label:
                    print("Couldn't find the label for one of the fields...")
                is_test_field = False
                curr_label = curr_label.strip()
                if len(self._test_labels) > 0:
                    test_label = self._test_labels[-1]
                    if test_label == curr_label[0:len(test_label)]:
                        self._curr_page_schema[index]['label'] = test_label
                        is_test_field = True
                if not is_test_field:
                    self._curr_page_schema[index] = None
                            

    async def _insert_field_schema(self, locator, on_input_parent=False, index=0):
        count = await locator.count()

        for i in range(count):
            curr = locator.nth(i)

            tag_name = (await curr.evaluate("curr => curr.tagName")).lower()
            attrs = await curr.evaluate("""
                curr => {
                    const attrs = curr.attributes
                    const ret = {}
                    for(const attr of attrs){
                        ret[attr.name] = attr.value
                    }
                    return ret
                }
            """)
            
            if not('aria-readonly' in attrs.keys() and attrs['aria-readonly'] == 'true'):
                # If our parent isn't in an input block, 
                # we check if we are entering an input block
                no_type = not self._curr_page_schema[index]["type"]
                on_input_curr = "runtime_omnistudio_omniscript-omniscript-" in tag_name and not (tag_name.endswith("-block") or tag_name.endswith("-formatted-rich-text"))
                if no_type and not on_input_parent and on_input_curr:
                    self._curr_page_schema[index]["type"] = tag_name.split("runtime_omnistudio_omniscript-omniscript-")[1]
                elif not on_input_curr:
                    on_input_curr = on_input_parent
                    
                # We are not on an input block
                # looking for either text-block tag or looking for input tag
                if not on_input_curr:
                    children = curr.locator(":scope > *")
                    await self._insert_field_schema(children, on_input_curr, index)
                # We are in an input block
                # looking for metdata from input/textarea/ul tag and their nested elements
                else:
                    itype = self._curr_page_schema[index]["type"]
                    if tag_name == "input" or tag_name == "textarea":
                        if itype == "multiselect" and attrs.get('type') == "checkbox" and attrs.get('name') == self._curr_page_schema[index]['key']:
                            options = self._curr_page_schema[index]["options"]
                            options.append(attrs.get('value'))
                            self._curr_page_schema[index]["options"] = options
                        else:
                            self._curr_page_schema[index]["required"] = "required" in attrs.keys() if self._curr_page_schema[index]["required" ] == False else self._curr_page_schema[index]["required"]
                            self._curr_page_schema[index]['pattern'] = attrs['pattern'] if 'pattern' in attrs.keys() else self._curr_page_schema[index]['pattern']
                            self._curr_page_schema[index]['minlength'] = attrs['minlength'] if 'minlength' in attrs.keys() else self._curr_page_schema[index]['minlength']
                            self._curr_page_schema[index]['maxlength'] = attrs['maxlength'] if 'maxlength' in attrs.keys() else self._curr_page_schema[index]['maxlength']

                    elif tag_name == "li" and itype == "select":
                        init = (await self._get_innermost_text(curr)).strip()
                        options = self._curr_page_schema[index]['options']
                        options.append(init)
                        self._curr_page_schema[index]['options'] = options
                    children = curr.locator(":scope > *")
                    await self._insert_field_schema(children, on_input_curr, index)