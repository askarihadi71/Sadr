let get_event_detials_url = window.location.origin + document.getElementById('get_event_detials_url').dataset.url
jalaliDatepicker.startWatch();

function show_alarm_details(alarm_id) {
    show_alarm_details(alarm_id)
}
let selected_alarm = null
let need_to_reload_alarms = false
function show_alarm_details(alarm_id, openModal = true) {
    if (alarm_id == null) return
    selected_alarm = alarm_id
    loading_section.classList.remove('hidden')
    console.log(get_event_detials_url.replace("999", alarm_id))
    new_fetch_helper(get_event_detials_url.replace("999", alarm_id)).then(res => {
        if ('error' in res) {
            loading_section.classList.add('hidden')
            console.log(res)
            toastr.error(res.error)
        } else {
            document.getElementById("alarm_details-id").textContent = res.id
            document.getElementById("alarm_details-device").textContent = res.device.title
            document.getElementById("alarm_details-devicename").textContent = res.device_name
            document.getElementById("alarm_details-type").textContent = res.alarm_type
            document.getElementById("alarm_details-channel").textContent = res.channel
            document.getElementById("alarm_details-alarmName").textContent = res.alarm_name
            document.getElementById("alarm_details-time").textContent = res.jTime
            document.getElementById("alarm_details-ip").textContent = res.ip
            document.getElementById("alarm_details-fileName").textContent = res.original_file_name

            if (res.file.file == null) {
                document.getElementById("alarm_details-image").classList.add("hidden")
                document.getElementById("alarm_details-image").src = ""
            } else {
                document.getElementById("alarm_details-image").classList.remove("hidden")
                document.getElementById("alarm_details-image").src = res.file.file

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

            document.getElementById("alarm_details-flags").innerHTML =
                `
                ${alarmSms}
                ${alarmEmail}
                ${alarmHandled}
                `
            document.getElementById("alarm_details-user").textContent = res.device.user.name
            document.getElementById("alarm_details-phone").textContent = res.device.user.phone
            document.getElementById("alarm_details-address").textContent = res.device.user.address

            if (openModal) {
                open_modal('event-details-modal')
            }

            loading_section.classList.add('hidden')
        }
    })
}


document.getElementById("select_date_modal_apply").addEventListener("click", ()=>{
    document.getElementById("start-time").value=start_time
    document.getElementById("end-time").value=end_time
})