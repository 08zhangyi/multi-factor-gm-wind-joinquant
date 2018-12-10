import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn import linear_model
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC


# 针对sklearn的学你模型包装的学习器基类
class BaseLearner(object):
    def __init__(self):
        pass

    def fit(self, factors_return_df):
        return None

    def predict(self, factors_df):
        return None


# SKLearn回归器基类
class BaseLearnerForSKLearnRegressor(BaseLearner):
    def __init__(self, select_number=None, select_ratio=None):
        super().__init__()
        self.regr = None
        self.select_number = select_number
        self.select_ratio = select_ratio

    def fit(self, factors_return_df):
        return_data_train = factors_return_df['return'].values
        del factors_return_df['return']
        factors_data_train = factors_return_df.values
        self.regr.fit(factors_data_train, return_data_train)

    def predict(self, factors_df):
        factors_data_test = factors_df.values
        return_data_test = self.regr.predict(factors_data_test)
        sorted_codes = list(factors_df.index[np.argsort(return_data_test)])  # 收益率预测从小到大排序的股票
        if self.select_number is not None:
            select_codes = sorted_codes[-self.select_number:]
        elif self.select_ratio is not None:
            select_codes = sorted_codes[-int(len(sorted_codes)*self.select_ratio):]
        else:
            raise Exception('选股数量或者选股比例须给出')
        return select_codes


class OrdinaryLinearRegression(BaseLearnerForSKLearnRegressor):
    def __init__(self, select_number=None, select_ratio=None):
        super().__init__(select_number, select_ratio)
        self.regr = linear_model.LinearRegression()


class AdaBoostDecisionTreeRegresor(BaseLearnerForSKLearnRegressor):
    def __init__(self, max_depth=4, n_estimators=20, random_state=np.random.RandomState(1024), select_number=None, select_ratio=None):
        super().__init__(select_number, select_ratio)
        self.regr = AdaBoostRegressor(DecisionTreeRegressor(max_depth=max_depth), n_estimators=n_estimators, random_state=random_state)


# SKLearn分类器基类
class BaseLearnerForSKLearnClassifier(BaseLearner):
    def __init__(self, select_number=None, select_ratio=None):
        super().__init__()
        self.clf = None
        self.select_number = select_number
        self.select_ratio = select_ratio

    def fit(self, factors_return_df):
        # factors_return_df不需要预处理，代码中将大于均值的设为1，小于均值的设为0
        return_data_train = factors_return_df['return'] > factors_return_df['return'].mean()
        return_data_train = return_data_train.replace({True: 1, False: 0})  # 用1和0替换收益率数据
        return_data_train = return_data_train.values
        del factors_return_df['return']
        factors_data_train = factors_return_df.values
        self.clf.fit(factors_data_train, return_data_train)  # 常规训练

    def predict(self, factors_df):
        factors_data_test = factors_df.values
        return_data_test = self.clf.predict_proba(factors_data_test)[:, 1]  # 预测标签为1的概率
        sorted_codes = list(factors_df.index[np.argsort(return_data_test)])  # 预测概率由大到小排序
        if self.select_number is not None:
            select_codes = sorted_codes[-self.select_number:]
        elif self.select_ratio is not None:
            select_codes = sorted_codes[-int(len(sorted_codes)*self.select_ratio):]
        else:
            raise Exception('选股数量或者选股比例须给出')
        return select_codes


class SVMClassifier(BaseLearnerForSKLearnClassifier):
    def __init__(self, cv=5, select_number=None, select_ratio=None):
        super().__init__(select_number, select_ratio)
        self.params = {'C': range(1, 10, 2), 'gamma': [x / 100. for x in range(1, 10, 2)],
                  'kernel': ['linear', 'poly', 'rbf', 'sigmoid']}  # 参数优化
        self.clf = GridSearchCV(SVC(probability=True), self.params, cv=cv)
