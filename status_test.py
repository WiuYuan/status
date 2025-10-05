import json
from js import document, window

answers = {}
current_q_index = 0
question_order = []


def load_flow(flow_str):
    return json.loads(flow_str)


def check_state(answers, states):
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
    requires = question_info.get("requires")
    if not requires:
        return True
    for pre_q, valid_answers in requires.items():
        if pre_q not in answers:
            return False
        if answers[pre_q] not in valid_answers:
            return False
    return True


def run_status_test(flow_str):
    global question_order, current_q_index, answers
    flow = load_flow(flow_str)
    answers = {}
    questions = flow["questions"]
    states = flow["states"]
    question_order = list(questions.keys())
    current_q_index = 0

    container = document.getElementById("question-container")
    container.innerHTML = ""
    show_next_question(flow)


def show_next_question(flow):
    global current_q_index, answers
    questions = flow["questions"]
    states = flow["states"]

    # 找到下一个需要显示的问题
    while current_q_index < len(question_order):
        q_id = question_order[current_q_index]
        q_info = questions[q_id]
        if check_requirements(q_id, q_info, answers):
            break
        current_q_index += 1
    else:
        # 结束
        state_name, desc = check_state(answers, states)
        container = document.getElementById("question-container")
        if state_name:
            container.innerHTML = f"<h2>✅ 当前状态：{state_name}</h2><p>{desc}</p>"
        else:
            container.innerHTML = "<h2>❌ 没有匹配任何状态</h2>"
        return

    # 显示当前问题
    q_id = question_order[current_q_index]
    q_info = questions[q_id]
    container = document.getElementById("question-container")
    container.innerHTML = f"<h3>{q_info['text']}</h3>"

    # 使用 JavaScript 函数创建按钮，确保事件处理器工作
    for opt in q_info["options"]:
        window.createButtonWithHandler(container, opt, q_id, opt, flow)


# 使函数在全局可用
from pyodide import create_proxy
