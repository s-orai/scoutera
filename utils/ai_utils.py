"""
AI結果の多数決処理ユーティリティ
"""

import re
from collections import defaultdict, Counter
from typing import List, Any, Optional


def extract_numeric_id(id: str) -> str:
    """
    IDから数値部分を抽出する
    
    Args:
        id: 候補者ID（数字のみ、またはBUから始まるID、または数字を含む文字列）
    
    Returns:
        str: 抽出されたID
    
    Examples:
        >>> extract_numeric_id("123")
        "123"
        >>> extract_numeric_id("BU12345678")
        "BU12345678"
        >>> extract_numeric_id("candidate_456")
        "456"
    """
    # 数字のみかチェック
    if id.isdigit():
        return id
    
    # BUで始まる場合はそのまま返す（抽出処理をスキップ）
    if id.startswith("BU"):
        return id
    
    # 数字以外が含まれている場合は数字のみを抽出
    numeric_only = re.sub(r'\D', '', id)
    return numeric_only


def get_majority_decision_by_id(ai_results: List[Any]) -> List[Any]:
    """
    複数の候補者に対するAI評価結果から、ID毎に多数決を取る
    
    Scout/JDサービスで使用される。各候補者（ID別）に対して3回の評価を行い、
    evaluation_resultで多数決を取る。
    
    Args:
        ai_results: List[ResultsContainer] - 複数回の実行結果のリスト
                    各ResultsContainerは複数のレコード（候補者）を含む
    
    Returns:
        List: ID毎の多数決結果のリスト
    
    Example:
        # 3回の評価結果（各回に複数の候補者）
        results = [
            ResultsContainer(results=[
                AiResult(id="123", evaluation_result="A", ...),
                AiResult(id="456", evaluation_result="B", ...)
            ]),
            ResultsContainer(results=[...]),  # 2回目
            ResultsContainer(results=[...])   # 3回目
        ]
        
        # ID毎に多数決
        final_results = get_majority_decision_by_id(results)
        # → [AiResult(id="123", evaluation_result="A", ...), ...]
    """
    results_by_id = defaultdict(list)
    
    # ID毎に結果を分類
    for inquiry in ai_results:
        for record in inquiry.results:
            # IDから数字のみを抽出
            numeric_id = extract_numeric_id(record.id)
            results_by_id[numeric_id].append(record)
    
    # ID毎に多数決を取る
    final_majority_results = []
    for id, records in results_by_id.items():
        counts = Counter(record.evaluation_result for record in records)
        majority_result = counts.most_common(1)[0][0] if counts else "N/A"
        
        # 多数決結果に一致する最初のレコードを返す
        majority_record = next(
            (record for record in records if record.evaluation_result == majority_result),
            None
        )
        if majority_record:
            final_majority_results.append(majority_record)
        
        print(f"ID: **{id}** の多数決結果: **{majority_result}** (投票: {dict(counts)})")
    
    return final_majority_results


def get_majority_decision_single(ai_results: List[Any]) -> Optional[Any]:
    """
    一人の候補者に対するAI評価結果から多数決を取る
    
    Screeningサービスで使用される。一人の候補者に対して3回の評価を行い、
    evaluation_resultで多数決を取る。
    
    Args:
        ai_results: List[ResultsContainer] - 3回の実行結果のリスト
                    各ResultsContainerは1つのレコード（同じ候補者）を含む
    
    Returns:
        単一のレコード（多数決結果）、または結果が空の場合はNone
    
    Example:
        # 同じ候補者への3回の評価
        results = [
            ResultsContainer(results=[AiResult(evaluation_result="A", ...)]),  # 1回目
            ResultsContainer(results=[AiResult(evaluation_result="A", ...)]),  # 2回目
            ResultsContainer(results=[AiResult(evaluation_result="B", ...)])   # 3回目
        ]
        
        # 多数決（A=2票, B=1票 → Aが採用）
        final_result = get_majority_decision_single(results)
        # → AiResult(evaluation_result="A", ...)
    """
    # 全ての結果レコードを収集
    all_records = []
    for inquiry in ai_results:
        for record in inquiry.results:
            all_records.append(record)
    
    if not all_records:
        print("⚠️ スクリーニング結果が空です")
        return None
    
    # evaluation_resultで多数決を取る
    counts = Counter(record.evaluation_result for record in all_records)
    majority_result = counts.most_common(1)[0][0] if counts else "N/A"
    
    # 多数決結果に一致する最初のレコードを返す
    majority_record = next(
        (record for record in all_records if record.evaluation_result == majority_result),
        None
    )
    
    print(f"✅ スクリーニング多数決結果: **{majority_result}** (投票: {dict(counts)})")
    
    return majority_record
