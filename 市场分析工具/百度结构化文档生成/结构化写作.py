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
                    'client_id': 'vm3NHQAGzcBRWUVKKBI1LRBv',
                    'client_secret': 'C0Xcr7UaXWVIg1xYTz8cErTBddALlud6'}
baidu_token_data = urllib.parse.urlencode(baidu_token_data).encode('utf-8')

request = urllib.request.Request(baidu_token_url, baidu_token_data, baidu_token_headers)
html = urllib.request.urlopen(request).read().decode('utf-8')
baidu_token_result = json.loads(html)
print(baidu_token_result)
access_token = baidu_token_result['access_token']

time.sleep(1.0)
# 结构化写作-股市
# 没有测试成功
gushi_url = 'https://aip.baidubce.com/rest/2.0/nlp/v1/gen_article?access_token='+access_token
gushi_headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
gushi_data = {'project_id': 1830,
              'stock_type': 'us',
              'stock_code': 'BIDU'}
gushi_data = json.dumps(gushi_data, ensure_ascii=False).encode('utf-8')
request = urllib.request.Request(gushi_url, gushi_data, gushi_headers)
print(request.get_full_url())
html = urllib.request.urlopen(request).read().decode('utf-8')
gushi_result = json.loads(html)
print(gushi_result)