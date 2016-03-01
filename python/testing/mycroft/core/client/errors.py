#!/usr/bin/env python
#  -*- coding: utf-8 -*-

class NoFreeIpException(ValueError):
    pass

class NoSupportProjectException(ValueError):
    pass

class ContainerException(Exception):
    pass

class NoCreatedContainerException(ContainerException):
    pass

class RequestException(ContainerException):
    pass

class ContainerStatusException(ContainerException):
    pass
