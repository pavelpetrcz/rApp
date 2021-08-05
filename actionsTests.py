import unittest

import actions


class ActionTests(unittest.TestCase):
    def testConvertToKeyValue(self):
        d = [{'negotiation': False, 'name': 'Celková cena', 'notes': ['včetně provize'], 'value': '4\xa0916\xa0000', 'currency': 'Kč', 'type': 'price_czk', 'unit': 'za nemovitost'}, {'type': 'string', 'name': 'ID zakázky', 'value': '37579'}, {'type': 'edited', 'name': 'Aktualizace', 'value': '23.06.2021', 'topped': False}, {'type': 'string', 'name': 'Stavba', 'value': 'Cihlová'}, {'type': 'string', 'name': 'Stav objektu', 'value': 'Novostavba'}, {'type': 'string', 'name': 'Vlastnictví', 'value': 'Osobní'}, {'type': 'string', 'name': 'Podlaží', 'value': '1. podlaží'}, {'unit': 'm2', 'type': 'area', 'name': 'Užitná plocha', 'value': '38'}, {'unit': 'm2', 'type': 'area', 'name': 'Plocha podlahová', 'value': '23'}, {'unit': 'm2', 'type': 'area', 'name': 'Plocha zahrady', 'value': '13'}, {'type': 'boolean', 'name': 'Sklep', 'value': True}, {'type': 'boolean', 'name': 'Parkování', 'value': True}, {'type': 'boolean', 'name': 'Garáž', 'value': True}, {'type': 'boolean', 'name': 'Vybavení', 'value': False}]
        testD = {'Celková cena': '4\xa0916\xa0000', 'ID zakázky': '37579', 'Aktualizace': '23.06.2021', 'Stavba': 'Cihlová', 'Stav objektu': 'Novostavba', 'Vlastnictví': 'Osobní', 'Podlaží': '1. podlaží', 'Užitná plocha': '38', 'Plocha podlahová': '23', 'Plocha zahrady': '13', 'Sklep': True, 'Parkování': True, 'Garáž': True, 'Vybavení': False}
        self.assertEqual(actions.convertToKeyValue(d, "name", "value", False), testD)

    def testGetOfferJson(self):
        self.assertEqual(actions.getOfferJson("ba"), "https://www.sreality.cz/api/cs/v2/estates/ba")


if __name__ == '__main__':
    unittest.main()
