from aiogram.fsm.state import State, StatesGroup

# FSM-состояния для добавления расхода
class AddExpenseStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_date = State()
    waiting_for_description = State()

# FSM-состояния для добавления дохода
class AddIncomeStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_date = State()
    waiting_for_description = State()

# FSM-состояния периода и категории для получения операций
class HistoryStates(StatesGroup):
    waiting_for_scope = State()
    waiting_for_category_type = State()
    waiting_for_category = State()
    waiting_for_period_type = State()
    waiting_for_day = State()
    waiting_for_range = State()
    waiting_for_month = State()
    waiting_for_year = State()

# FSM-состояния периода для круговой диаграммы
class ChartStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_period_type = State()
    waiting_for_day = State()
    waiting_for_range = State()
    waiting_for_month = State()
    waiting_for_year = State()

# FSM-состояния периода для столбчатой диаграммы и статистики
class SummaryStates(StatesGroup):
    waiting_for_period_type = State()
    waiting_for_day = State()
    waiting_for_range = State()
    waiting_for_month = State()
    waiting_for_year = State()