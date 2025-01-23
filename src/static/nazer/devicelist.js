let search_users_url = window.location.origin + document.getElementById('search_users_url').dataset.url
let set_owner_url = window.location.origin + document.getElementById('set_owner_url').dataset.url
let clear_owner_url = window.location.origin + document.getElementById('clear_owner_url').dataset.url



let selected_owner = null
let selected_device = null

function findUser(param){
    let queryparam = [["search", param],] 
    selected_owner = null
    loading_section.classList.remove('hidden')
    new_fetch_helper(search_users_url,queryparam).then(res => {
        if ('error' in res) {
            loading_section.classList.add('hidden')
            console.log(res)
            toastr.error(res.error)
        } else {
            let tbody = document.getElementById("set_owner_modal_table_body")
            tbody.innerHTML=``
            res.forEach(item=>{
            
                let tr = document.createElement("tr")
                tr.classList.add("table-body-tr")
                let tdUsername = document.createElement("td")
                tdUsername.classList.add("table-body-td")
                let tdName = document.createElement("td")
                tdName.classList.add("table-body-td")

                let tdPhone = document.createElement("td")
                tdPhone.classList.add("table-body-td")
                let tdEmail = document.createElement("td")
                tdEmail.classList.add("table-body-td")

                tdUsername.textContent=item.username
                tdName.textContent=`${item.first_name} ${item.last_name}`
            
                let tdSelect = document.createElement("td")
                tdSelect.classList.add("table-body-td", "flex", "items-center")
                let selectBtn = document.createElement("button")
                selectBtn.dataset.pk=item.pk
                selectBtn.classList.add("btn-success", "py-1", "fa", "fa-check-square-o")
                selectBtn.addEventListener("click", e=>{
                    selected_owner = null
                    tbody.querySelectorAll("tr").forEach(trs=>{
                        trs.classList.remove("bg-green-400", "dark:bg-green-400")
                    })
                    e.target.parentElement.parentElement.classList.add("bg-green-400", "dark:bg-green-400")
                    selected_owner = e.target.dataset.pk
                })
                tdSelect.appendChild(selectBtn)

                tr.appendChild(tdUsername)
                tr.appendChild(tdName)

                tdPhone.textContent=item.phone
                tr.appendChild(tdPhone)

                tdEmail.textContent=item.email
                tr.appendChild(tdEmail)

                tr.appendChild(tdSelect)
                tbody.appendChild(tr)
            })
            loading_section.classList.add('hidden')
        }
    })
}


document.querySelectorAll(".add-owner-btn").forEach(btn=>{
    btn.addEventListener("click", e=>{
        selected_owner = null
        selected_device=btn.dataset.device
        open_modal('user_search_modal')
    })
})


document.getElementById("user_search_modal_apply").addEventListener("click", ()=>{
    if(selected_owner === null || selected_device === null){
        toastr.warning("ابتدا از انتخاب یک کاربر و یک دستگاه اطمینان حاصل کنید.")
        return
    }
    let jsonConf = {
        device:selected_device,
        user:selected_owner,
    }
    let body=JSON.stringify(jsonConf)
    loading_section.classList.remove('hidden')
    post_method(set_owner_url, body).then(response => {
        loading_section.classList.add('hidden')
        if (response.error) {
            postMethodErrorHandler(response)
        } else {

            document.getElementById("all-device-table-body").querySelectorAll(`tr[data-device="${selected_device}"]`).forEach(tr=>{
                tr.classList.remove("bg-orange-500", "dark:bg-orange-500")
                tr.querySelectorAll(".add-owner-btn").forEach(btn=>{btn.classList.add("hidden")})
                tr.querySelectorAll(".remove-owner-btn").forEach(btn=>{btn.classList.remove("hidden")})
            })


            document.getElementById("all-device-table-body").querySelectorAll(`tr[data-device="${selected_device}"]`).forEach(tr=>{
                tr.querySelectorAll('[name="owner-td"]').forEach(td_username=>{
                    td_username.textContent=response.username
                })
            })

            document.getElementById("all-device-table-body").querySelectorAll(`tr[data-device="${selected_device}"]`).forEach(tr=>{
                tr.querySelectorAll('[name="name"]').forEach(td_name=>{
                    td_name.textContent=response.name
                })
            })
            close_modal('user_search_modal')
        }
    })
})

let set_owner_user_search_debounce;
let search_user_input = document.getElementById("search_user_input")
search_user_input.addEventListener("keyup", e=>{
    e.preventDefault()
    clearTimeout(set_owner_user_search_debounce)
    if (search_user_input.value.length > 1) {
        set_owner_user_search_debounce = setTimeout(() => {
            findUser(search_user_input.value)
        }, 1000)
    } else {
        document.getElementById("set_owner_modal_table_body").innerHTML=``
    }

})

document.querySelectorAll(".remove-owner-btn").forEach(btn=>{
    btn.addEventListener("click", e=>{
        confirmActionMessageBox(
            document.body,
            "مالک دستگاه حذف شود؟",
            ()=>{
                let jsonConf = {
                    device:e.target.dataset.device,
                }
                let body=JSON.stringify(jsonConf)
                loading_section.classList.remove('hidden')
                post_method(clear_owner_url, body).then(response => {
                    loading_section.classList.add('hidden')
                    if (response.error) {
                       
                        postMethodErrorHandler(response)
                        
                    } else {
                        e.target.parentElement.parentElement.parentElement.classList.add("bg-orange-500", "dark:bg-orange-500")
                        e.target.classList.add("hidden")
                        e.target.parentElement.querySelectorAll(".add-owner-btn").forEach(addOwnerBtn=>{addOwnerBtn.classList.remove("hidden")})

                        e.target.parentElement.parentElement.parentElement.querySelectorAll('[name="owner-td"]').forEach(td_username=>{
                            td_username.textContent='فاقد مالک'
                        })
                    }
                })
            }
        )
    })
})
