// 前端交互逻辑
document.addEventListener('DOMContentLoaded', function() {
    // 自动关闭 alert
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(el) {
            bootstrap.Alert.getOrCreateInstance(el).close();
        });
    }, 5000);
});
