import json
from js import document, console

# 用于存储当前答案
answers = {}


def load_flow(flow_str):
    return json.loads(flow_str)


def check_state(answers, states):
    """检查当前回答是否满足某个状态（支持多选条件）"""
    for state_name, state_info in states.items():
        for condition in state_info["conditions"]:
            ok = True
            for q, expected in condition.items():
                if q not in answers:
                    ok = False
                    break
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


# 当前问题索引
current_q_index = 0
question_order = []


def run_status_test(flow_str):
    global question_order, current_q_index, answers
    flow = load_flow(flow_str)
    answers = {}
    questions = flow["questions"]
    states = flow["states"]

    # 顺序存储问题 id
    question_order = list(questions.keys())
    current_q_index = 0

    # 清空网页输出
    container = document.getElementById("question-container")
    container.innerHTML = ""

    # 显示第一个问题
    show_next_question(flow)


def show_next_question(flow):
    global current_q_index, answers
    questions = flow["questions"]
    states = flow["states"]

    # 找到下一个需要触发的问题
    while current_q_index < len(question_order):
        q_id = question_order[current_q_index]
        q_info = questions[q_id]
        if check_requirements(q_id, q_info, answers):
            break
        current_q_index += 1
    else:
        # 没有更多问题，显示最终状态
        state_name, desc = check_state(answers, states)
        output_container = document.getElementById("question-container")
        if state_name:
            output_container.innerHTML = (
                f"<h2>✅ 当前状态：{state_name}</h2><p>{desc}</p>"
            )
        else:
            output_container.innerHTML = "<h2>❌ 没有匹配任何状态</h2>"
        return

    # 显示问题和选项按钮
    q_id = question_order[current_q_index]
    q_info = questions[q_id]

    container = document.getElementById("question-container")
    container.innerHTML = f"<h3>{q_info['text']}</h3>"

    for opt in q_info["options"]:
        btn = document.createElement("button")
        btn.innerText = opt

        def make_handler(answer):
            def handler(ev):
                answers[q_id] = answer
                global current_q_index
                current_q_index += 1
                show_next_question(flow)

            return handler

        btn.addEventListener("click", make_handler(opt))
        container.appendChild(btn)
