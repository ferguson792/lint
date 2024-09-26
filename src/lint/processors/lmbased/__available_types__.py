from lint.processors.lmbased.core import *

import lint.processors.lmbased.mistralonline as mo

LanguageModel.available_types = [mo.MistralClientModel]
