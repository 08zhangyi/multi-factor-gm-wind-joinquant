from WindPy import w
import sys
sys.path.append('D:\\programs\\多因子策略开发\\单因子研究')
TS_TOKEN = 'fcd3ee99a7d5f0e27c546d074a001f0b3eae01312c4dd8354415fba1'


class 行业比较分析模板():
    def __init__(self, code, date, mode):
        self.code = code
        self.date = date
        self.industry_name, self.industry_code_list = self._get_industry_code_list(code, date, mode)

    def output(self):
        result = []
        return result

    @staticmethod
    def _get_industry_code_list(code, date, mode):
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
            industry_code_list = w.wset("sectorconstituent", "date=" + date + ";windcode=881001.WI").Data[1]
            industry_name = '全部A股'
        else:  # 按照行业分类提取本行业A股
            industry_code = w.wss(code, INDEXCODE[mode][0], 'tradeDate=' + date + ';' + INDEXCODE[mode][1]).Data[0][0]
            industry_code_list = w.wset("sectorconstituent", "date=" + date + ";windcode=" + industry_code).Data[1]
            industry_name = w.wss(industry_code, "sec_name").Data[0][0]
        return industry_name, industry_code_list

    @staticmethod
    def _get_last_season_end(date):
        year = int(date[0:4])
        month = int(date[5:7])
        season = (month - 1) // 3
        if season == 0:
            last_season_end = str(year - 1) + '-12-31'
        elif season == 1:
            last_season_end = str(year) + '-03-31'
        elif season == 2:
            last_season_end = str(year) + '-06-30'
        else:
            last_season_end = str(year) + '-09-30'
        return last_season_end

    @staticmethod
    def _get_last_year_end(date):
        year = int(date[0:4])
        last_year_end = str(year - 1) + '-12-31'
        return last_year_end

    @staticmethod
    def _get_last_year_date(date):
        year = int(date[0:4])
        last_year_date = str(year - 1) + date[4:]
        return last_year_date

    @staticmethod
    def tushare_date_format(date):
        date = ''.join(date.split('-'))
        return date


if __name__ == '__main__':
    code = '000002.SZ'
    date = '2019-03-25'
    mode = 'sw2'
    model = 行业比较分析模板(code, date, mode)
