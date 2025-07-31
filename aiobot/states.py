from aiogram.fsm.state import StatesGroup, State

class AddExpenseStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_date = State()
    waiting_for_description = State()

class AddIncomeStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_date = State()
    waiting_for_description = State()

class HistoryStates(StatesGroup):
    waiting_for_scope = State()
    waiting_for_category_type = State()
    waiting_for_category = State()
    waiting_for_period_type = State()
    waiting_for_day = State()
    waiting_for_range = State()
    waiting_for_month = State()
    waiting_for_year = State()

class ChartStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_period_type = State()
    waiting_for_day = State()
    waiting_for_range = State()
    waiting_for_month = State()
    waiting_for_year = State()

class SummaryStates(StatesGroup):
    waiting_for_period_type = State()
    waiting_for_day = State()
    waiting_for_range = State()
    waiting_for_month = State()
    waiting_for_year = State()

class SetLimitStates(StatesGroup):
    waiting_for_category_type = State()
    waiting_for_category = State()
    waiting_for_period_type = State()
    waiting_for_amount = State()

class DeleteLimitStates(StatesGroup):
    waiting_for_category_type = State()
    waiting_for_category = State()
    waiting_for_period_type = State()
    confirming = State()

class LimitStates(StatesGroup):
    main = State()
    choose_category = State()
    choose_period = State()
    enter_amount = State()
    confirm_delete = State()