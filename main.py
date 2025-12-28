#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股股票异动检测系统 - 主程序
该系统实现了以下功能：
1. 连续10个交易日内，涨跌幅偏离值累计达 +100%
2. 连续30个交易日内，涨跌幅偏离值累计达 +200%
偏离值计算公式：单只股票涨跌幅 - 对应指数涨跌幅
"""

from stock_monitor import StockAnomalyDetector

def main():
    print("A股股票异动检测系统")
    print("="*50)
    print("功能说明：")
    print("1. 连续10个交易日内，涨跌幅偏离值累计达 +100%")
    print("2. 连续30个交易日内，涨跌幅偏离值累计达 +200%")
    print("偏离值计算公式：单只股票涨跌幅 - 对应指数涨跌幅")
    print("="*50)
    
    try:
        # 创建检测器实例
        detector = StockAnomalyDetector()
        
        # 示例股票代码
        example_stocks = [
            ("603601", "再升科技"),
            ("301005", "超杰"),
            ("002149", "西部材料")
        ]
        
        for stock_code, description in example_stocks:
            print(f"\n检测{description}: {stock_code}")
            try:
                result = detector.detect_anomaly(stock_code)
                
                print(f"  当前价格: {result['current_price']:.2f}")
                print(f"  是否异动: {'是' if result['has_anomaly'] else '否'}")
                print(f"  10天偏离: {result['deviation_10d']:.2f}%")
                print(f"  30天偏离: {result['deviation_30d']:.2f}%")
                
                if result['has_anomaly']:
                    triggered_rules = []
                    if result['anomaly_10d']:
                        triggered_rules.append("10天偏离≥100%")
                    if result['anomaly_30d']:
                        triggered_rules.append("30天偏离≥200%")
                    print(f"  触发规则: {', '.join(triggered_rules)}")
                
                print(f"  10天最低价: {result['min_price_10d']:.2f} ({result['min_date_10d']})")
                print(f"  30天最低价: {result['min_price_30d']:.2f} ({result['min_date_30d']})")
                
                if result['critical_price_10d']:
                    print(f"  10天临界价格: {result['critical_price_10d']:.2f}")
                else:
                    print("  10天异动已触发")
                    
                if result['critical_price_30d']:
                    print(f"  30天临界价格: {result['critical_price_30d']:.2f}")
                else:
                    print("  30天异动已触发")
                    
            except Exception as e:
                print(f"  检测失败: {e}")
    
        print("\n" + "="*50)
        print("系统运行正常")
        
    except ValueError as e:
        print(f"配置错误: {e}")
        print("请确保已安装tushare并设置了TUSHARE_TOKEN环境变量")

if __name__ == "__main__":
    main()