from WindPy import w
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
TS_TOKEN = '9668f6b57f4e3fe1199446a9c7b251d553963832bbf6e411b8065ea2'


class 行业比较分析模板():
    def __init__(self, code, date, mode):
        self.code = code
        self.date = date
        self.industry_name, self.industry_code_list = self._get_industry_code_list(mode)

    def _get_industry_code_list(self, mode):
        w.start()
        INDEXCODE = {'sw1': ['indexcode_sw', 'industryType=1'],  # 申万一级行业
                     'sw2': ['indexcode_sw', 'industryType=2'],  # 申万二级行业
                     'sw3': ['indexcode_sw', 'industryType=3'],  # 申万三级行业
                     'sw4': ['indexcode_sw', 'industryType=4'],  # 申万明细行业
                     'wind1': ['indexcode_wind', 'industryType=1'],  # 万得一级行业
                     'wind2': ['indexcode_wind', 'industryType=2'],  # 万得二级行业
                     'wind3': ['indexcode_wind', 'industryType=3'],  # 万得三级行业
                     'wind4': ['indexcode_wind', 'industryType=4'],  # 万得明细行业
                     'citic1': ['indexcode_citic', 'industryType=1'],  # 中信一级
                     'citic2': ['indexcode_citic', 'industryType=2'],  # 中信二级
                     'citic3': ['indexcode_citic', 'industryType=3'],  # 中信三级
                     'amac': ['indexcode_AMAC', ''],  # 基金业协会行业
                     }
        if mode == 'all':  # 提取全部A股
            industry_code_list = w.wset("sectorconstituent", "date="+self.date+";windcode=881001.WI").Data[1]
            industry_name = '全部A股'
        else:  # 按照行业分类提取本行业A股
            industry_code = w.wss(self.code, INDEXCODE[mode][0], 'tradeDate='+self.date+';'+INDEXCODE[mode][1]).Data[0][0]
            industry_code_list = w.wset("sectorconstituent", "date="+self.date+";windcode="+industry_code).Data[1]
            industry_name = w.wss(industry_code, "sec_name").Data[0][0]
        print(industry_code_list)
        print(industry_name)
        return industry_name, industry_code_list

    def output(self):
        result = {'text': ''}
        return result


if __name__ == '__main__':
    code = '000002.SZ'
    date = '2019-03-25'
    mode = 'sw2'
    model = 行业比较分析模板(code, date, mode)
