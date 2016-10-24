# -*- coding: utf-8 -*-
"""
This file is part of the EIDA mediator/federator webservices.

"""

import os

import flask
from flask_restful import abort, reqparse, request, Resource

from federator import settings
from federator.server import general_request, httperrors
from federator.utils import misc


dataselect_reqparser = general_request.general_reqparser.copy()
dataselect_reqparser.add_argument('quality', type=str)
dataselect_reqparser.add_argument('minimumlength', type=float)
dataselect_reqparser.add_argument('longestonly', type=bool)

class DataselectRequestTranslator(general_request.GeneralRequestTranslator):
    """Translate query params to commandline params."""

    def __init__(self, query_args):
        super(DataselectRequestTranslator, self).__init__(query_args)
        
        # add service commandline switch
        self.add(general_request.FDSNWSFETCH_SERVICE_PARAM, 'dataselect')
        
        # sanity check - for GET, need at least one of SNCL and network can't be
        # just wildcards
        if request.method == 'GET' and self.getpar('-S') is None and \
            self.getpar('-C') is None and self.getpar('-L') is None and (
                self.getpar('-L') is None or self.getpar('-L') in ('*', '??')):
                
                raise httperrors.BadRequestError()
        

class DataselectResource(general_request.GeneralResource):
    """
    Handler for dataselect service route.
    
    """
     
    def get(self):
        
        args = dataselect_reqparser.parse_args()
        fetch_args = DataselectRequestTranslator(args)

        return self._process_request(
            fetch_args, general_request.DATASELECT_MIMETYPE)

        
    def post(self):
        
        # request.method == 'POST'
        # Note: must be sent as binary to preserve line breaks
        # curl: --data-binary @postfile --header "Content-Type:text/plain"
        args = dataselect_reqparser.parse_args()
        fetch_args = DataselectRequestTranslator(args)
        
        temp_postfile, fetch_args = self._process_post_args(fetch_args)
        
        return self._process_request(
            fetch_args, general_request.DATASELECT_MIMETYPE, 
            postfile=temp_postfile)
        
        
    
