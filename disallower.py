from typing import Union, Any, Callable, List, Iterable
import warnings
import collections

from base import ContractWarning, ContractException
from symbols import OnMissingPolicy, Warn, Ignore, Crash

def _extract_predicates(predicate: Union[Callable, Iterable]) -> List[Callable]:
    """E.g.
    some_function -> [some_function]
    [some_function] -> [some_function]
    (some_function, another_function) -> [some_function, another_function]
    """
    if isinstance(predicate, collections.Iterable):
        return list(predicate)
    else:
        return [predicate]

def _check_args_predicates(args, args_predicates, disallow: bool):
    for i, (arg, predicate) in enumerate(zip(args, args_predicates)):
        predicates = _extract_predicates(predicate)
        for predicate in predicates:
            if disallow:
                if predicate(arg):
                    error_msg = f"`{arg}` should not fulfill `{predicate.__name__}`"
                    raise ContractException(error_msg)
            else:
                if not predicate(arg):
                    error_msg = f"`{arg}` does not fulfill `{predicate.__name__}`"
                    raise ContractException(error_msg)
                
def _get_on_missing_policy(kwargs) -> (List, OnMissingPolicy):
    """Extracts on_missing_policy from kwargs, and returns it along with
    kwargs sans the on_missing_policy key
    """
    DEFAULT_ON_MISSING_POLICY = Crash
    on_missing_policy = kwargs.get("on_missing_policy", DEFAULT_ON_MISSING_POLICY)
    new_kwargs = {k: v for k, v in kwargs.items() if k != "on_missing_policy"}
    return new_kwargs, on_missing_policy
                
def _get_key(predicate, kwargs, key, on_missing_policy: OnMissingPolicy) \
        -> Union[Any, Ignore]:
    try:
        return kwargs[key]
    except KeyError:
        if on_missing_policy is Warn:
            warning_msg = f"Contract `{predicate.__name__}` cannot check for missing keyword argument '{key}'"
            warnings.warn(warning_msg, ContractWarning)
            return Ignore
        elif on_missing_policy is Ignore:
            return Ignore
        else:
            error_msg = f"Contract `{predicate.__name__}` cannot check for missing keyword argument '{key}'"
            raise KeyError(error_msg)
    
def _check_kwargs_predicates(kwargs,
                             kwargs_predicates,
                             on_missing_policy: OnMissingPolicy,
                             disallow: bool):
    """Depending on on_missing_policy, this may Raise ContractException
    """
    for key, predicate in kwargs_predicates.items():
        predicates = _extract_predicates(predicate)
        
        for predicate in predicates:
            value = _get_key(predicate, kwargs, key, on_missing_policy)
            
            if value is Ignore:
                return
            
            if disallow:
                if predicate(value):
                    error_msg = f"{key}: `{value}` should not fulfill `{predicate.__name__}`"
                    raise ContractException(error_msg)
            else:
                if not predicate(value):
                    error_msg = f"{key}: `{value}` does not fulfill `{predicate.__name__}`"
                    raise ContractException(error_msg)

# Decorators:

def disallow(*args_predicates, **kwargs_predicates):
    kwargs_predicates, on_missing_policy = \
        _get_on_missing_policy(kwargs_predicates)
    
    def inner(f):
        def inner2(*args, **kwargs):
            _check_args_predicates(args, args_predicates, disallow=True)
            _check_kwargs_predicates(kwargs,
                                     kwargs_predicates,
                                     on_missing_policy=on_missing_policy,
                                     disallow=True)
            return f(*args, **kwargs)
        return inner2
    return inner


def require(*args_predicates, **kwargs_predicates):
    kwargs_predicates, on_missing_policy = \
        _get_on_missing_policy(kwargs_predicates)
    
    def inner(f):
        def inner2(*args, **kwargs):
            _check_args_predicates(args, args_predicates, disallow=False)
            _check_kwargs_predicates(kwargs,
                                     kwargs_predicates,
                                     on_missing_policy=on_missing_policy,
                                     disallow=False)
            return f(*args, **kwargs)
        return inner2
    return inner

#~ def when_present(*args_predicates, **kwargs_predicates):
#~     return require(*args_predicates, **kwargs_predicates)
