from docx import Document


def title():
    pass


def input_task():
    """1. Исходное задание;"""
    pass


def task_function_list():
    """2. Перечень составленных функций задач;"""
    pass


def load_balancing():
    """3. Таблица перераспределения нагрузки;"""
    pass


def reject_modules_stats():
    """4. Статистика отказавших модулей;"""
    pass


def alg_docs():
    """5. Детальное описание алгоритма статистической выборки векторов кратности 3 и 4 (1/2 страницы);"""
    pass


def reliability_p_or_q():
    """6. Найденный показатель надёжности системы (P или Q);"""
    pass


def modification_proposes():
    """7. С учётом п.5 предложения по модификации системы (с обоснованием в плане стоимости, сложности и проч.);"""
    pass


def new_system_structure():
    """8. Структура модифицированной системы;"""
    pass


def conclusions():
    """10. Вывод о том, что «малой кровью» достигнуто существенное
    (показать на сколько) улучшение показателя надёжности."""
    pass


def system_docs():
    load_balancing()
    reject_modules_stats()
    alg_docs()
    reliability_p_or_q()


def new_system_docs():
    """9. Пункты 2-4 и 6 для модифицированной системы;"""
    system_docs()


def document_do_all(doc, data, *funcs):
    for func in funcs:
        func(doc, data)


def dump_report(data, pathname):
    doc = Document()
    document_do_all(doc,
                    data,
                    title,
                    input_task,
                    task_function_list,
                    system_docs,
                    modification_proposes,
                    new_system_structure,
                    new_system_docs,
                    conclusions)
    doc.save(pathname)