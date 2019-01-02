import tushare as ts
import re

# tushare配置
pro = ts.pro_api(token='9668f6b57f4e3fe1199446a9c7b251d553963832bbf6e411b8065ea2')

data = pro.stock_basic(exchange='', list_status='L', fields='name').values
data = [re.sub('[a-zA-Z]', '', d[0]) for d in data]
print(data)
