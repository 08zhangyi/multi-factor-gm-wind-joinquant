# 百度POST编写示例
import urllib.parse
import urllib.request
import json
import time

time.sleep(1.0)
# 获取access_token
baidu_token_url = 'https://aip.baidubce.com/oauth/2.0/token'
baidu_token_headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
baidu_token_data = {'grant_type': 'client_credentials',
                    'client_id': 'DP7yZde5EK2MEKLzcjzwCCp5',
                    'client_secret': 'EQPFBZOjgyyhpf9llpsZobIUIftpyj8I'}
baidu_token_data = urllib.parse.urlencode(baidu_token_data).encode('utf-8')

request = urllib.request.Request(baidu_token_url, baidu_token_data, baidu_token_headers)
html = urllib.request.urlopen(request).read().decode('utf-8')
baidu_token_result = json.loads(html)
print(baidu_token_result)
access_token = baidu_token_result['access_token']

time.sleep(1.0)
# 春联
chunlian_url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/couplets?access_token='+access_token
chunlian_headers = {'Content-Type': 'application/json; charset=UTF-8'}
chunlian_data = {'text': '百度',
                 'index': 0}
chunlian_data = json.dumps(chunlian_data, ensure_ascii=False).encode('utf-8')

request = urllib.request.Request(chunlian_url, chunlian_data, chunlian_headers)
html = urllib.request.urlopen(request).read().decode('utf-8')
chunlian_result = json.loads(html)
print(chunlian_result)

time.sleep(1.0)
# 写诗
xieshi_url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/poem?access_token='+access_token
xieshi_headers = {'Content-Type': 'application/json; charset=UTF-8'}
xieshi_data = {'text': '股票大涨',
               'index': 0}
xieshi_data = json.dumps(xieshi_data, ensure_ascii=False).encode('utf-8')

request = urllib.request.Request(xieshi_url, xieshi_data, xieshi_headers)
html = urllib.request.urlopen(request).read().decode('utf-8')
xieshi_result = json.loads(html)
print(xieshi_result)