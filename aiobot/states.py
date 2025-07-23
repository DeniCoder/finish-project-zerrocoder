from aiogram.fsm.state import State, StatesGroup

# Состояния FSM для добавления расхода
class AddExpenseStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_date = State()
    waiting_for_description = State()

# Состояния FSM для добавления дохода
class AddIncomeStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_date = State()
    waiting_for_description = State()

# Состояния FSM для выбора типа и категории
class CategoryStatsStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_category = State()

# Состояния FSM для графика
class ChartStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_period = State()