#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股票异动检测测试 - 模拟触发异动的场景
"""
from stock_monitor import StockAnomalyDetector
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def test_with_custom_data():
    """
    使用自定义数据测试异动检测，模拟可能触发异动的情况
    """
    print("使用自定义数据测试异动检测")
    print("="*50)
    
    # 创建一个StockAnomalyDetector实例
    detector = StockAnomalyDetector()
    
    # 模拟一个可能触发异动的股票数据
    # 创建30天的数据，其中前10天价格较低，后面价格快速上涨
    dates = pd.date_range(end=datetime.now(), periods=40, freq='D')
    # 过滤掉周末，模拟交易日
    dates = [date for date in dates if date.weekday() < 5][:30]  # 取前30个交易日
    
    # 构造一个可能触发异动的价格序列
    # 前10天价格较低（10元左右），后20天快速上涨到20元以上
    base_prices_first_part = [10.0 + np.random.uniform(-0.5, 0.5) for _ in range(10)]  # 前10天低价
    base_prices_second_part = [20.0 + i*0.5 + np.random.uniform(-0.2, 0.2) for i in range(20)]  # 后20天上涨
    prices = base_prices_first_part + base_prices_second_part
    
    # 确保日期和价格数组长度一致
    if len(dates) != len(prices):
        # 如果长度不一致，调整到一致
        min_len = min(len(dates), len(prices))
        dates = dates[:min_len]
        prices = prices[:min_len]
    
    # 创建股票数据
    stock_df = pd.DataFrame({
        'date': [date.date() for date in dates],
        'close': prices
    })
    
    # 模拟指数数据，涨幅较小
    index_prices = [3000.0 + i*2 + np.random.uniform(-10, 10) for i in range(len(dates))]
    index_df = pd.DataFrame({
        'date': [date.date() for date in dates],
        'close': index_prices
    })
    
    # 获取当前价格（最新价格）
    current_stock_price = prices[-1]  # 最后一个价格作为当前价格
    current_index_price = index_prices[-1]  # 指数当前价格
    
    # 计算10天内的最低价格和日期
    if len(prices) >= 10:
        min_10d_price = min(prices[-10:])  # 最近10天最低价
        min_10d_idx = prices[-10:].index(min_10d_price) + len(prices) - 10  # 在整个列表中的索引
    else:
        min_10d_price = min(prices)  # 如果不足10天，取全部最低价
        min_10d_idx = prices.index(min_10d_price)
    min_10d_date = dates[min_10d_idx].date()
    
    # 计算30天内的最低价格和日期
    min_30d_price = min(prices)  # 30天最低价
    min_30d_idx = prices.index(min_30d_price)  # 在整个列表中的索引
    min_30d_date = dates[min_30d_idx].date()
    
    # 找到对应日期的指数价格
    # 使用更安全的访问方式
    matching_index_10d = index_df[index_df['date'] == min_10d_date]
    if len(matching_index_10d) > 0:
        index_price_10d = matching_index_10d.iloc[0]['close']
    else:
        index_price_10d = index_prices[min_10d_idx]
    
    matching_index_30d = index_df[index_df['date'] == min_30d_date]
    if len(matching_index_30d) > 0:
        index_price_30d = matching_index_30d.iloc[0]['close']
    else:
        index_price_30d = index_prices[min_30d_idx]
    
    # 计算涨幅
    stock_growth_10d = detector.calculate_growth_rate(current_stock_price, min_10d_price)
    stock_growth_30d = detector.calculate_growth_rate(current_stock_price, min_30d_price)
    index_growth_10d = detector.calculate_growth_rate(current_index_price, index_price_10d)
    index_growth_30d = detector.calculate_growth_rate(current_index_price, index_price_30d)
    
    # 计算偏离值
    deviation_10d = stock_growth_10d - index_growth_10d
    deviation_30d = stock_growth_30d - index_growth_30d
    
    # 判断是否触发异动
    anomaly_10d = deviation_10d >= 100
    anomaly_30d = deviation_30d >= 200
    has_anomaly = anomaly_10d or anomaly_30d
    
    print(f"股票代码: 600001 (模拟)")
    print(f"对应指数: 000001")
    print(f"当前价格: {current_stock_price:.2f}")
    print(f"是否异动: {'是' if has_anomaly else '否'}")
    print(f"10天偏离: {deviation_10d:.2f}%")
    print(f"30天偏离: {deviation_30d:.2f}%")
    print(f"10天股票涨幅: {stock_growth_10d:.2f}%")
    print(f"30天股票涨幅: {stock_growth_30d:.2f}%")
    print(f"10天指数涨幅: {index_growth_10d:.2f}%")
    print(f"30天指数涨幅: {index_growth_30d:.2f}%")
    print(f"10天最低价: {min_10d_price:.2f} ({min_10d_date})")
    print(f"30天最低价: {min_30d_price:.2f} ({min_30d_date})")
    print(f"10天异动触发: {'是' if anomaly_10d else '否'}")
    print(f"30天异动触发: {'是' if anomaly_30d else '否'}")
    
    # 计算临界价格
    if not anomaly_10d:
        required_index_growth_10d = index_growth_10d + 100
        required_stock_price_10d = min_10d_price * (1 + required_index_growth_10d / 100)
        critical_growth_10d = detector.calculate_growth_rate(required_stock_price_10d, min_10d_price)
        print(f"10天临界价格: {required_stock_price_10d:.2f}")
        print(f"10天临界涨幅: {critical_growth_10d:.2f}%")
    else:
        print("10天异动已触发")
        
    if not anomaly_30d:
        required_index_growth_30d = index_growth_30d + 200
        required_stock_price_30d = min_30d_price * (1 + required_index_growth_30d / 100)
        critical_growth_30d = detector.calculate_growth_rate(required_stock_price_30d, min_30d_price)
        print(f"30天临界价格: {required_stock_price_30d:.2f}")
        print(f"30天临界涨幅: {critical_growth_30d:.2f}%")
    else:
        print("30天异动已触发")

def test_normal_functionality():
    """
    测试正常功能
    """
    print("\n正常功能测试")
    print("="*50)
    
    detector = StockAnomalyDetector()
    
    # 使用模拟数据测试
    try:
        result = detector.detect_anomaly("600001")
        print(f"股票600001异动检测结果: {result['has_anomaly']}")
        print(f"10天偏离: {result['deviation_10d']:.2f}%")
        print(f"30天偏离: {result['deviation_30d']:.2f}%")
        print(f"当前价格: {result['current_price']:.2f}")
        if result['critical_price_10d']:
            print(f"10天临界价格: {result['critical_price_10d']:.2f}")
        else:
            print("10天异动已触发")
        if result['critical_price_30d']:
            print(f"30天临界价格: {result['critical_price_30d']:.2f}")
        else:
            print("30天异动已触发")
    except Exception as e:
        print(f"检测股票600001时出错: {e}")

if __name__ == "__main__":
    test_with_custom_data()
    test_normal_functionality()