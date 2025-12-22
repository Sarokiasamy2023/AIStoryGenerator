import utilities
import json
import rstr 
import re
import random
from faker import Faker
import string

"""
Types: 
 - text and textarea
 - select and multiselect
 - number
 Attributes:
 - key
 - label
 - required
 - type
 - pattern
 - minlength
 - maxlength
 - options

Incorrect data generation:

Simple cases:
if required, return empty -- sometimes
if select, return invalid_*seven random alphanumerics* -- definite
if number, generate number outside min and max if present. if not generate between 1 and 5 chars -- definite
if minlength is there and >=2, generate random string/faker of length less than minlength -- sometimes
if maxlength is there, generate random string/faker of length more than maxlength -- sometimes
^ takes care of textarea/text with no pattern
if multiselect, -- definite
   - either return valid choices less than minselect if minselect is >=2
   - or return valid choices greater than maxselect
   - or return correct amount of invalid choices
   - or return correct amount of mixed valid and invalid choices
if pattern, generate correct pattern then add underscore and 7 rand alpanumeric -- definite
"""

class DataGenerator:
    def __init__(self):
        self._fake = Faker()

    """
    Given the schema of a field:
    We will generate a correct value for the field based on the schema. 
    """
    def generate_correct(self, schema):
        if schema and schema['type']:
            itype = schema['type']

            """
            If the field is not required,
            generate an empty value for the field 25% of the time
            """
            if not schema['required']:
                r = random.random()
                if r < 0.00005:
                    return self._generate_empty(schema)
            
            # ---- pattern is present ---
            if schema['pattern']:
                """
                30% of the time: return a generated string from regex pattern
                70% of the time: choose a lowest-frequency string from 100 generated regex strings
                """
                try:
                    pattern = schema['pattern']
                    r = random.random()

                    if r < 0.3:
                        return rstr.xeger(pattern)
                    else:
                        # count occurances of 100 generated strings
                        seen = {}
                        for _ in range(100):
                            curr = rstr.xeger(pattern)
                            # the key is the string, and the value is the number of times it has been generated
                            seen[curr] = 1 if curr not in seen.keys() else seen[curr] + 1
                        lowest = min(seen.values())
                        # collect lowest occuring generated string(s) and return a random one
                        ret = [
                            generated 
                            for generated, occ in seen.items() 
                            if occ == lowest
                        ]
                        if len(ret) > 0:
                            return random.choice(ret)
                except Exception as e:
                    print(f"   Couldn't read regex pattern ({e}). Generating string using constraints now...")
            
            # ---- select / multiselect ----
            if itype == "select" or itype == "multiselect":
                """
                For k maximum required options, select between 1 and k options with bias towards lower numbers
                k = 1 for select
                k = len(options) for multiselect
                """
                options = [
                    option.strip() 
                    for option in schema['options'] 
                    if option.strip() != '-- Clear --'
                ]
                if len(options) > 0:
                    min_select = 1
                    max_select = 1 if schema['type'] == 'select' else len(options) # 1 for select, len(options) for multiselect.
                    ret = set([])
                    """
                    We want to pick a number between min_select and max_select, but we don't want all values
                    to be equally likely. We want smaller numbers to appear more often.

                    To do that, we take a random number r (0-1) and raise it to a power 'b' (bias):
                        r = r ** b

                    How bias affects the randomness:
                    - b < 1: r becomes bigger -> we get higher numbers more often.
                    - b = 1: r stays uniform -> no bias.
                    - b > 1: r becomes smaller -> we get lower numbers more often.

                    Then we scale r into our desired range:
                        value = r * (max_select - min_select + 1) + min_select

                    This gives a number between min_select and max_select, but influenced by the bias.
                    """
                    r = random.random()
                    bias = 2.5
                    r = r ** bias

                    num_selected = int(r * (max_select - min_select + 1)) + min_select
                    num_selected = min(num_selected, max_select)
                    
                    if itype == "multiselect":
                        r = random.random()
                        # 10% chance of selecting all available options for multiselect
                        if r < 0.1:
                            num_selected = max_select
                    
                    while len(ret) < num_selected:
                        ret.add(random.choice(options))
                    return " | ".join(list(ret)).strip('\'').strip('\"')

            # ---- number ----
            elif itype == "number":
                bias = 1.5
                r = random.random()
                r = r**bias
                lo = 0
                hi = 9999
                return str(int(r * (hi - lo + 1)) + lo)
            """
            Length-based text generation (used when no pattern or select logic applies): 

            Generate a string whose length falls between minlength and maxlength,
            with a bias toward shorter lengths.

            If minlength and maxlength aren't present:
            make them 5 and 15 respectively
            
            If one is present:
            Make minlength 2/3 of maxlength, and vice versa

            Keep generating text until we have reached the generated length.
            """
            if schema['minlength'] is not None and schema['maxlength'] is not None:
                minlength = int(schema['minlength'])
                maxlength = int(schema['maxlength'])
            elif schema['minlength']is not None:
                minlength = int(schema['minlength'])
                maxlength = int(3/2*minlength)
            elif schema['maxlength']is not None:
                maxlength = int(schema['maxlength'])
                minlength = int(2/3*maxlength)
            else:
                minlength = 5
                maxlength = 15
            
            # sanity check
            if maxlength < minlength:
                maxlength = minlength

            if not schema['required'] and minlength == 0 and maxlength > 0:
                """
                We already gave it a 25% chance to be empty above if it is not required.
                Force the non-empty case to be at least 1 char.
                """
                minlength = 1
            
            length = None
            # 5% chance of returning 'minlength' number of spaces
            r = random.random()
            if r < 0.05:
                return ' '*minlength
            # 2.5% chance of returning 'minlength' size string 
            elif r < 0.075:
                maxlength = minlength
            # 5% chance of returning 'maxlength' number of spaces
            elif r < 0.125:
                return ' '*maxlength
            # 2.5% chance of returning 'maxlength' size string 
            elif r < 0.15:
                minlength = maxlength     
            
            r = random.random()
            bias = random.uniform(3.0, 4.0)
            r = r ** bias
            
            length = int(r*(maxlength - minlength + 1)) + minlength

            ret = ""
            while len(ret) < length:
                diff = length - len(ret)
                # if the remaining length is less than 5, fill with random chars
                if diff < 5:
                    ret += ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=diff))
                # otherwise use faker text
                else:
                    ret += self._fake.text(max_nb_chars=diff)
            ret = ret[:length].replace("\n", "").strip("\"")
            ret += ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=max(0, length-len(ret))))
            return ret
        return None




    def generate_incorrect(self, schema):
        if schema and schema['type']:
            r = random.random()
            if schema['required'] and r < 0.07:
                return self._generate_empty(schema)

            ret = None
            if schema['pattern']:
                init = ""
                while len(init) == 0:
                    init = self.generate_correct(schema)
                regex = re.compile(schema['pattern'])
                while bool(regex.fullmatch(init)):
                    init = utilities.slightly_modify(init)
                ret = init
            elif schema['type'] == 'select' or schema['type'] == 'multiselect':
                options = [
                    option.strip() 
                    for option in schema['options'] 
                    if option.strip() != '-- Clear --'
                ]
                if len(options) > 0:
                    min_select = 1
                    max_select = 1 if schema['type'] == 'select' else len(options) # 1 for select, len(options) for multiselect.

                    bias = 2.5
                    r = random.random()
                    r = r ** bias

                    num_selected = int(r * (max_select - min_select + 1)) + min_select
                    num_selected = min(num_selected, max_select)
                    
                    if schema['type'] == "multiselect":
                        r = random.random()
                        # 10% chance of selecting all available options for multiselect
                        if r < 0.1:
                            num_selected = max_select
                    selected_options = set([])
                    while len(selected_options) < num_selected:
                        selected_options.add(self._generate_invalid_choice(schema, options))
                    ret = " | ".join(list(selected_options))
            elif schema['type'] == 'number':
                ret = ''.join(random.choices(string.ascii_letters, k=random.randint(1,5)))

            if ret is None:
                minlength = 1 if not schema['minlength'] else max(1, int(schema['minlength']))
                maxlength = None if not schema['maxlength'] else max(minlength, int(schema['maxlength']))
                length = None

                if maxlength and minlength and minlength >= 2:
                    r = random.random()
                    if r < 0.5:
                        length = max(minlength - random.randint(1, max(minlength-1, 1)), 1)
                    else:
                        length = maxlength + random.randint(1, 5)
                elif maxlength:
                    length = maxlength + random.randint(1, 5)
                elif minlength and minlength >= 2:
                    length = max(minlength - random.randint(1, max(minlength-1, 1)), 1)

                if length:
                    ret = ""
                    while len(ret) < length:
                        diff = length - len(ret)
                        # if the remaining length is less than 5, fill with random chars
                        if diff < 5:
                            ret += ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=diff))
                        # otherwise use faker text
                        else:
                            ret += self._fake.text(max_nb_chars=diff)
                    ret = ret[:length].replace("\n", "").strip("\"")
                    ret += ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=max(0, length-len(ret))))
        
            if ret is None:
                return self.generate_incorrect(schema)
            else:
                return ret
    
    def _generate_empty(self, schema):
        if schema['type'] == 'select':
            if '-- Clear --' in schema['options']:
                return '-- Clear --'
        return ''
    
    def _generate_invalid_choice(self, schema, options):
        if '-- Clear --' in options:
            options.remove('-- Clear --')
        r = random.random()
        if r < 0.25:
            ret = self.generate_correct(schema)
            ret += "_" + ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        elif r < 0.5:
            ret = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
            ret += "_" + self.generate_correct(schema)
        elif r < 0.75:
            ret = "INVALID_" + ''.join(random.choices(string.ascii_letters + string.digits, k=7))
        elif r < 1.0:
            ret = ''.join(random.choices(string.ascii_letters + string.digits, k=7)) + "_INVALID"
        return ret