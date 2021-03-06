# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# This is <httperrors.py>
# -----------------------------------------------------------------------------
# This file is part of EIDA webservices.
#
# EIDA webservices is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EIDA webservices is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----
#
# Copyright (c) Daniel Armbruster (ETH), Fabian Euchner (ETH)
#
# REVISION AND CHANGES
# 2018/05/18        V0.1    Daniel Armbruster, Fabian Euchner
#
# -----------------------------------------------------------------------------
"""
FDSNWS conform HTTP error definitions.

See also: http://www.fdsn.org/webservices/FDSN-WS-Specifications-1.1.pdf
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from builtins import * # noqa

from flask import request, g

from eidangservices import settings

# Error <CODE>: <SIMPLE ERROR DESCRIPTION>
# <MORE DETAILED ERROR DESCRIPTION>
# Usage details are available from <SERVICE DOCUMENTATION URI>
# Request:
# <SUBMITTED URL>
# Request Submitted:
# <UTC DATE TIME>
# Service version:
# <3-LEVEL VERSION>

ERROR_MESSAGE_TEMPLATE = """
Error %s: %s

%s

Usage details are available from %s

Request:
%s

Request Submitted:
%s

Service version:
%s
"""


def get_error_message(code, description_short, description_long,
                      documentation_uri, request_url, request_time,
                      service_version):
    """Return text of error message."""

    return ERROR_MESSAGE_TEMPLATE % (code, description_short,
                                     description_long, documentation_uri,
                                     request_url, request_time,
                                     service_version)

# get_error_message ()

# -----------------------------------------------------------------------------


class FDSNHTTPError(Exception):
    """
    General HTTP error class for 5xx and 4xx errors for FDSN web services,
    with error message according to standard. Needs to be subclassed for
    individual error types.

    """
    code = 0
    error_desc_short = ''

    DOCUMENTATION_URI = settings.FDSN_SERVICE_DOCUMENTATION_URI
    SERVICE_VERSION = ''

    @staticmethod
    def create(status_code, *args, **kwargs):
        """
        Factory method for concrete FDSN error implementations.
        """
        if status_code in settings.FDSN_NO_CONTENT_CODES:
            return NoDataError(status_code)
        elif status_code == 400:
            return BadRequestError(*args, **kwargs)
        elif status_code == 413:
            return RequestTooLargeError(*args, **kwargs)
        elif status_code == 414:
            return RequestURITooLargeError(*args, **kwargs)
        elif status_code == 500:
            return InternalServerError(*args, **kwargs)
        elif status_code == 503:
            return TemporarilyUnavailableError(*args, **kwargs)
        else:
            return InternalServerError(*args, **kwargs)

    # create

    def __init__(self, documentation_uri=None, service_version=None):
        super().__init__()

        self.documentation_uri = (documentation_uri if documentation_uri else
                                  self.DOCUMENTATION_URI)
        self.service_version = (service_version if service_version else
                                self.SERVICE_VERSION)

        self.description = get_error_message(
            self.code, self.error_desc_short, self.error_desc_short,
            self.documentation_uri, request.url,
            g.request_start_time.isoformat(),
            self.service_version)

    # __init__ ()

# class FDSNHTTPError


class NoDataError(FDSNHTTPError):
    description = ''

    def __init__(self, status_code=204):
        self.code = status_code

# class NoDataError


class BadRequestError(FDSNHTTPError):
    code = 400
    error_desc_short = 'Bad request'


class RequestTooLargeError(FDSNHTTPError):
    code = 413
    error_desc_short = 'Request too large'


class RequestURITooLargeError(FDSNHTTPError):
    code = 414
    error_desc_short = 'Request URI too large'


class InternalServerError(FDSNHTTPError):
    code = 500
    error_desc_short = 'Internal server error'


class TemporarilyUnavailableError(FDSNHTTPError):
    code = 503
    error_desc_short = 'Service temporarily unavailable'


# ---- END OF <httperrors.py> ----
