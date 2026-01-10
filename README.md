# A股股票异动检测系统

本系统用于实时计算A股股票的异动信息，基于以下规则：

## 异动规则

1. 连续10个交易日内，涨跌幅偏离值累计达 +100%
2. 连续30个交易日内，涨跌幅偏离值累计达 +200%

偏离值计算公式：单只股票涨跌幅 - 对应指数涨跌幅

## 股票与指数对应关系

- 6开头股票（上交所）对应指数代码 000001（上证指数）
- 3开头股票（创业板）对应指数代码 399102（深证成指）
- 0开头股票（深交所）对应指数代码 399107（深证综指）

## 系统功能

1. 获取股票和指数最近40天的收盘价数据
2. 实时计算涨幅
3. 计算偏离值
4. 检测异动条件
5. 反推临界价格和涨幅

## 安装依赖

```bash
pip install -r requirements.txt
```
打包命令
pyinstaller --onefile --console --name "A股股票异动检测系统" --collect-data akshare stock_monitor.py --clean

## 使用方法

### 1. 配置tushare

必须安装tushare并设置token：

1. 安装tushare：`pip install tushare`
2. 注册tushare账号并获取token：https://tushare.pro/
3. token =9f238ba8094b9c34820125808456beb71f4b73f6cbadd5ebf123c03f

### 2. 运行示例

```bash
python example.py
```

或运行主程序：
```bash
python main.py
```

### 3. 在代码中使用

```python
from stock_monitor import StockAnomalyDetector

# 创建检测器实例（会自动使用环境变量中的token）
detector = StockAnomalyDetector()

# 检测股票异动
result = detector.detect_anomaly("600001")

# 输出结果
print(f"是否异动: {result['has_anomaly']}")
print(f"10天偏离: {result['deviation_10d']:.2f}%")
print(f"30天偏离: {result['deviation_30d']:.2f}%")
```

## 输出结果说明

- `has_anomaly`: 是否触发异动（10天偏离≥100% 或 30天偏离≥200%）
- `anomaly_10d`: 10天异动是否触发
- `anomaly_30d`: 30天异动是否触发
- `deviation_10d`: 10天偏离值（个股涨幅 - 指数涨幅）
- `deviation_30d`: 30天偏离值（个股涨幅 - 指数涨幅）
- `critical_price_10d`: 触发10天异动的临界价格（如果已触发则为None）
- `critical_price_30d`: 触发30天异动的临界价格（如果已触发则为None）

## 算法流程

1. 获取股票和对应指数最近40天的收盘价数据
2. 计算10天和30天内的最低收盘价及对应日期
3. 获取当前价格和对应指数当前价格
4. 计算个股和指数的10天、30天涨幅
5. 计算偏离值
6. 判断是否触发异动条件
7. 如未触发，计算临界价格和涨幅