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


# 优矿Adaboost算法，回归版本
class AdaboostRegressor(BaseLearner):
    def __init__(self, select_number=None, select_ratio=None, criteria='Discrimination'):
        super().__init__()
        self.select_number = select_number
        self.select_ratio = select_ratio
        self.criteria = criteria

    def fit(self, factors_return_df, QN=5, L=100, tol=1e-6, fcycle=0):
        criteria = self.criteria
        # 提取收益率数据，使用排序值
        Y = np.array(factors_return_df['return'].values)
        Y = Y.argsort().argsort() / float(len(Y))
        del factors_return_df['return']
        # 提取因子数据，使用排序值
        X = factors_return_df.values.argsort(axis=0).argsort(axis=0) / float(len(factors_return_df))
        # 初始化参数
        hlen = X.shape[0]  # 一共有多少股票（多少行）
        vlen = X.shape[1]  # 一共有多少列（多少个因子）
        eps = 1.0 / hlen
        Weights = np.repeat(1.0 / hlen, hlen)  # 形状（候选股数量，），初始化每个样本的权重相同
        Qs = np.array([np.percentile(X, q, axis=0) for q in np.linspace(0, 100, QN + 1)[1:]])  # 对因子划分QN分组
        # 初始化候选学习器参数，L为最多涉及到的因子数量
        BestFactors = np.array(np.zeros(L), dtype=int)
        BestWsPositive = np.zeros((L, QN))
        BestWsNegative = np.zeros((L, QN))
        BestWs = np.zeros((L, QN))
        WeakRegressorWeights = np.zeros(L)  # 用于记录生成的L个弱分类器的权重
        old_BestFactors = None
        old_BestFactors_list = []
        # 循环L次进行学习
        for i in range(L):
            SignedWeight = (Y * Weights).reshape((-1, 1))  # 根据每个样本的权重极端的优化目标（赋权的优化目标，权重大，目标需要优化的努力相对更多）(候选股数量,1)
            # SignedWeight对于Classifier问题有用，Y为-1或1值，对于Regressor问题相当于加权回归
            Ws_positive = np.zeros((len(Qs), vlen))  # 仅对Classifier问题有用
            Ws_negative = np.zeros((len(Qs), vlen))  # 仅对Classifier问题有用
            Ws = np.zeros((len(Qs), vlen))  # 根据下面的计算，Ws就是每个因子对应权重的组合的收益率 (分组数，因子数）
            Yps = np.zeros((hlen, vlen))  # 单独用每个因子对每个样本的预测值，所以Yps大小为(hlen,vlen)
            # 给定一个样本，Yps输出(1,vlen)大小的值，为vlen个因子对Y值得预测结果（多个预测结果）

            # 第一步是根据分组准备数据的阶段
            for j in range(len(Qs)):  # 对每个分为组进行分析，j为分位组的序号
                if j == 0:  # loc为大小为(hlen,vlen)的True-False矩阵，每个股票是否处于某个因子的第j组中
                    loc = (X <= Qs[j])
                else:
                    loc = (X <= Qs[j]) & (X > Qs[j - 1])
                Quantiled_Weight = Weights.reshape((-1, 1)) * loc  # 根据每个样本的权重，乘以loc会把loc的True变为1，False变为0，也就是根据每个因子的 (股票数，因子数）
                Quantiled_Weight_normed = Quantiled_Weight / (np.sum(Quantiled_Weight, axis=0) + 1e-14)  # 每个因子组内资产权重归一化（列归一化）
                # Quantiled_Weight_normed大小也是(hlen,vlen)，对于每个因子，所有的样本在其上的权重归一化为1，补充解释见下文
                Ws[j] = np.sum(Quantiled_Weight_normed * Y.reshape((-1, 1)), axis=0)  # Ws的形状为(1,vlen)，每个位置记录对应因子按照样本权重计算的加权平均收益率，代表此组的预测能力
                WeakScores = Ws[j]
                Yps += WeakScores * loc  # 对每个分组j累积到Yps中，所有组合的收益率和，由于loc的不重复性（每个股票的每个因子只会落到一组），因此记录的是按照因子分组下的预测能力

            # 分组分析完毕

            # 第二步是根据此时的权重和数据选择合适的因子的阶段
            if criteria == 'Discrimination':  # 表示用区分性最大准则，因子对样本收益预测区分度最大，此准则不用到样本权重
                Zs = np.zeros(vlen)  # Zs为按某个指标计算下每个因子的分数，下同
                for zloc in range(vlen):  # zloc标示第zloc个因子
                    Zs[zloc] = np.sum(np.abs(Ws[:, zloc].reshape((-1, 1)) - Ws[:, zloc]))  # Ws关于每个因子（某列）的收益率交互差（ri-rj绝对值求和，计算收益率离散性的指标），不同j组间的差距
                BestFactors[i] = np.argmax(Zs)  # 第i轮迭代下（第i个弱预测器或者弱分类器的计算）离散性最大的因子取出来，就是现在的weight下此因子对收益率的预测最有区分度
                while old_BestFactors is not None and BestFactors[i] in old_BestFactors_list:
                    Zs[BestFactors[i]] = np.min(Zs)  # 已经在old_BestFactors_list中，不重复选取，选取下一个因子，与fcycle的用处相关
                    BestFactors[i] = np.argmax(Zs)
            else:  # 表示用预测性最好准则，因子对样本收益预测预测性最佳，此准则用到样本权重
                Zs = np.sum(np.abs(Y.reshape((-1, 1)) - Yps) * Weights.reshape((-1, 1)), axis=0)  # 计算每个因子对样本的预测值Yps与真值Y之差的绝对值，用样本权重求和作为误差计算权重
                BestFactors[i] = np.argmin(Zs)  # 寻求在此权重情况下预测误差最小的因子
                while old_BestFactors is not None and BestFactors[i] in old_BestFactors_list:
                    Zs[BestFactors[i]] = np.max(Zs)
                    BestFactors[i] = np.argmin(Zs)
            BestWs[i] = Ws[:, BestFactors[i]]  # 取出此最强预测因子BestFactors[i]的Ws值（此因子的预测值），记录到BestWs中
            Error = np.abs(Y - Yps[:, BestFactors[i]])  # 计算此因子BestFactors[i]预测误差
            MaxError = np.max(Error)
            LinearError = Error / MaxError  # 预测误差比例
            TotalErrorRate = np.sum(Weights * LinearError)  # 根据样本权重计算预测误差评分值
            WeakRegressorWeight = TotalErrorRate / (1 - TotalErrorRate)
            WeakRegressorWeights[i] = WeakRegressorWeight  # 第i个模型的权重，理论是如果预测的比较好（除了个别的其他的都很小），则TotalErrorRate比较小，则WeakRegressorWeight也比较小
            Weights *= WeakRegressorWeight ** (1 - LinearError)
            Weights /= np.sum(Weights)  # 按照Adaboost论文中的方法更新权重，对预测较差的样本加大权重
            if WeakRegressorWeight > 1 - tol:  # 回归足够好，可以跳出
                break

            if i != 0 and np.sum(np.abs(Yps[:, BestFactors[i]])) < tol and BestFactors[i] == old_BestFactors:
                # BestFactors[i]的预测力已经很低了，其跟上一个因子一样，优化完毕，不再计算
                break
            # old_BestFactors_list因子的用处，防止连续选出某几个重复的因子
            old_BestFactors = BestFactors[i]
            old_BestFactors_list.append(BestFactors[i])
            if len(old_BestFactors_list) > fcycle:  # fcycle为表示避免连续重复运用同一因子的参数，为0表示可以连续重复运用一个因子，为1表示至少需要隔一个其他因此才能重复利用此因子
                old_BestFactors_list.pop(0)
        print(BestFactors[:i], BestWs[:i])
        self.model = BestFactors[:i], BestWs[:i], WeakRegressorWeights[:i], Qs, eps

    def predict(self, factors_df):
        model = self.model
        basket_num = self.select_number
        stockCodes = []
        def RobustAdaboostPredict(factors_df, model):
            BestFactors, BestWs, WeakRegressorWeights, Qs, eps = model
            X = factors_df.values.argsort(axis=0).argsort(axis=0) / float(len(factors_df))
            hlen = len(X)  # 形状(候选股票池,0)
            Fp = X[:, BestFactors]
            Qsp = Qs[:, BestFactors]  # Qs类似操作
            Yps = np.zeros((hlen, len(BestFactors)))  # 对BestFactors中的每个因子，根据输入样本的位于分组表中的定位（Qs记录），输出因子的预测值
            for j in range(len(Qs)):
                if j == 0:
                    loc = (Fp < Qsp[j])
                else:
                    loc = (Fp < Qsp[j]) & (Fp > Qsp[j - 1])
                WeakScores = BestWs[:, j]  # 用上个模型计算的BestWs作为预测值
                Yps += WeakScores * loc  # 把每个模型的预测结果记录下来
            # 根据WeakRegressorWeights计算权重并按权重求和记录结果
            Yp = Yps.dot(np.log(1 / WeakRegressorWeights)) / np.sum(np.log(1 / WeakRegressorWeights))
            return Yp
        Yp = RobustAdaboostPredict(factors_df, model)
        yp_rk = Yp.argsort().argsort()  # 预测的排序值 作为factor_df的索引值
        hlen = len(yp_rk)
        stockCodes.append(np.array(factors_df.index)[yp_rk > hlen - basket_num])
        select_code_list = list(stockCodes[0])  # 需要返回一个list格式的股票代码， 与优矿for循环的本质区别：我们这个用了掘金模块，可以按天滚动， 但是优矿策略，算法部分并没有写进回测框架里，所以需要把所有的日期全部遍历一遍
        return select_code_list


# 优矿Adaboost算法，回分类版本
class AdaboostClassifier(BaseLearner):
    def __init__(self, select_number=None, select_ratio=None, clf_ratio=0.3):
        super().__init__()
        self.select_number = select_number
        self.select_ratio = select_ratio
        self.clf_ratio = clf_ratio

    def fit(self, factors_return_df, QN=5, L=100, tol=1e-6, fcycle=0):
        clf_ratio = self.clf_ratio
        # 提取收益率数据，使用排序值
        Y = np.array(factors_return_df['return'].values)
        Y = Y.argsort().argsort() / float(len(Y))
        del factors_return_df['return']
        # 提取因子数据，使用排序值
        Y_temp_loc = (Y < clf_ratio) | (Y > (1.0 - clf_ratio))
        Y = Y[Y_temp_loc]
        Y[Y < clf_ratio] = -1
        Y[Y > (1 - clf_ratio)] = 1 # 最终训练集Y
        X = factors_return_df.values.argsort(axis=0).argsort(axis=0) / float(len(factors_return_df))
        X = X[Y_temp_loc]  # 最终训练集X
        # 初始化参数
        hlen = X.shape[0]  # 一共有多少股票（多少行）
        vlen = X.shape[1]  # 一共有多少列（多少个因子）
        eps = 1.0 / hlen
        Weights = np.repeat(1.0 / hlen, hlen)  # 形状（候选股数量，），初始化每个样本的权重相同
        Qs = np.array([np.percentile(X, q, axis=0) for q in np.linspace(0, 100, QN + 1)[1:]])  # 对因子划分QN分组
        # 初始化候选学习器参数，L为最多涉及到的因子数量
        BestFactors = np.array(np.zeros(L), dtype=int)
        BestWsPositive = np.zeros((L, QN))
        BestWsNegative = np.zeros((L, QN))
        BestWs = np.zeros((L, QN))
        WeakRegressorWeights = np.zeros(L)  # 用于记录生成的L个弱分类器的权重
        old_BestFactors = None
        old_BestFactors_list = []
        # 循环L次进行学习
        for i in range(L):
            SignedWeight = (Y * Weights).reshape((-1, 1))  # 根据每个样本的权重极端的优化目标（赋权的优化目标，权重大，目标需要优化的努力相对更多）(候选股数量,1)
            # SignedWeight对于Classifier问题有用，Y为-1或1值，对于Regressor问题相当于加权回归
            Ws_positive = np.zeros((len(Qs), vlen))  # 仅对Classifier问题有用
            Ws_negative = np.zeros((len(Qs), vlen))  # 仅对Classifier问题有用
            Ws = np.zeros((len(Qs), vlen))  # 根据下面的计算，Ws就是每个因子对应权重的组合的收益率 (分组数，因子数）
            Yps = np.zeros((hlen, vlen))  # 单独用每个因子对每个样本的预测值，所以Yps大小为(hlen,vlen)
            # 给定一个样本，Yps输出(1,vlen)大小的值，为vlen个因子对Y值得预测结果（多个预测结果）

            # 第一步是根据分组准备数据的阶段
            for j in range(len(Qs)):  # 对每个分为组进行分析，j为分位组的序号
                if j == 0:  # loc为大小为(hlen,vlen)的True-False矩阵，每个股票是否处于某个因子的第j组中
                    loc = (X <= Qs[j])
                else:
                    loc = (X <= Qs[j]) & (X > Qs[j - 1])
                Quantiled_SignedWeight = SignedWeight * loc  # 按loc提取实例
                positive_loc = Quantiled_SignedWeight > 0
                negative_loc = Quantiled_SignedWeight < 0  # 获取正负例组合
                Ws_positive[j] = np.sum(Quantiled_SignedWeight * positive_loc, axis=0)  # 预测正例的数量
                Ws_negative[j] = -np.sum(Quantiled_SignedWeight * negative_loc, axis=0)  # 预测负例的数量
                WeakScores = 1.0 / 2.0 * np.log((Ws_positive[j] + eps) / (Ws_negative[j] + eps))  # 根据Adaboost原文计算的采用某个因子的模型权重
                # WeakScores的就是每个因子第j组对正负样本的区分能力
                Yps += WeakScores * loc  # 对每个分组j累积到Yps中，所有组合的收益率和，由于loc的不重复性（每个股票的每个因子只会落到一组），因此记录的是按照因子分组下的预测能力

            # 分组分析完毕

            # 第二步是根据此时的权重和数据选择合适的因子的阶段
            Zs = np.sum(np.sqrt(Ws_positive * Ws_negative), axis=0)  # 正负组合的相关性指标，按照权重计算
            BestFactors[i] = np.argmin(Zs)  # 寻找Zs值最小，也就是要求某一因子的Ws_positive或者Ws_negative小（若样本正负例分布合理，则两者不能同时小），也就是对正例或者负例很有预测力的因子
            while old_BestFactors is not None and BestFactors[i] in old_BestFactors_list:
                Zs[BestFactors[i]] = np.max(Zs)
                BestFactors[i] = np.argmin(Zs)
            BestWsPositive[i] = Ws_positive[:, BestFactors[i]]
            BestWsNegative[i] = Ws_negative[:, BestFactors[i]]  # 记录BestFactors[i]的预测结果
            Weights *= np.exp(-Y * Yps[:, BestFactors[i]])
            Weights /= np.sum(Weights)  # 梯度更新权重


            if i != 0 and np.sum(np.abs(Yps[:, BestFactors[i]])) < tol and BestFactors[i] == old_BestFactors:
                # BestFactors[i]的预测力已经很低了，其跟上一个因子一样，优化完毕，不再计算
                break
            # old_BestFactors_list因子的用处，防止连续选出某几个重复的因子
            old_BestFactors = BestFactors[i]
            old_BestFactors_list.append(BestFactors[i])
            if len(old_BestFactors_list) > fcycle:  # fcycle为表示避免连续重复运用同一因子的参数，为0表示可以连续重复运用一个因子，为1表示至少需要隔一个其他因此才能重复利用此因子
                old_BestFactors_list.pop(0)

        self.model = BestFactors[:i], BestWsPositive[:i], BestWsNegative[:i], Qs, eps

    def predict(self, factors_df):
        model = self.model
        basket_num = self.select_number
        stockCodes = []
        def RobustAdaboostPredict(factors_df, model):
            BestFactors, BestWsPositive, BestWsNegative, Qs, eps = model
            X = factors_df.values.argsort(axis=0).argsort(axis=0) / float(len(factors_df))
            hlen = len(X)  # 形状(候选股票池,0)
            Fp = X[:, BestFactors]
            Qsp = Qs[:, BestFactors]  # Qs类似操作
            Yps = np.zeros((hlen, len(BestFactors)))  # 对BestFactors中的每个因子，根据输入样本的位于分组表中的定位（Qs记录），输出因子的预测值
            for j in range(len(Qs)):
                if j == 0:
                    loc = (Fp < Qsp[j])
                else:
                    loc = (Fp < Qsp[j]) & (Fp > Qsp[j - 1])
                WeakScores = 1.0 / 2.0 * np.log((BestWsPositive[:, j] + eps) / (BestWsNegative[:, j] + eps))
                Yps += WeakScores * loc  # 把每个模型的预测结果记录下来
            Yp = Yps.sum(axis=1)
            return Yp
        Yp = RobustAdaboostPredict(factors_df, model)
        yp_rk = Yp.argsort().argsort()  # 预测的排序值 作为factor_df的索引值
        hlen = len(yp_rk)
        stockCodes.append(np.array(factors_df.index)[yp_rk > hlen - basket_num])
        select_code_list = list(stockCodes[0])  # 需要返回一个list格式的股票代码， 与优矿for循环的本质区别：我们这个用了掘金模块，可以按天滚动， 但是优矿策略，算法部分并没有写进回测框架里，所以需要把所有的日期全部遍历一遍
        return select_code_list