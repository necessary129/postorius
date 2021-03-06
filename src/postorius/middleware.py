# -*- coding: utf-8 -*-
# Copyright (C) 2015 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.


from postorius import utils
from postorius.models import MailmanApiError


class PostoriusMiddleware(object):

    def process_request(self, request):
        utils.set_other_emails(request.user)

    def process_exception(self, request, exception):
        if isinstance(exception, MailmanApiError):
            return utils.render_api_error(request)
