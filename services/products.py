PRODUCTS = {
    "смеситель": {
        "default": "Смеситель для кухни",
        "keywords": {
            "кух": "Смеситель для кухни",
            "ван": "Смеситель для ванной",
        }
    },
    "ванна": "Ванна акриловая",
    "душ": {
        "default": "Душевая кабина",
        "keywords": {
            "гигиен": "Гигиенический душ",
        }
    },
    "раковина": "Раковина керамическая",
    "унитаз": "Унитаз компакт",
    "туалет": "Унитаз компакт",
    "полотенцесуш": "Полотенцесушитель",
    "сифон": "Сифон для раковины",
    "фильтр": "Фильтр для воды",
}

def get_random_product():
    import random
    return random.choice(PRODUCTS)

def find_product_by_text(text: str):
    text = text.lower()

    for key, rule in PRODUCTS.items():

        # если правило — строка (простое соответствие)
        if isinstance(rule, str):
            if key in text:
                return rule

        # если правило — сложное (default + keywords)
        else:
            if key in text:
                for sub_key, product in rule.get("keywords", {}).items():
                    if sub_key in text:
                        return product

                return rule.get("default")

    return None