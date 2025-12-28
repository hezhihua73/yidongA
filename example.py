#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股票异动检测使用示例
"""
from stock_monitor import StockAnomalyDetector
import os

def main():
    print("A股股票异动检测系统")
    print("="*50)
    
    try:
        # 创建异动检测器实例（会自动使用环境变量中的token）
        detector = StockAnomalyDetector()
        
        # 测试股票列表
        test_stocks = [
            "601600",  # 上证股票
            "301306",  # 深证创业板股票
            "000547"   # 深证主板股票
        ]
        
        for stock_code in test_stocks:
            print(f"\n正在检测股票: {stock_code}")
            try:
                result = detector.detect_anomaly(stock_code)
                
                print(f"  股票代码: {result['stock_code']}")
                print(f"  对应指数: {result['index_code']}")
                print(f"  当前价格: {result['current_price']:.2f}")
                print(f"  是否异动: {'是' if result['has_anomaly'] else '否'}")
                print(f"  10天偏离: {result['deviation_10d']:.2f}%")
                print(f"  30天偏离: {result['deviation_30d']:.2f}%")
                print(f"  10天股票涨幅: {result['stock_growth_10d']:.2f}%")
                print(f"  30天股票涨幅: {result['stock_growth_30d']:.2f}%")
                print(f"  10天指数涨幅: {result['index_growth_10d']:.2f}%")
                print(f"  30天指数涨幅: {result['index_growth_30d']:.2f}%")
                print(f"  10天最低价: {result['min_price_10d']:.2f} ({result['min_date_10d']})")
                print(f"  30天最低价: {result['min_price_30d']:.2f} ({result['min_date_30d']})")
                
                if result['critical_price_10d']:
                    print(f"  10天临界价格: {result['critical_price_10d']:.2f}")
                    print(f"  10天临界涨幅: {result['critical_growth_10d']:.2f}%")
                else:
                    print("  10天异动已触发")
                    
                if result['critical_price_30d']:
                    print(f"  30天临界价格: {result['critical_price_30d']:.2f}")
                    print(f"  30天临界涨幅: {result['critical_growth_30d']:.2f}%")
                else:
                    print("  30天异动已触发")
                    
            except Exception as e:
                print(f"  检测股票{stock_code}时出错: {e}")
    
        print("\n" + "="*50)
        print("检测完成")
        
    except ValueError as e:
        print(f"配置错误: {e}")
        print("请确保已安装tushare并设置了TUSHARE_TOKEN环境变量")

if __name__ == "__main__":
    main()