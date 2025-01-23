
let overview_url = window.location.origin + document.getElementById('overview_url').dataset.url
let search_users_url = window.location.origin + document.getElementById('search_users_url').dataset.url
let get_alarms_url = window.location.origin + document.getElementById('get_alarms_url').dataset.url
let get_event_detials_url = window.location.origin + document.getElementById('get_event_detials_url').dataset.url
let alarm_change_status_url = window.location.origin + document.getElementById('alarm_change_status_url').dataset.url

let param = document.getElementById("search_user_input").value
let queryparam = [["search", param],] 
jalaliDatepicker.startWatch();


function load_overview(){

    new_fetch_helper(overview_url).then(res => {
        if ('error' in res && res.status != 200) {
            loading_section.classList.add('hidden')
            console.log(res)
            toastr.error(res.error)
        } else {
            document.getElementById("un-handled-alarms").textContent=res.un_handled
            document.getElementById("all-alarms").textContent=res.all

            document.getElementById("all_sms").textContent = res.all_emails
            document.getElementById("all_emails").textContent = res.all_sms
            loading_section.classList.add('hidden')

        }
    })
}


function generate_alarm_table_records(alarm){
    let alarmUserElement =``
    if(alarm.device.user){
        let alarmUser = alarm.device.user.name || alarm.device.user.phone;
        alarmUserElement = `<p>${alarmUser}</p>`;
    }
    let alarmSms = alarm.is_sms_sent
    ? `<p class="table-green-badge">ارسال شد</p>`
    : `<p class="table-red-badge">ارسال نشد</p>`;

    let alarmEmail = alarm.is_email_sent
    ? `<p class="table-green-badge">ارسال شد</p>`
    : `<p class="table-red-badge">ارسال نشد</p>`;

    let alarmHandled = alarm.handled
    ? `<p class="table-green-badge">رسیدگی شد</p>`
    : `<p class="table-red-badge">رسیدگی نشد</p>`;


    let trElement= 
    `
        <tr class="hover:bg-gray-200 dark:hover:bg-meta-4">
            <td class="table-td">${alarm.alarm_type}</td>
            <td class="table-td">${alarmUserElement}</td>
            <td class="table-td">${alarm.device.title} - ${alarm.device_name}</td>
            <td class="table-td"><p  style="direction: ltr;">${alarm.jTime}</p></td>
            <td class="table-td">${alarmSms}</td>
            <td class="table-td">${alarmEmail}</td>
            <td class="table-td">${alarmHandled}</td>

           
            <td class="table-td">
                <div class="flex items-center gap-x-2 justify-center">
                    <button data-pk=${alarm.pk} class="alarmdetail-btn hover:text-primary">
                        <svg class="fill-current" width="18" height="18" viewBox="0 0 18 18"
                            fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M8.99981 14.8219C3.43106 14.8219 0.674805 9.50624 0.562305 9.28124C0.47793 9.11249 0.47793 8.88749 0.562305 8.71874C0.674805 8.49374 3.43106 3.20624 8.99981 3.20624C14.5686 3.20624 17.3248 8.49374 17.4373 8.71874C17.5217 8.88749 17.5217 9.11249 17.4373 9.28124C17.3248 9.50624 14.5686 14.8219 8.99981 14.8219ZM1.85605 8.99999C2.4748 10.0406 4.89356 13.5562 8.99981 13.5562C13.1061 13.5562 15.5248 10.0406 16.1436 8.99999C15.5248 7.95936 13.1061 4.44374 8.99981 4.44374C4.89356 4.44374 2.4748 7.95936 1.85605 8.99999Z"
                                fill="" />
                            <path
                                d="M9 11.3906C7.67812 11.3906 6.60938 10.3219 6.60938 9C6.60938 7.67813 7.67812 6.60938 9 6.60938C10.3219 6.60938 11.3906 7.67813 11.3906 9C11.3906 10.3219 10.3219 11.3906 9 11.3906ZM9 7.875C8.38125 7.875 7.875 8.38125 7.875 9C7.875 9.61875 8.38125 10.125 9 10.125C9.61875 10.125 10.125 9.61875 10.125 9C10.125 8.38125 9.61875 7.875 9 7.875Z"
                                fill="" />
                        </svg>
                    </button>
                </div>
            </td>
        </tr>

    `
    return trElement
}

let selected_alarm = null
let need_to_reload_alarms = false
function show_alarm_details(alarm_id,openModal=true){
    if(alarm_id==null) return
    selected_alarm = alarm_id
    loading_section.classList.remove('hidden')
    new_fetch_helper(get_event_detials_url.replace("999", alarm_id)).then(res => {
        if ('error' in res) {
            loading_section.classList.add('hidden')
            console.log(res)
            toastr.error(res.error)
        } else {
            document.getElementById("alarm_details-id").textContent=res.id
            document.getElementById("alarm_details-device").textContent=res.device.title
            document.getElementById("alarm_details-devicename").textContent=res.device_name
            document.getElementById("alarm_details-type").textContent=res.alarm_type
            document.getElementById("alarm_details-channel").textContent=res.channel
            document.getElementById("alarm_details-alarmName").textContent=res.alarm_name
            document.getElementById("alarm_details-time").textContent=res.jTime
            document.getElementById("alarm_details-ip").textContent=res.ip
            document.getElementById("alarm_details-fileName").textContent=res.original_file_name
            document.getElementById("alarm_details-alarm_address").textContent=res.device.address


            

            document.getElementById("alarm_details-image").src = res.file.file
            if(res.file.file == null){
                document.getElementById("alarm_details-image").classList.add("hidden")
                document.getElementById("alarm_details-image").src =""
            }else{
                document.getElementById("alarm_details-image").classList.remove("hidden")

            }


            let alarmSms = res.is_sms_sent
            ? `<span class="px-2 py-1 text-sm rounded bg-green-100 text-green-800">پیامک ارسال شد</span>`
            : `<span class="px-2 py-1 text-sm rounded bg-red-100 text-red-800">پیامک ارسال نشد</span>`;

            let alarmEmail = res.is_email_sent
            ? `<span class="px-2 py-1 text-sm rounded bg-green-100 text-green-800">ایمیل ارسال شد</span>`
            : `<span class="px-2 py-1 text-sm rounded bg-red-100 text-red-800">ایمیل ارسال نشد</span>`;

            let alarmHandled = res.handled
            ? `<span class="px-2 py-1 text-sm rounded bg-green-100 text-green-800">رسیدگی شد</span>`
            : `<span class="px-2 py-1 text-sm rounded bg-red-100 text-red-800">رسیدگی نشده</span>`;

            document.getElementById("alarm_details-flags").innerHTML=
            `
            ${alarmSms}
            ${alarmEmail}
            ${alarmHandled}
            `
            if(res.device.user){
                document.getElementById("alarm_details-user").textContent=res.device.user.name
                document.getElementById("alarm_details-phone").textContent=res.device.user.phone
                document.getElementById("alarm_details-address").textContent=res.device.user.address
            }else{
                document.getElementById("alarm_details-user").textContent='-'
                document.getElementById("alarm_details-phone").textContent='-'
                document.getElementById("alarm_details-address").textContent='-'
            }
            
            
            if(openModal){
                open_modal('event-details-modal')
            }

            loading_section.classList.add('hidden')
        }
    })
}

function change_alarm_status(){
    if(selected_alarm == null){
        toastr.warning("رویدادی انتخاب نشده است.")
        return
    }
    need_to_reload_alarms=true
    new_fetch_helper(alarm_change_status_url.replace("999", selected_alarm)).then(res => {
        if ('error' in res && res.status != 200) {
            loading_section.classList.add('hidden')
            console.log(res)
            toastr.error(res.error)
        } else {
            show_alarm_details(selected_alarm, false)
            toastr.success("وضعیت رویداد تغییر کرد.")
        }
    })
}
document.getElementById("event-details-modal-close-btn").addEventListener("click",(e)=>{
    if(need_to_reload_alarms){
        get_alarms()
        load_overview()
        need_to_reload_alarms=false
    }
})

document.getElementById("alarm_details-changeStatus").addEventListener("click", ()=>{
    change_alarm_status()
})

let alarmRecords = {}; // To store current state of alarms by their unique pk

function updateAlarmTable(alarm) {
    const alarmPk = alarm.pk;
    let rowElement;

    // Create or update row
    if (alarmRecords[alarmPk]) {
        // Update existing record
        rowElement = document.getElementById(`alarm-row-${alarmPk}`);
        if (rowElement) {
            updateRow(rowElement, alarm);
        }
    } else {
        // Create new record
        rowElement = createRow(alarm);
        if(firstTimeLoaded){
            new_alarm_popup(alarm)
        }
        
        document.querySelector("#alarms-table-body").prepend(rowElement);
        alarmRecords[alarmPk] = alarm; // Store the alarm in the records
    }
}

function createRow(alarm) {
    const trElement = document.createElement('tr');
    trElement.id = `alarm-row-${alarm.pk}`;
    trElement.className = "hover:bg-gray-200 dark:hover:bg-meta-4";
    trElement.innerHTML = generateRowHTML(alarm);
    return trElement;
}

function updateRow(rowElement, alarm) {
    rowElement.innerHTML = generateRowHTML(alarm);
}

function generateRowHTML(alarm) {
    const alarmUser = alarm.device.user ? (alarm.device.user.name || alarm.device.user.phone) : '';
    const alarmSms = alarm.is_sms_sent ? `<p class="table-green-badge">ارسال شد</p>` : `<p class="table-red-badge">ارسال نشد</p>`;
    const alarmEmail = alarm.is_email_sent ? `<p class="table-green-badge">ارسال شد</p>` : `<p class="table-red-badge">ارسال نشد</p>`;
    const alarmHandled = alarm.handled ? `<p class="table-green-badge">رسیدگی شد</p>` : `<p class="table-red-badge">رسیدگی نشد</p>`;

    return `
        <td class="table-td">${alarm.alarm_type}</td>
        <td class="table-td"><p>${alarmUser}</p></td>
        <td class="table-td">${alarm.device.title} - ${alarm.device_name}</td>
        <td class="table-td"><p style="direction: ltr;">${alarm.jTime}</p></td>
        <td class="table-td">${alarmSms}</td>
        <td class="table-td">${alarmEmail}</td>
        <td class="table-td">${alarmHandled}</td>
        <td class="table-td">
            <div class="flex items-center gap-x-2 justify-center">
                <button data-pk=${alarm.pk} onclick=show_details_of_alarm(${alarm.pk}) class="alarmdetail-btn hover:text-primary">
                    <i class="fa fa-eye"></i>
                </button>
            </div>
        </td>
    `;
}
function show_details_of_alarm(pk){
    show_alarm_details(pk)
}

document.getElementById("alarms-table-body").innerHTML=``
let firstTimeLoaded = false
function get_alarms(with_loader=true){
    if(with_loader){ loading_section.classList.remove('hidden')}

    new_fetch_helper(get_alarms_url).then(res => {
        if ('error' in res) {
            loading_section.classList.add('hidden')
            console.log(res)
            toastr.error(res.error)
        } else {
            res.forEach(alarm=>{
                updateAlarmTable(alarm)
            })
            loading_section.classList.add('hidden')
        }
        firstTimeLoaded=true
    })
}

load_overview()
get_alarms()

setInterval(() => {
    get_alarms(false)
    load_overview()
}, 10000);


function new_alarm_popup(alarm){
    console.log(alarm)
    let msgHtml =  `
        <p>نوع:<strong>${alarm.alarm_type}</strong></p>
        <p>دستگاه:<strong>${alarm.device.title}</strong></p>
    `
    if(alarm.device.user != null){
        msgHtml += `
            <p>کاربر:<strong>${alarm.device.user.name}</strong></p>
            <p>شماره تماس:<strong>${alarm.device.user.phone}</strong></p>
            <p>آدرس:<strong>${alarm.device.user.address}</strong></p>

        `
    }
    popup.dialog({
        title: '<div class="title-cust title-dialogfull">دریافت هشدار جدید</div>',
        message: msgHtml,
        callback:(result) => {
          console.log('result = ', result)
        },
      });
}
// popup.dialog({
//     title: '<div class="title-cust title-dialogfull">دریافت هشدار جدید</div>',
//     message: `
//     <p>دستگاه:<strong></strong></p>
//     `,
//     callback:(result) => {
//       console.log('result = ', result)
//     },
//   });

