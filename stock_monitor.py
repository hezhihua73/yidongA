import requests
from datetime import datetime, timedelta
import pandas as pd
import tushare as ts
import akshare as ak

class StockAnomalyDetector:
    """
    A股股票异动信息实时计算类
    """

    def __init__(self):
        # 从README中直接获取tushare token
        token = '9f238ba8094b9c34820125808456beb71f4b73f6cbadd5ebf123c03f'
        if token:
            try:
                ts.set_token(token)
                self.pro = ts.pro_api()
            except Exception as e:
                raise ValueError(f"tushare初始化失败: {e}。请确认token是否正确，以及是否有权限访问相关接口")
        else:
            raise ValueError("请设置TUSHARE_TOKEN环境变量")

        # 股票代码前缀对应的指数代码映射
        self.index_mapping = {
            '6': '000001',  # 上证指数
            '3': '399102',  # 创业板指
            '0': '399107'   # 深证综指
        }

    def get_stock_data(self, stock_code, days=40):
        """
        获取股票最近N天的收盘价数据（使用tushare）
        """
        try:
            if stock_code.startswith('6'):
                ts_code = f'{stock_code}.SH'
            else:
                ts_code = f'{stock_code}.SZ'

            df = self.pro.daily(ts_code=ts_code,
                           start_date=(datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d'),
                           end_date=datetime.now().strftime('%Y%m%d'))

            if df.empty:
                raise ValueError(f"无法获取股票{stock_code}的数据，请确认股票代码是否正确")

            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
            df.rename(columns={'trade_date': 'date'}, inplace=True)
            return df[['date', 'close']].reset_index(drop=True)
        except Exception as e:
            error_msg = str(e)
            if "token" in error_msg.lower() or "权限" in error_msg or "认证" in error_msg:
                raise Exception("tushare认证失败，请检查token是否正确设置，以及是否有权限访问daily接口")
            raise Exception(f"获取股票{stock_code}数据时出错: {e}")

    def get_index_data(self, index_code, days=40):
        """
        获取指数最近N天的收盘价数据（使用AKShare）
        """
        try:
            # 使用AKShare获取指数数据
            start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
            end_date = datetime.now().strftime('%Y%m%d')

            if index_code == '000001':
                # 上证指数
                df = ak.stock_zh_index_daily_em(symbol=f"sh{index_code}")
            elif index_code == '399102':
                # 深证成指
                df = ak.stock_zh_index_daily_em(symbol=f"sz{index_code}")
            elif index_code == '399107':
                # 深证综指
                df = ak.stock_zh_index_daily_em(symbol=f"sz{index_code}")
            else:
                raise ValueError(f"不支持的指数代码: {index_code}")

            # 过滤日期范围
            df['date'] = pd.to_datetime(df['date']).dt.date
            df = df[(df['date'] >= datetime.strptime(start_date, '%Y%m%d').date()) &
                    (df['date'] <= datetime.strptime(end_date, '%Y%m%d').date())]

            if df.empty:
                raise ValueError(f"无法获取指数{index_code}的数据")

            # 选择需要的列并重置索引
            df = df[['date', 'close']].iloc[::-1].reset_index(drop=True)
            return df
        except Exception as e:
            raise Exception(f"获取指数{index_code}数据时出错 (使用AKShare): {e}")

    def calculate_growth_rate(self, current_price, start_price):
        """
        计算涨幅
        涨幅=（现在价格-起点价格）/起点价格 * 100
        """
        if start_price == 0:
            return 0
        return (current_price - start_price) / start_price * 100

    def find_min_price_in_period(self, stock_data, days):
        """
        找到指定天数内的最低收盘价及对应日期
        """
        if len(stock_data) < days:
            recent_data = stock_data
        else:
            recent_data = stock_data.head(days)

        if recent_data.empty:
            return None, None

        min_idx = recent_data['close'].idxmin()
        min_price = recent_data.loc[min_idx, 'close']
        min_date = recent_data.loc[min_idx, 'date']
        # 间隔交易日 30 和 10 是极限
        min_mid_day = min_idx + 1
        return min_price, min_date, min_mid_day

    def get_current_price(self, stock_code):
        """
        获取股票当前价格（使用tushare）
        如果获取失败，返回stock_data最新一天的价格
        """
        try:
            if stock_code.startswith('6'):
                ts_code = f'{stock_code}.SH'
            else:
                ts_code = f'{stock_code}.SZ'

            df = self.pro.daily(ts_code=ts_code,
                           start_date=datetime.now().strftime('%Y%m%d'),
                           end_date=datetime.now().strftime('%Y%m%d'))
            if not df.empty:
                return df.iloc[0]['close']
            else:
                raise ValueError(f"无法获取股票{stock_code}的实时数据")
        except Exception as e:
            error_msg = str(e)
            if "token" in error_msg.lower() or "权限" in error_msg or "认证" in error_msg:
                # 如果tushare认证失败，获取历史数据的最新价格作为当前价格
                try:
                    if stock_code.startswith('6'):
                        ts_code = f'{stock_code}.SH'
                    else:
                        ts_code = f'{stock_code}.SZ'

                    df = self.pro.daily(ts_code=ts_code,
                                   start_date=(datetime.now() - timedelta(days=5)).strftime('%Y%m%d'),
                                   end_date=datetime.now().strftime('%Y%m%d'))

                    if not df.empty:
                        df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
                        df.rename(columns={'trade_date': 'date'}, inplace=True)
                        # 返回最新一天的价格
                        return df.iloc[0]['close']
                except:
                    pass  # 如果再次失败，继续执行下面的逻辑
            # 如果实时数据获取失败，返回错误信息，但我们会通过其他方式处理
            raise Exception(f"获取股票{stock_code}实时数据时出错: {e}")

    def get_index_current_price(self, index_code):
        """
        获取指数当前价格（使用AKShare）
        如果获取失败，返回index_data最新一天的价格
        """
        try:
            if index_code == '000001':
                # 上证指数
                df = ak.stock_zh_index_spot_em()
                index_data = df[df['代码'] == index_code]
            elif index_code == '399102':
                # 创业板指
                df = ak.stock_zh_index_spot_em()
                index_data = df[df['代码'] == index_code]
            elif index_code == '399107':
                # 深证综指
                df = ak.stock_zh_index_spot_em()
                index_data = df[df['代码'] == index_code]
            else:
                raise ValueError(f"不支持的指数代码: {index_code}")

            if not index_data.empty:
                return float(index_data.iloc[0]['最新价'])
            else:
                raise ValueError(f"无法获取指数{index_code}的实时数据")
        except Exception as e:
            # 如果实时数据获取失败，使用日线数据的最新值
            try:
                symbol = f"sh{index_code}" if index_code == '000001' else f"sz{index_code}"
                df_daily = ak.stock_zh_index_daily_em(symbol=symbol)
                if not df_daily.empty:
                    df_daily['date'] = pd.to_datetime(df_daily['date']).dt.date
                    # 返回最新一天的价格
                    return df_daily['close'].iloc[-1]
            except:
                pass  # 如果再次失败，继续执行下面的逻辑
            raise Exception(f"获取指数{index_code}实时数据时出错 (使用AKShare): {e}")

    def get_price_by_date(self, data, target_date):
        """
        根据日期获取对应的价格
        """
        # 确保target_date是date类型
        if isinstance(target_date, datetime):
            target_date = target_date.date()

        matching_row = data[data['date'] == target_date]
        if not matching_row.empty:
            return matching_row.iloc[0]['close']
        else:
            # 如果没有找到精确匹配的日期，返回最接近的日期的价格
            if len(data) == 0:
                return None

            # 找到最接近的日期
            data['date_diff'] = abs(data['date'] - target_date)
            closest_idx = data['date_diff'].idxmin()
            closest_price = data.loc[closest_idx, 'close']
            data.drop('date_diff', axis=1, inplace=True)  # 清理临时列
            return closest_price

    def detect_anomaly(self, stock_code):
        """
        检测股票异动
        """
        # 1. 获取股票和对应指数代码
        index_prefix = stock_code[0]
        index_code = self.index_mapping.get(index_prefix)
        if not index_code:
            raise ValueError(f"不支持的股票代码前缀: {index_prefix}")

        # 2. 获取股票和指数最近40天的数据
        stock_data = self.get_stock_data(stock_code)
        index_data = self.get_index_data(index_code)

        if stock_data.empty or index_data.empty:
            raise ValueError("无法获取股票或指数数据")

        # 3. 获取当前价格 - 如果获取实时价格失败，使用stock_data最新一天的价格
        try:
            current_stock_price = self.get_current_price(stock_code)
        except:
            # 如果实时价格获取失败，使用stock_data最新一天的价格
            current_stock_price = stock_data['close'].iloc[0]

        try:
            current_index_price = self.get_index_current_price(index_code)
        except:
            print("指数实时价格获取失败，使用上一交易日收盘价格")
            # 如果实时指数价格获取失败，使用index_data最新一天的价格
            current_index_price = index_data['close'].iloc[0]
        print(f"指数价格: {current_index_price:.2f}")

        # 4. 计算10天和30天的最低价格及对应日期
        min_10d_price, min_10d_date, min_10mid_day = self.find_min_price_in_period(stock_data, 10)
        min_30d_price, min_30d_date, min_30mid_day = self.find_min_price_in_period(stock_data, 30)

        if min_10d_price is None or min_30d_price is None:
            raise ValueError("无法找到指定周期内的最低价格")

        # 5. 获取对应日期的指数价格
        index_price_10d = self.get_price_by_date(index_data, min_10d_date)
        index_price_30d = self.get_price_by_date(index_data, min_30d_date)

        if index_price_10d is None or index_price_30d is None:
            raise ValueError("无法获取对应日期的指数价格")

        # 6. 计算涨幅
        stock_growth_10d = self.calculate_growth_rate(current_stock_price, min_10d_price)
        stock_growth_30d = self.calculate_growth_rate(current_stock_price, min_30d_price)

        index_growth_10d = self.calculate_growth_rate(current_index_price, index_price_10d)
        index_growth_30d = self.calculate_growth_rate(current_index_price, index_price_30d)

        # 7. 计算偏离值
        deviation_10d = stock_growth_10d - index_growth_10d
        deviation_30d = stock_growth_30d - index_growth_30d

        # 8. 判断是否触发异动
        anomaly_10d = deviation_10d >= 100
        anomaly_30d = deviation_30d >= 200
        has_anomaly = anomaly_10d or anomaly_30d

        # 9. 反推最大涨幅和价格（如果未触发异动但接近触发）
        critical_price_10d = None
        critical_growth_10d = None
        critical_growth_10d_gap = None
        critical_price_30d = None
        critical_growth_30d = None
        critical_growth_30d_gap = None
        critical_price_9d = None
        critical_growth_9d_gap = None
        critical_price_29d = None
        critical_growth_29d_gap = None

        if not anomaly_10d:
            # 计算触发10天异动所需的临界价格
            required_index_growth_10d = index_growth_10d + 100
            required_stock_price_10d = min_10d_price * (1 + required_index_growth_10d / 100)
            critical_price_10d = required_stock_price_10d
            critical_growth_10d = self.calculate_growth_rate(required_stock_price_10d, min_10d_price)
            critical_growth_10d_gap = (required_stock_price_10d - current_stock_price) / current_stock_price * 100

        if not anomaly_30d:
            # 计算触发30天异动所需的临界价格
            required_index_growth_30d = index_growth_30d + 200
            required_stock_price_30d = min_30d_price * (1 + required_index_growth_30d / 100)
            critical_price_30d = required_stock_price_30d
            critical_growth_30d = self.calculate_growth_rate(required_stock_price_30d, min_30d_price)
            critical_growth_30d_gap = (required_stock_price_30d - current_stock_price) / current_stock_price * 100

        if not anomaly_10d:
            if critical_growth_10d_gap < 20.0:
                # 如果涨幅空间小于20了,则计算下一天的空间
                min_9d_price, min_9d_date, min_9mid_day = self.find_min_price_in_period(stock_data, 9)
                index_price_9d = self.get_price_by_date(index_data, min_9d_date)
                stock_growth_9d = self.calculate_growth_rate(current_stock_price, min_9d_price)
                index_growth_9d = self.calculate_growth_rate(current_index_price, index_price_9d)
                deviation_9d = stock_growth_9d - index_growth_9d
                # 计算触发9天异动所需的临界价格
                required_index_growth_9d = index_growth_9d + 100
                required_stock_price_9d = min_9d_price * (1 + required_index_growth_9d / 100)
                critical_price_9d = required_stock_price_9d
                critical_growth_9d = self.calculate_growth_rate(required_stock_price_9d, min_9d_price)
                critical_growth_9d_gap = (required_stock_price_9d - current_stock_price) / current_stock_price * 100

        if not anomaly_30d:
            if critical_growth_30d_gap < 20.0:
                # 如果涨幅空间小于20了,则计算下一天的空间
                min_29d_price, min_29d_date, min_29mid_day = self.find_min_price_in_period(stock_data, 29)
                index_price_29d = self.get_price_by_date(index_data, min_29d_date)
                stock_growth_29d = self.calculate_growth_rate(current_stock_price, min_29d_price)
                index_growth_29d = self.calculate_growth_rate(current_index_price, index_price_29d)
                deviation_29d = stock_growth_29d - index_growth_29d
                # 计算触发29天异动所需的临界价格
                required_index_growth_29d = index_growth_29d + 200
                required_stock_price_29d = min_29d_price * (1 + required_index_growth_29d / 100)
                critical_price_29d = required_stock_price_29d
                critical_growth_29d = self.calculate_growth_rate(required_stock_price_29d, min_29d_price)
                critical_growth_29d_gap = (required_stock_price_29d - current_stock_price) / current_stock_price * 100

        result = {
            'stock_code': stock_code,
            'index_code': index_code,
            'current_price': current_stock_price,
            'has_anomaly': has_anomaly,
            'anomaly_10d': anomaly_10d,
            'anomaly_30d': anomaly_30d,
            'deviation_10d': deviation_10d,
            'deviation_30d': deviation_30d,
            'stock_growth_10d': stock_growth_10d,
            'stock_growth_30d': stock_growth_30d,
            'index_growth_10d': index_growth_10d,
            'index_growth_30d': index_growth_30d,
            'min_price_10d': min_10d_price,
            'min_date_10d': min_10d_date,
            'min_price_30d': min_30d_price,
            'min_date_30d': min_30d_date,
            'critical_price_10d': critical_price_10d,
            'critical_growth_10d': critical_growth_10d,
            'critical_price_30d': critical_price_30d,
            'critical_growth_30d': critical_growth_30d,
            'critical_growth_10d_gap': critical_growth_10d_gap,
            'critical_growth_30d_gap': critical_growth_30d_gap,
            'min_10mid_day': min_10mid_day,
            'min_30mid_day': min_30mid_day,
            'critical_price_9d': critical_price_9d,
            'critical_growth_9d_gap': critical_growth_9d_gap,
            'critical_price_29d':critical_price_29d,
            'critical_growth_29d_gap':critical_growth_29d_gap,
        }

        return result


def display_result(result):
    """显示检测结果"""
    print(f"  上一个交易日收盘价格: {result['current_price']:.2f}")
    print(f"  是否异动: {'是' if result['has_anomaly'] else '否'}")

    # 使用颜色标识偏离值（仅在支持的终端中显示）
    dev_10d_str = f"{result['deviation_10d']:.2f}%"
    dev_30d_str = f"{result['deviation_30d']:.2f}%"

    print(f"  10天偏离: {dev_10d_str}")
    print(f"  30天偏离: {dev_30d_str}")

    if result['has_anomaly']:
        triggered_rules = []
        if result['anomaly_10d']:
            triggered_rules.append("10天偏离≥100%")
        if result['anomaly_30d']:
            triggered_rules.append("30天偏离≥200%")
        print(f"  触发规则: {', '.join(triggered_rules)}")

    print(f"  10天最低价: {result['min_price_10d']:.2f} ({result['min_date_10d']}) {result['min_10mid_day']}天")
    print(f"  30天最低价: {result['min_price_30d']:.2f} ({result['min_date_30d']}) {result['min_30mid_day']}天")

    if result['critical_price_10d']:
        print(f"  10天临界价格: {result['critical_price_10d']:.2f} (临界涨幅: {result['critical_growth_10d_gap']:.2f}%)")
    else:
        print("  10天异动已触发")

    if result['critical_price_30d']:
        print(f"  30天临界价格: {result['critical_price_30d']:.2f} (临界涨幅: {result['critical_growth_30d_gap']:.2f}%)")
    else:
        print("  30天异动已触发")

    if result['critical_price_9d'] is not None:
        print(f"  明日10天临界价格: {result['critical_price_9d']:.2f} (临界涨幅: {result['critical_growth_9d_gap']:.2f}%)")

    if result['critical_price_29d'] is not None:
        print(f"  明日30天临界价格: {result['critical_price_29d']:.2f} (临界涨幅: {result['critical_growth_29d_gap']:.2f}%)")


def main():
    # 设置控制台编码为UTF-8以处理中文字符
    import sys
    import io

    # 尝试设置控制台编码
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        # 如果设置失败，继续执行
        pass

    print("=" * 60)
    print("                   A股股票异动检测系统")
    print("=" * 60)
    print("功能说明：")
    print("1. 连续10个交易日内，涨跌幅偏离值累计达 +100%")
    print("2. 连续30个交易日内，涨跌幅偏离值累计达 +200%")
    print("偏离值计算公式：单只股票涨跌幅 - 对应指数涨跌幅")
    print("最低价日期间隔天数，最大值为10，30")
    print("=" * 60)

    try:
        # 创建检测器实例
        detector = StockAnomalyDetector()

        print("\n欢迎使用A股股票异动检测系统")
        print("提示：")
        print("  - 输入6位股票代码开始检测")
        print("  - 输入 'quit', 'exit', 'q' 或 '退出' 退出程序")
        print("  - 输入 'help' 查看帮助信息")

        while True:
            try:
                stock_input = input("\n>>> 请输入股票代码: ").strip()

                if stock_input.lower() in ['quit', 'exit', 'q', '退出']:
                    print("感谢使用，再见！")
                    input("按回车键退出...\n")  # 添加这行以保持窗口打开
                    break
                elif stock_input.lower() == 'help':
                    print("\n帮助信息：")
                    print("  - 本系统用于检测A股股票异动情况")
                    print("  - 10天偏离：股票在最近10个交易日内的涨幅偏离指数的幅度")
                    print("  - 30天偏离：股票在最近30个交易日内的涨幅偏离指数的幅度")
                    print("  - 异动触发：10天偏离≥100% 或 30天偏离≥200%")
                    continue

                # 验证输入格式
                if not stock_input.isdigit() or len(stock_input) != 6:
                    print("错误: 股票代码应为6位数字，请重新输入")
                    continue

                print(f"\n正在检测股票: {stock_input} ...")
                result = detector.detect_anomaly(stock_input)

                try:
                    # 获取股票名称
                    stock_name = ak.stock_info_a_code_name().set_index("code").loc[stock_input, "name"]
                    print(f"\n股票名称: {stock_name}")
                except:
                    print(f"股票名称查询异常")

                print(f"检测完成！")
                print("-" * 40)
                display_result(result)
                print("-" * 40)

            except ValueError as e:
                if "不支持的股票代码前缀" in str(e):
                    print(f"错误: 不支持的股票代码前缀，请输入A股股票代码(6位数字)")
                else:
                    print(f"错误: {e}")
            except Exception as e:
                print(f"错误: 检测失败: {e}")

        print("\n" + "=" * 60)
        print("                            系统已退出")
        print("=" * 60)
        input("按回车键退出...\n")  # 添加这行以保持窗口打开

    except ValueError as e:
        print(f"错误: 配置错误: {e}")
        print("请确保已安装tushare并设置了TUSHARE_TOKEN环境变量")
        input("按回车键退出...\n")  # 添加这行以保持窗口打开
    except Exception as e:
        print(f"错误: 系统错误: {e}")
        print("请检查是否已安装必要的依赖库")
        input("按回车键退出...\n")  # 添加这行以保持窗口打开


if __name__ == "__main__":
    main()