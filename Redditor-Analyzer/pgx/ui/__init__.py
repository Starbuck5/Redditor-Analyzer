from pgx.ui.UI import UI

from pgx.ui.base import *
from pgx.ui.compound import *
from pgx.ui.component import *
from pgx.ui.constants import *


# replaces string definitions with class types
# 'TextBox' string -> pgx.ui.TextBox class definition
Selectable.ALLOWED_PARENTS = tuple([eval(p) for p in Selectable.ALLOWED_PARENTS])
