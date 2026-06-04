def calculate_record_points(bristol_type: int, color: str, streak_days: int) -> float:
    """
    計算單次排便紀錄的健康積分。
    
    公式：
        單次積分 = (布里斯托基礎分 * 顏色權重) + 連續天數加成
        
    參數：
        bristol_type (int): 布里斯托大便分類法 (1-7)
        color (str): 大便顏色 ('brown', 'yellow', 'green', 'black', 'red', 'pale')
        streak_days (int): 使用者目前的連續排便紀錄天數
        
    傳回值：
        float: 計算出來的積分值 (四捨五入至小數點後兩位)
    """
    # 1. 布里斯托基礎分
    bristol_base_scores = {
        4: 10.0,  # 香蕉狀 (最健康)
        3: 8.0,   # 有裂紋的香腸狀 (健康)
        5: 6.0,   # 軟團塊 (偏健康)
        2: 4.0,   # 凹凸不平香腸狀 (輕微便秘)
        6: 4.0,   # 糊狀 (輕微腹瀉)
        1: 2.0,   # 顆粒狀 (嚴重便秘)
        7: 2.0    # 水狀 (嚴重腹瀉)
    }
    
    # 預防輸入越界，預設給予基本分數 2.0
    base_score = bristol_base_scores.get(int(bristol_type), 2.0)
    
    # 2. 顏色權重配置
    color_weights = {
        'brown': 1.0,
        'yellow': 1.0,
        'green': 0.8,
        'black': 0.2,
        'red': 0.2,
        'pale': 0.2
    }
    
    # 預防顏色未定義，預設權重為 0.5
    weight = color_weights.get(color.lower(), 0.5)
    
    # 3. 連續天數加成
    # 每連續一天增加 1.5 分，上限 15.0 分
    streak_bonus = min(float(streak_days) * 1.5, 15.0)
    
    # 4. 計算總積分
    total_points = (base_score * weight) + streak_bonus
    
    return round(total_points, 2)
