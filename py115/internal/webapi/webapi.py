__author__ = 'deadblue'

import inspect

from py115.agent import Agent

def json(url: str):
    def wrapper_creator(func):
        def wraper(agent: Agent, *args, **kwargs):
            # Get passing args
            call_args = inspect.getcallargs(func, *args, **kwargs)
            return None
        return wraper
    return wrapper_creator

def jsonp(func):
    pass

def json_ec(func):
    pass