class Symbol: pass


class OnMissingPolicy(Symbol): pass
class Warn(OnMissingPolicy): pass
class Ignore(OnMissingPolicy): pass
class Crash(OnMissingPolicy): pass
