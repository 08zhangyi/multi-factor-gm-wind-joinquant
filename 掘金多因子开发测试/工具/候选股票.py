from WindPy import w


# 股票池基类，直接使用给定的股票池
class SelectedStockPool(object):
    def __init__(self, code_list, date):
        self.code_list = code_list
        self.date = date  # 股票池计算日期为date日收盘后

    def get_stock_pool(self):
        return self.code_list


# 从指数列表中选股股票
class SelectedStockPoolFromList(SelectedStockPool):
    def __init__(self, included_index_list, date):
        w.start()
        all_code_set = set()
        for index in included_index_list:
            code_set = set(w.wset("sectorconstituent", "date=" + date + ";windcode=" + index).Data[1])
            all_code_set = all_code_set | code_set
        self.code_list = list(all_code_set)


# 从指数列表中选取股票并且剔除部分无用的股票
class SelectedStockPoolFromListExcluded(SelectedStockPool):
    def __init__(self, included_index_list, excluded_index_list, date):
        w.start()
        all_code_set = set()
        for index in included_index_list:
            code_set = set(w.wset("sectorconstituent", "date=" + date + ";windcode=" + index).Data[1])
            all_code_set = all_code_set | code_set
        for index in excluded_index_list:
            code_set = set(w.wset("sectorconstituent", "date=" + date + ";windcode=" + index).Data[1])
            all_code_set = all_code_set.difference(code_set)
        self.code_list = list(all_code_set)


if __name__ == '__main__':
    date = '2021-04-20'
    included_index_list = ['000300.SH', '000016.SH']
    stock_pool = SelectedStockPoolFromList(included_index_list, date).get_stock_pool()
    print(stock_pool)
    print(len(stock_pool))

    date = '2021-04-20'
    included_index_list = ['000300.SH']
    excluded_index_list = ['000016.SH']
    stock_pool = SelectedStockPoolFromListExcluded(included_index_list, excluded_index_list, date).get_stock_pool()
    print(stock_pool)
    print(len(stock_pool))