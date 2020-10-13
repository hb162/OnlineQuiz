const qtnList = document.getElementById("form_question");
const addQtnBtn = document.getElementById("add_question");
const delQtnBtn = document.querySelector(".remove_question");
const qtnEditList = document.getElementById("modal-default");

qtnEditList.addEventListener("click", (event) => {
    const target = event.target;
    const targetClass = target.className;
    if (targetClass === null) return;

    if (targetClass === "qs-remove-answer-edit") {
        deleteAnswerEdit(target);
    }
    if (targetClass === "qs-add-answer-edit") {
        addAnswerEdit(target);
    }
})

const addAnswerEdit = (target) => {
    const currentQtn = target.parentNode.parentNode.parentNode;
    const ansList = currentQtn.querySelector(".qs-list-edit");
    if (ansList.childElementCount < 26) {
        let ansId = "A";
        if (ansList.lastElementChild !== null) {
            ansId = nextChar(ansList.lastElementChild.id); //Khi vượt quá "z", hàm này sẽ trả về "{", "}"...
        }
        const ansForm = document.createElement("div");
        ansForm.setAttribute("id", `${ansId}`)
        ansForm.setAttribute("class", "qs-ans");
        const ansFormContent =`<label class="qs-label-edit qs-label-ans" for="${ansId}">${ansId}</label>
                            <input type="checkbox" class="qs-checkbox-correct-edit">
                            <input type="text" id="${ansId}" class="qs-choices-edit form-control">       
                        <a href="javascript:void(0);" class="qs-remove-answer-edit">
                            <i class="fas fa-minus inline faw"></i></a>`;
        ansForm.innerHTML = ansFormContent;
        ansList.appendChild(ansForm);
    }
}

const deleteAnswerEdit = (target) => {
    const currentAns = target.parentNode;
    const ansList = currentAns.parentNode;
    console.log(ansList.lastChild);
    let lastAns = ansList.lastElementChild;

    while (lastAns !== currentAns) {
        const prevAns = lastAns.previousElementSibling;
        lastAns.setAttribute("id", `${prevAns.id}`);
        lastAns.querySelector(".qs-label-ans").textContent = `${prevAns.id}`;
        lastAns = prevAns;
    }
    ansList.removeChild(currentAns);
}

addQtnBtn.addEventListener("click", () => {

    let qtnId = 0;

    if (qtnList.lastElementChild !== null) {
        qtnId = parseInt(qtnList.lastElementChild.id) + 1;
    }

    const qtnForm = document.createElement("div");
    qtnForm.setAttribute("class", "qtn-form");
    qtnForm.setAttribute("id", `${qtnId}`)
    const qtnFormContent = `
                        <div class="row">
                        <div class="col-xl-1 qs_label">
                                <label for="question_title" class="incr"><i class="fa fa-circle" style="font-size: 10px"></i></label>
                            </div>
                            <div class="col-xl-10 qs">
                                <input type="text" id="question_title" name="question_title"
                                       placeholder="Have a multiple-choice question to ask?"
                                       class="question_title form-control inline">
                                <a href="javascript:void(0);" class="remove_question"><i class="fa fa-trash inline faw"
                                                                                         aria-hidden="true"></i></a>
                                <br>
                                <div class="question_wrapper" id="all_answer"></div>
                                <button class="add_selector" type="button">&#43;Add Answer</button>
                                <div class="explain">
                                    <div class="label_explain"><i class="fas fa-exclamation"></i></div>
                                    <input type="text" class="question_explain" id="exp"
                                           placeholder="An explaination, if you like">
                                </div>
                            </div>
                        </div>
        `;
    qtnForm.innerHTML = qtnFormContent;
    qtnList.appendChild(qtnForm);

})
qtnList.addEventListener("click", (event) => {
    const target = event.target;
    const targetClass = target.className;
    if (targetClass === null) return;

    if (targetClass === "remove_question") {
        deleteQuestion(target);
    }
    if (targetClass === "add_selector") {
        addAnswer(target);
    }
    if (targetClass === "remove_button") {
        deleteAnswer(target);
    }
})

const deleteQuestion = (target) => {
    const currentQtn = target.parentNode.parentNode.parentNode;
    let lastQtn = qtnList.lastChild;

    while (lastQtn !== currentQtn) {
        const prevQtn = lastQtn.previousSibling;
        lastQtn.setAttribute("id", `${prevQtn.id}`);
        lastQtn.querySelector(".incr").innerHTML = `<i class="fa fa-circle" style="font-size: 10px"></i>`;
        lastQtn = prevQtn;
    }
    qtnList.removeChild(currentQtn);
}

const addAnswer = (target) => {
    const currentQtn = target.parentNode.parentNode;
    const ansList = currentQtn.querySelector(".question_wrapper");
    if (ansList.childElementCount < 26) {
        let ansId = "A";
        if (ansList.lastChild !== null) {
            ansId = nextChar(ansList.lastChild.id); //Khi vượt quá "z", hàm này sẽ trả về "{", "}"...
        }
        const ansForm = document.createElement("div");
        ansForm.setAttribute("class", "test");
        ansForm.setAttribute("id", `${ansId}`)
        const ansFormContent = `
            <label for="slt" class="incr2">${ansId}</label><input type="checkbox" class="qs_correct inline"><input type="text" id="slt" name="question" placeholder="Answer..." class="question_selector inline sel_data"><a href="javascript:void(0);" class="remove_button">
                        <i class="fas fa-minus inline faw"></i></a>
        `;
        ansForm.innerHTML = ansFormContent;
        ansList.appendChild(ansForm);
    }
}

const deleteAnswer = (target) => {
    const currentAns = target.parentNode;
    const ansList = currentAns.parentNode;
    let lastAns = ansList.lastChild;
    while (lastAns !== currentAns) {
        const prevAns = lastAns.previousSibling;
        console.log(prevAns)
        lastAns.setAttribute("id", `${prevAns.id}`);
        lastAns.querySelector(".incr2").textContent = `${prevAns.id}`;
        lastAns = prevAns;
    }
    ansList.removeChild(currentAns);
}


const nextChar = (c) => {
    return String.fromCharCode(c.charCodeAt(0) + 1).toUpperCase();
}