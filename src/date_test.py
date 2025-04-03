from datetime import datetime

def get_last_day_of_month(year, month):
    if month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        return 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
    else:
        return 31

def test_date_transition():
    # 2024년 12월 31일부터 시작
    current_date = datetime(2024, 12, 31)
    print(f"시작 날짜: {current_date.strftime('%Y-%m-%d')}")
    
    # 24개월 동안의 날짜 전환 테스트
    for _ in range(24):
        if current_date.month == 1:
            current_date = current_date.replace(year=current_date.year - 1, month=12, day=31)
        else:
            last_day = get_last_day_of_month(current_date.year, current_date.month - 1)
            current_date = current_date.replace(month=current_date.month - 1, day=last_day)
        
        print(f"다음 날짜: {current_date.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    test_date_transition() 