function SweetConfirmDelete(url, method_type, formData) {
    //console.log('url', url)
    //console.log('type', method_type)
    //console.log('formData', formData)
    Swal.fire({
        title: "정말 삭제하시겠습니까?",
        text: "관련된 데이터가 모두 삭제됩니다.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#34c38f",
        cancelButtonColor: "#f46a6a",
        confirmButtonText: "삭제",
        cancelButtonText: "취소"
    }).then(function (result) {
        if (result.value) {
            $.ajax({
                url: url,
                type: method_type,
                data: formData,
                processData: false,
                contentType: false,
                success: function (res) {
                    Swal.fire({
                        title: "삭제완료.",
                        text: "요청하신 데이터의 삭제가 완료되었습니다.",
                        icon: "success"
                    }).then(function () {
                        location.reload();
                    });
                },
                error: function (xhr, status, error) {
                    alert("오류가 발생했습니다: " + xhr.responseJSON.error);
                }
            })
        }
    });

}

function SweetAlert_OK() {
    return Swal.fire({
        title: "OK",
        text: "요청하신 데이터가 등록되었습니다.",
        icon: "success"
    });
}

function SweetAlert_Error(message) {
    return Swal.fire({
        title: "Error",
        text: message,
        icon: "error"
    });
}

// 튜토리얼 메뉴 설정, 멤버 설정 리다이렉트 이벤트 변수
function initTutorialSettings() { // 초기화 함수
    if (localStorage.getItem('tutorial_menu_settings') === null) {
        localStorage.setItem('tutorial_menu_settings', 'false');
    }
    if (localStorage.getItem('tutorial_member_settings') === null) {
        localStorage.setItem('tutorial_member_settings', 'false');
    }
}

initTutorialSettings();
