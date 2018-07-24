import unittest

from disallower import disallow, require, Warn, Ignore
from base import ContractWarning, ContractException

## Predicate functions:
def negative_values(x: int) -> bool:
    return x < 0

def valid_lang(s: str) -> bool:
    return s.lower() in ["sv", "en"]


## Test function definitions:
@disallow(age=negative_values)
@require(lang=valid_lang)
def greet_person(age: int, lang: str):
    return "Du är gammal!" if age > 80 else "Du är ung!"

@disallow(age=negative_values)
def greet_person_raise_on_negative_age(age: int, lang: str):
    return "Du är gammal!" if age > 80 else "Du är ung!"

@disallow(age=negative_values)
@require(lang=valid_lang, lung=valid_lang, on_missing_policy=Warn)
def greet_person_warn_on_missing_kwarg(age: int, lang: str):
    return "Du är gammal!" if age > 80 else "Du är ung!"
    
    
## Test cases
class TestGreetPerson(unittest.TestCase):
    def test_valid_call(self):
        greet_person(age=30, lang="sv")
        
    def test_rasies_on_negative_age(self):
        with self.assertRaises(ContractException):
            greet_person_raise_on_negative_age(age=-30)
    
    def test_warns(self):
        with self.assertWarns(ContractWarning):
            greet_person_warn_on_missing_kwarg(age=30, lang="sv")
            
if __name__ == "__main__":
    unittest.main()
