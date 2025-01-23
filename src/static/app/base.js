function postMethodErrorHandler(response){
    if(response.error.extra !== undefined){
        if (response.error.extra.fields !== undefined) {
            Object.keys(response.error.extra.fields).forEach(k => {
                if (response.error.extra.fields[k] instanceof Array) {
                    response.error.extra.fields[k].forEach(msg => {
                        toastr.error(`${k} : ${msg}`)
                    })
                }
            })
        }
    } else {
        if (typeof (response.error) === "object") {
            Object.keys(response.error).forEach(k => {
                toastr.error(response.error[k])
            })
        } else {
            toastr.error(response.error)
        }
    }
}
async function post_method(url, body) {
    try {
        const response = await fetch(url, {
            method: 'POST', headers: {
                'X-CSRFToken': getCookie("csrftoken"), 'Accept': 'application/json', 'Content-Type': 'application/json'
            }, body: body,
        });
        if (!response.ok) {
            try {
                const data = await response.json()
                return {error: data}
            } catch {
                throw new Error(`something went wrong with Getting Data!!!   ${response.status} : ${response.statusText}`);
            }
        }
        try{
            return await response.json()
        }catch{
            return response
        }
    } catch (error) {
        return {error: error.message}
    }
}

function close_modal(modal_id) {
    let modal = document.getElementById(modal_id);
    modal.classList.add('hidden');
}
function open_modal(modal_id) {
    let modal = document.getElementById(modal_id);
    modal.classList.remove('hidden');
}
document.addEventListener('keydown', function (event) {
    if (event.key === "Escape") {
        const modal = document.getElementById('event-details-modal');
        modal.classList.add('hidden');
    }
});  

async function new_fetch_helper(baseUrl, queryParams=null) {
    try {
        let searchUrl = new URL(baseUrl);
        if(queryParams !== null){
            queryParams.forEach(param=>{
                searchUrl.searchParams.append(param[0], param[1]);
            })
        }
        let response = await fetch(searchUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
        });
        if (!response.ok) {
            try {
                const data = await response.json()
                return {error: JSON.stringify(data)}
            } catch {
                return {error: `something went wrong with Getting Data!!!   ${response.status} : ${response.statusText}`}
            }
        }
        try {
            return await response.json()
        } catch {
            return {error: `Data cannot convert to json!   ${response.status} : ${response.statusText}`, status:response.status}
        }
    } catch (error) {
        return {error: error.message}
    }
}

function get_Gregorian(value){
    // value="1403/02/20-16:22:00"
    let js_date=value.split('-')[0].split('/')
    let js_time = value.split('-')[1].split(':')
    let g_date = jalaali.toGregorian(parseInt(js_date[0]),parseInt( js_date[1]),parseInt( js_date[2]))

    // let d = new Date(g_date.gy,g_date.gm,g_date.gd, parseInt(js_time[0]),parseInt(js_time[1]),parseInt(js_time[2]))
    let year = g_date.gy.toString().padStart(4, '0')
    let mon = g_date.gm.toString().padStart(2, '0')
    let day = g_date.gd.toString().padStart(2, '0')

    return `${year}/${mon}/${day} ${js_time[0]}:${js_time[1]}:${js_time[2]}`
}


function confirmActionMessageBox(parent, message, confirm_function, after_job_function=null) {
    let fadeBack = document.createElement('div')
   fadeBack.className="w-full h-full fixed top-0 left-0 bg-black/50"
   fadeBack.style.zIndex=52

   let deleteConfirmDiv = document.createElement('div')
   deleteConfirmDiv.classList.add('fixed', 'top-24', 'left-0', 'right-0', 'mx-auto', 'py-8','px-10', 'rounded-lg', 'bg-white', 'dark:bg-zinc-800', 'border-2', 'border-white', 'font-Sahel', 'w-fit', 'shadow-lg')
   deleteConfirmDiv.style.zIndex=53

   let deleteConfirm_p = document.createElement('p')
   deleteConfirm_p.classList.add('mb-3')
   let confirmActionBtn = document.createElement('button')
   confirmActionBtn.classList.add('bg-green-400','px-2', 'py-1', 'dark:text-white')

   let cancelActionBtn = document.createElement('button')
   cancelActionBtn.classList.add('bg-orange-400','px-2', 'py-1', 'dark:text-white', 'mr-3')

   deleteConfirm_p.innerText = message

   confirmActionBtn.innerText = "انجام شود"
   cancelActionBtn.innerText = "لغو عملیات"
   deleteConfirmDiv.appendChild(deleteConfirm_p)
   deleteConfirmDiv.appendChild(confirmActionBtn)
   deleteConfirmDiv.appendChild(cancelActionBtn)
   cancelActionBtn.addEventListener('click', e => {
       deleteConfirmDiv.remove()
       fadeBack.remove()
   })
   confirmActionBtn.addEventListener('click', e => {
       confirm_function()
       deleteConfirmDiv.remove()
       fadeBack.remove()
       if(after_job_function){
           setTimeout(after_job_function, 1000)
       }
   })

    parent.appendChild(deleteConfirmDiv)
    parent.appendChild(fadeBack)
}

let popup = Notification({
    position: 'center',
    duration: 150000,
    isHidePrev: false,
    isHideTitle: false,
    maxOpened: 8,
  });