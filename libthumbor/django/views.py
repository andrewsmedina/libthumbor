#!/usr/bin/python
# -*- coding: utf-8 -*-

# libthumbor - python extension to thumbor
# http://github.com/heynemann/libthumbor

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 Bernardo Heynemann heynemann@gmail.com

'''Generic view for create thumbor encrypted urls.'''
import logging

from django.http import Http404, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponse
from django.conf import settings

from libthumbor.crypto import CryptoURL

THUMBOR_SECURITY_KEY = getattr(settings, 'THUMBOR_SECURITY_KEY', 'my-security-key')
THUMBOR_SERVER = getattr(settings, 'THUMBOR_SERVER', 'http://localhost:8888/')

def generate_url(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    crypto = CryptoURL(THUMBOR_SECURITY_KEY)
    
    args = request.GET
    # convert Django QueryDict to a python dict
    args = dict(zip(map(str, args.keys()), args.values()))
    error_message = None

    try:
        if 'width' in args:
            args['width'] = int(args['width'])
    except ValueError, e:
        error_message = "The width value '%s' is not an integer." % args['width']

    try:
        if 'height' in args:
            args['height'] = int(args['height'])
    except ValueError, e:
        error_message = "The height value '%s' is not an integer." % args['height']

    try:
        if 'crop_top' in args or 'crop_left' in args or 'crop_right' in args or 'crop_bottom' in args:
            args['crop'] = ((int(args['crop_left']), int(args['crop_top'])),
                    (int(args['crop_right']), int(args['crop_bottom'])))
    except KeyError, e:
        error_message = "Missing values for cropping. Expected all 'crop_left', 'crop_top', 'crop_right', 'crop_bottom' values."
    except ValueError, e:
        error_message = "Invalid values for cropping. Expected all 'crop_left', 'crop_top', 'crop_right', 'crop_bottom' to be integers."

    if error_message is not None:
        logging.warning(error_message)
        return HttpResponseBadRequest(error_message)

    try:
        return HttpResponse(THUMBOR_SERVER + crypto.generate(**args).strip("/"), mimetype="text/plain")
    except (ValueError, KeyError), e:
        error_message = str(e)
        logging.warning(error_message)
        return HttpResponseBadRequest(error_message)


