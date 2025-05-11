# input分を適切な日数、年数に変換するスクリプト

import sys
import datetime


def main():
    input = 765961876346315283100
    print(str(input) + "分は")
    
    # 1日は1440分
    day = input // 1440
    print(str(day) + "日")
    
    # 1年は525600分
    year = input // 525600
    print(str(year) + "年")
    
    # 1億年
    one_hundred_million_years = input // 525600 // 100000000
    print(str(one_hundred_million_years) + "億年")
    
    # 1兆年
    one_trillion_years = input // 525600 // 1000000000000
    print(str(one_trillion_years) + "兆年")
    

if __name__ == '__main__':
    main()