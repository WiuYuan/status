import json


def load_flow(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_state(answers, states):
    """检查当前回答是否满足某个状态（支持多选条件）"""
    for state_name, state_info in states.items():
        for condition in state_info["conditions"]:
            # 对每个条件逐个检查是否匹配
            ok = True
            for q, expected in condition.items():
                if q not in answers:
                    ok = False
                    break
                # 如果 expected 是列表 -> 当前答案必须在里面
                if isinstance(expected, list):
                    if answers[q] not in expected:
                        ok = False
                        break
                else:
                    if answers[q] != expected:
                        ok = False
                        break
            if ok:
                return state_name, state_info["description"]
    return None, None


def check_requirements(question_id, question_info, answers):
    """判断一个问题是否需要被触发"""
    requires = question_info.get("requires")
    if not requires:
        return True
    for pre_q, valid_answers in requires.items():
        if pre_q not in answers:
            return False
        if answers[pre_q] not in valid_answers:
            return False
    return True


def run_status_test(flow_file):
    flow = load_flow(flow_file)
    answers = {}
    questions = flow["questions"]
    states = flow["states"]

    for q_id, q_info in questions.items():
        # 检查是否应触发
        if not check_requirements(q_id, q_info, answers):
            continue

        # 提问
        print(f"\n{q_info['text']}")
        for i, opt in enumerate(q_info["options"], 1):
            print(f"{i}. {opt}")

        # 用户输入
        while True:
            choice = input("请输入选项编号：")
            try:
                choice = int(choice)
                selected = q_info["options"][choice - 1]
                break
            except Exception:
                print("无效输入，请输入有效数字。")

        answers[q_id] = selected

        # 检查状态
        state_name, desc = check_state(answers, states)
        if state_name:
            print(f"\n✅ 当前状态判定为：{state_name} ({desc})")
            return

    print("\n❌ 没有匹配任何状态。最终回答如下：")
    print(json.dumps(answers, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run_status_test("flow.json")
