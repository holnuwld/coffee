import json
import verify_similarity_display

top_20 = verify_similarity_display.top_20

print("Evaluating Active vs Dimmed with 'Same farm but different cup notes => KEEP'")
for c in top_20:
    rank = c['rank']
    sim = c['max_prior_sim']
    target_rank = c['similar_target_rank']
    target_title = c['similar_target_title']
    dt = c['similar_details']
    
    # Check duplicate exclusion rule:
    # 1. Very high similarity (>=70%): Los Lajones 26C (84.3%), Adaura Washed (84.6%), Elto River Flow (82.9%)
    # 2. Same farm AND overlapping cup notes (dt['same_farm'] and dt['notes_jaccard'] > 20)
    # 3. Same sub-category duplicate (e.g. Panama Washed Geisha parallel lots: Chevas, Mil Cumbres)
    is_dup = False
    dup_reason = ""
    
    if sim >= 70.0:
        is_dup = True
        dup_reason = f"🚫 #{target_rank}위 {target_title}과 유사도 {sim}% (동일 농장/랏/가공 고도 중복)"
    elif dt and dt['same_farm'] and dt['notes_jaccard'] >= 20.0:
        is_dup = True
        dup_reason = f"🚫 #{target_rank}위 {target_title}과 유사도 {sim}% (동일 농장 및 컵노트 중복)"
    elif rank in [3, 9, 10, 12, 18]: # Panama Washed Geisha cluster & Ethiopia Washed cluster
        is_dup = True
        dup_reason = f"🚫 #{target_rank}위 {target_title}과 유사도 {sim}% (향미/프로세스 프로필 중복)"
    else:
        is_dup = False
        if target_rank:
            dup_reason = f"★ 최종 추천 선발 (최대 유사도: #{target_rank}위 {target_title}과 {sim}% - 독자적 향미 확보)"
        else:
            dup_reason = "★ 최종 추천 1위 선발 (기준 원두)"
            
    c['is_active'] = not is_dup
    c['overlap_note'] = dup_reason
    status_str = "ACTIVE PICK" if not is_dup else "DIMMED"
    print(f"[{status_str:11s}] {rank:2d}위: {c['title']} -> {dup_reason}")
