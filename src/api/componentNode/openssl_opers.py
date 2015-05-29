'''
Created on Mar 13, 2015

@author: root
'''
import os
import re
import logging

from tornado.options import options
from common.abstractOpers import AbstractOpers
from utils import get_file_data, set_file_data
from utils import http_get


class OpensslOpers(AbstractOpers):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    def config(self, args):
        
        _ip = args.get('ip')
        content = get_file_data(options.openssl_conf)
        replaced = re.findall('.*IP:(.*)\n?', content)[0]
        content = content.replace(replaced, _ip)
        set_file_data(options.openssl_conf, content)
        
        logging.info('generate .key and .crt file')
        os.system(options.openssl_cmd)
        
        if not os.path.exists(options.tmp_keys_file):
            os.mkdir(options.tmp_keys_file)
        
        key_cmd = 'cp %s %s' % (options.openssl_key_file, options.tmp_keys_file)
        crt_cmd = 'cp %s %s' % (options.openssl_crt_file, options.tmp_keys_file)
        logging.info('do copy: %s' % key_cmd)
        logging.info('do copy: %s' % crt_cmd)
        os.system( key_cmd )
        os.system( crt_cmd )
        
        return {"message": "config openssl.cnf successfully"}

    def copyssl(self, args):
        _ip = args.get('ip')
        port = args.get('port')
        logging.info('ip :%s, port:%s' % (_ip, port))
        crt_filepath = os.path.join(options.tmp_keys_file, 'logstash-forwarder.crt')
        key_filepath = os.path.join(options.tmp_keys_file, 'logstash-forwarder.key')
        self._get(crt_filepath, options.openssl_crt_file, _ip, port)
        self._get(key_filepath, options.openssl_key_file, _ip, port)
        
        return {"message": "copy .crt and .key file successfully"}

    def _get(self, filename, save_path, _ip, port):
        uri = '/inner/admin/file/%s' % filename
        curl = 'http://%s:%s%s' % (_ip, port, uri)
        fetch_ret = http_get(curl)
        set_file_data(save_path, fetch_ret)
        