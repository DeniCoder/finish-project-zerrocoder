from aiogram.fsm.state import StatesGroup, State

class SelectPeriodStates(StatesGroup):
    """
    Универсальные состояния для диалогов по выбору периода и дат.
    """
    waiting_for_period_type = State()
    waiting_for_day = State()
    waiting_for_range = State()
    waiting_for_month = State()
    waiting_for_year = State()

class AddExpenseStates(StatesGroup):
    """
    Сценарий создания расхода.
    """
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_date = State()
    waiting_for_description = State()

class AddIncomeStates(StatesGroup):
    """
    Сценарий создания дохода.
    """
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_date = State()
    waiting_for_description = State()

class HistoryStates(SelectPeriodStates):
    """
    Сценарии просмотра истории операций.
    """
    waiting_for_scope = State()
    waiting_for_category_type = State()
    waiting_for_category = State()

class ChartStates(SelectPeriodStates):
    """
    Сценарии построения диаграмм.
    """
    waiting_for_type = State()

class SummaryStates(SelectPeriodStates):
    """
    Сценарии получения сводной статистики.
    """
    pass

class SetLimitStates(StatesGroup):
    """
    Сценарии добавления или редактирования лимитов.
    """
    waiting_for_category_type = State()
    waiting_for_category = State()
    waiting_for_period_type = State()
    waiting_for_amount = State()

class DeleteLimitStates(StatesGroup):
    """
    Сценарии удаления лимитов.
    """
    waiting_for_category_type = State()
    waiting_for_category = State()
    waiting_for_period_type = State()
    confirming = State()
