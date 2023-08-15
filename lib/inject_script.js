/**
 * JavaScript 模板文件
 */

const MAIN_SELECT_OPTIONS = ['母婴', '美食', '时尚', '美妆', '家居', '穿搭', '好物', '宠物']
const TAG_OPTIONS = ['好物', '测评', '探店', "旅行", '护肤', '萌娃', '萌宠', '穿搭']


const container = document.createElement('div')
container.id = 'forecast-result-container'

// 生成一级标签下拉选项
const selectLabel = document.createElement('label')
selectLabel.innerText = '一级: '

const select = document.createElement('select')
select.id = 'user-tag-select'
select.className = 'short-select'

const checkboxContainer = document.createElement('ul')
checkboxContainer.className = 'dowebok'

const inputLabel = document.createElement('label')
inputLabel.innerText = '职业: '

const input = document.createElement('input')
input.id = 'user-profession'

const submit = document.createElement("button")
submit.innerText = '提交'
submit.className = 'btn twinkle'

for (let i = 0; i < MAIN_SELECT_OPTIONS.length; i++) {
    const option = document.createElement("option")
    option.value = MAIN_SELECT_OPTIONS[i]
    option.textContent = MAIN_SELECT_OPTIONS[i]
    select.appendChild(option)
}

container.appendChild(selectLabel)
container.appendChild(select)

/**
 * 主类型
 * Python 类型: str
 * 示例: '母婴' --> '#select_value_default#' --> '母婴'
 * 示例: '' --> '#select_value_default#' --> '好物'
 * #select_value_default# 被替换的字符串
 * @type {string}
 */
select.value = '#select_value_default#' || '好物'
/**
 * 标签
 * Python 类型: List[str]
 * 示例: ['好物', '测评'] --> `#checkbox_options_default#` --> ['好物', '测评']
 * @type {Array[String]}
 */
const checkboxOptionsDefault = [`#checkbox_options_default#`]
/**
 * 主类型
 * Python 类型: str
 * 示例: '营养师' --> '#user-profession-default#' --> '营养师'
 * #select_value_default# 被替换的字符串
 * @type {string}
 */
input.value = '#user-profession-default#'

// 生成二级标签多选选项
for (let i = 0; i < TAG_OPTIONS.length; i++) {
    const li = document.createElement('li')
    const checkbox = document.createElement("input")
    checkbox.type = "checkbox"
    checkbox.name = "user-tag-checkbox"
    checkbox.setAttribute('data-labelauty', TAG_OPTIONS[i])
    if (checkboxOptionsDefault.indexOf(TAG_OPTIONS[i]) !== -1) {
        checkbox.setAttribute('checked', 'checked')
    }
    checkbox.value = TAG_OPTIONS[i]

    li.appendChild(checkbox)
    checkboxContainer.appendChild(li)
}

container.appendChild(checkboxContainer)
container.appendChild(inputLabel)
container.appendChild(input)

// 处理提交按钮点击事件
submit.addEventListener("click", function () {
    // 获取用户选择的一级标签值
    let selectedLevel1 = select.value
    let profession = input.value
    let selectedLevel2 = []
    let checkboxes = document.querySelectorAll('input[name="user-tag-checkbox"]:checked')
    for (let i = 0; i < checkboxes.length; i++) {
        selectedLevel2.push(checkboxes[i].value)
    }
    let div = document.getElementById('user-tag-data') || document.createElement('div')
    div.id = 'user-tag-data'
    div.innerText = JSON.stringify({
        '一级': selectedLevel1,
        '二级': selectedLevel2,
        '职业': profession
    })
    document.body.appendChild(div)
});
container.appendChild(submit)

document.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault(); // 阻止默认的 Enter 行为（比如换行）
        submit.click(); // 触发按钮点击事件
    }
});

document.body.appendChild(container)

$(function () {
    // noinspection JSUnresolvedReference
    $(':input').labelauty();
});